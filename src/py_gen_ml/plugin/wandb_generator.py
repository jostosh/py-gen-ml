"""Generator that emits Weights & Biases tracking helpers from protobuf messages."""
from __future__ import annotations

from typing import ClassVar, Optional

import protogen

from py_gen_ml.extensions_pb2 import (
    METRIC,
    METRIC_SET,
    PARAM,
    RUN_CONFIG,
    TAG,
    Wandb,
)
from py_gen_ml.logging.setup_logger import setup_logger
from py_gen_ml.plugin.common import get_extension_value, snake_case
from py_gen_ml.plugin.constants import WANDB_SUFFIX
from py_gen_ml.plugin.generator import Generator
from py_gen_ml.plugin.message_kind import (
    collect_message_closure,
    get_message_kind,
    ordered_messages,
)
from py_gen_ml.plugin.registry import GeneratorSpec
from py_gen_ml.plugin.schema_emit import emit_pydantic_model
from py_gen_ml.plugin.tracking import collect_slot_paths, format_paths_literal
from py_gen_ml.plugin.type_mapping import PythonTypeMapper, TypeMapper
from py_gen_ml.typing.some import some

logger = setup_logger(__name__)


class WandbGenerator(Generator):
    """Emit W&B adapters for messages with ``(pgml.wandb).enable``.

    ``RUN_CONFIG`` roots get ``init_*_run``; ``METRIC_SET`` roots get
    ``log_*``. Field slots come from ``(pgml.tracking_field)`` with kind-based
    defaults (PARAM / METRIC).
    """

    name: ClassVar[str] = 'wandb'
    output_suffix: ClassVar[Optional[str]] = WANDB_SUFFIX

    def __init__(
        self,
        gen: protogen.Plugin,
        suffix: Optional[str] = None,
        *,
        type_mapper: Optional[TypeMapper] = None,
    ) -> None:
        super().__init__(gen, type_mapper=type_mapper or PythonTypeMapper())
        self._suffix = suffix or WANDB_SUFFIX

    def _generate_code_for_file(self, file: protogen.File) -> None:
        roots = self._enabled_roots(file)
        if not roots:
            return

        messages = collect_message_closure(roots, file)
        g = self._new_python_file(
            file,
            self._suffix,
            emit_typing_import=True,
            emit_pgml_import=False,
        )
        g.P('import wandb')
        g.P('from pydantic import BaseModel, Field')
        g.P()
        g.P()

        self._emit_flatten_helper(g)

        for message in ordered_messages(file, messages):
            emit_pydantic_model(
                g,
                message,
                base_class='BaseModel',
                field_annotation=self._field_annotation,
                field_type=self._field_type,
                use_field_descriptions=True,
            )

        for root in sorted(roots, key=lambda m: m.proto.name):
            self._generate_root_helpers(g, root)

        self._run_yapf(g)

    @staticmethod
    def _enabled_roots(file: protogen.File) -> list[protogen.Message]:
        roots: list[protogen.Message] = []
        for message in file.messages:
            opts = get_extension_value(message, 'wandb', Wandb)
            if opts is not None and opts.enable:
                roots.append(message)
        return roots

    @staticmethod
    def _emit_flatten_helper(g: protogen.GeneratedFile) -> None:
        g.P(
            'def _wandb_flatten(obj: BaseModel, paths: typing.Sequence[typing.Tuple[str, str]]) -> typing.Dict[str, typing.Any]:',
        )
        g.set_indent(4)
        g.P('"""Map ``(attr_path, log_key)`` pairs on ``obj`` to a flat dict."""')
        g.P('out: typing.Dict[str, typing.Any] = {}')
        g.P('for attr_path, key in paths:')
        g.set_indent(8)
        g.P('cur: typing.Any = obj')
        g.P('for part in attr_path.split("."):')
        g.set_indent(12)
        g.P('cur = getattr(cur, part)')
        g.set_indent(8)
        g.P('if cur is None:')
        g.set_indent(12)
        g.P('continue')
        g.set_indent(8)
        g.P('out[key] = cur if isinstance(cur, (str, int, float, bool)) else str(cur)')
        g.set_indent(4)
        g.P('return out')
        g.set_indent(0)
        g.P()
        g.P()

    def _generate_root_helpers(
        self,
        g: protogen.GeneratedFile,
        root: protogen.Message,
    ) -> None:
        opts = some(get_extension_value(root, 'wandb', Wandb))
        kind = get_message_kind(root)
        class_name = root.proto.name
        helper = snake_case(class_name)

        if kind == RUN_CONFIG:
            self._emit_run_config_helpers(g, root, opts, class_name, helper)
        elif kind == METRIC_SET:
            self._emit_metric_set_helpers(g, root, class_name, helper)
        else:
            logger.warning(
                'Message %s has (pgml.wandb).enable but kind is not RUN_CONFIG '
                'or METRIC_SET; emitting flatten helpers only for PARAM/METRIC/TAG',
                class_name,
            )
            self._emit_generic_log_helpers(g, root, class_name, helper)

    def _emit_run_config_helpers(
        self,
        g: protogen.GeneratedFile,
        root: protogen.Message,
        opts: Wandb,
        class_name: str,
        helper: str,
    ) -> None:
        param_paths = collect_slot_paths(root, PARAM)
        tag_paths = collect_slot_paths(root, TAG)
        project = opts.project or ''
        run_name_field = opts.run_name_field or ''

        g.P(f'_{helper}_PARAM_PATHS: typing.List[typing.Tuple[str, str]] = {format_paths_literal(param_paths)}')
        g.P()
        g.P()
        g.P(f'_{helper}_TAG_PATHS: typing.List[typing.Tuple[str, str]] = {format_paths_literal(tag_paths)}')
        g.P()
        g.P()

        g.P(f'def {helper}_config(config: {class_name}) -> typing.Dict[str, typing.Any]:')
        g.set_indent(4)
        g.P(f'"""Flatten PARAM fields of ``{class_name}`` for ``wandb.init(config=...)``."""')
        g.P(f'return _wandb_flatten(config, _{helper}_PARAM_PATHS)')
        g.set_indent(0)
        g.P()
        g.P()

        g.P(
            f'def init_{helper}_run('
            f'config: {class_name}, *, '
            f'project: typing.Optional[str] = None, '
            f'name: typing.Optional[str] = None, '
            f'**kwargs: typing.Any'
            f') -> typing.Any:',
        )
        g.set_indent(4)
        g.P(f'"""Initialize a W&B run for ``{class_name}`` with config + tags."""')
        if project:
            g.P(f'proj = project if project is not None else {project!r}')
        else:
            g.P('proj = project')
        if run_name_field:
            g.P(f'run_name = name if name is not None else getattr(config, {run_name_field!r}, None)')
        else:
            g.P('run_name = name')
        g.P(f'tags = [str(v) for v in _wandb_flatten(config, _{helper}_TAG_PATHS).values()]')
        g.P(
            f'return wandb.init('
            f'project=proj, '
            f'name=run_name, '
            f'config={helper}_config(config), '
            f'tags=tags or None, '
            f'**kwargs'
            f')',
        )
        g.set_indent(0)
        g.P()
        g.P()

    def _emit_metric_set_helpers(
        self,
        g: protogen.GeneratedFile,
        root: protogen.Message,
        class_name: str,
        helper: str,
    ) -> None:
        metric_paths = collect_slot_paths(root, METRIC)
        g.P(f'_{helper}_METRIC_PATHS: typing.List[typing.Tuple[str, str]] = {format_paths_literal(metric_paths)}')
        g.P()
        g.P()

        g.P(f'def {helper}_dict(metrics: {class_name}) -> typing.Dict[str, typing.Any]:')
        g.set_indent(4)
        g.P(f'"""Flatten METRIC fields of ``{class_name}`` for ``wandb.log``."""')
        g.P(f'return _wandb_flatten(metrics, _{helper}_METRIC_PATHS)')
        g.set_indent(0)
        g.P()
        g.P()

        g.P(
            f'def log_{helper}('
            f'metrics: {class_name}, *, step: typing.Optional[int] = None'
            f') -> None:',
        )
        g.set_indent(4)
        g.P(f'"""Log ``{class_name}`` metrics via ``wandb.log``."""')
        g.P(f'payload = {helper}_dict(metrics)')
        g.P('if step is not None:')
        g.set_indent(8)
        g.P('wandb.log(payload, step=step)')
        g.set_indent(4)
        g.P('else:')
        g.set_indent(8)
        g.P('wandb.log(payload)')
        g.set_indent(0)
        g.P()
        g.P()

    def _emit_generic_log_helpers(
        self,
        g: protogen.GeneratedFile,
        root: protogen.Message,
        class_name: str,
        helper: str,
    ) -> None:
        param_paths = collect_slot_paths(root, PARAM)
        metric_paths = collect_slot_paths(root, METRIC)
        g.P(f'_{helper}_PARAM_PATHS: typing.List[typing.Tuple[str, str]] = {format_paths_literal(param_paths)}')
        g.P()
        g.P()
        g.P(f'_{helper}_METRIC_PATHS: typing.List[typing.Tuple[str, str]] = {format_paths_literal(metric_paths)}')
        g.P()
        g.P()
        g.P(f'def {helper}_config(obj: {class_name}) -> typing.Dict[str, typing.Any]:')
        g.set_indent(4)
        g.P(f'return _wandb_flatten(obj, _{helper}_PARAM_PATHS)')
        g.set_indent(0)
        g.P()
        g.P()
        g.P(f'def log_{helper}(obj: {class_name}, *, step: typing.Optional[int] = None) -> None:')
        g.set_indent(4)
        g.P(f'payload = _wandb_flatten(obj, _{helper}_METRIC_PATHS)')
        g.P('wandb.log(payload, step=step) if step is not None else wandb.log(payload)')
        g.set_indent(0)
        g.P()
        g.P()

    def _field_annotation(self, field: protogen.Field) -> str:
        annotation = self._field_type(field)
        if field.is_list():
            annotation = f'typing.List[{annotation}]'
        if field.proto.proto3_optional:
            annotation = f'typing.Optional[{annotation}]'
        return annotation

    def _field_type(self, field: protogen.Field) -> str:
        if field.kind == protogen.Kind.ENUM:
            return 'str'
        assert self._type_mapper is not None
        return self._type_mapper.field_to_type(field)


wandb_spec = GeneratorSpec(
    name='wandb',
    factory=lambda plugin: WandbGenerator(plugin),
    enabled_by_default=False,
    description='Weights & Biases init/config/metric helpers for (pgml.wandb) messages.',
)
