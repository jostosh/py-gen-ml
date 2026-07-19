"""Generator that emits MLflow tracking helpers from protobuf messages."""
from __future__ import annotations

from typing import ClassVar, Optional

import protogen

from py_gen_ml.extensions_pb2 import (
    METRIC,
    METRIC_SET,
    PARAM,
    RUN_CONFIG,
    TAG,
    MLflow,
)
from py_gen_ml.logging.setup_logger import setup_logger
from py_gen_ml.plugin.common import get_extension_value, snake_case
from py_gen_ml.plugin.constants import MLFLOW_SUFFIX
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

# Maps protogen field kinds to ``mlflow.types.schema.DataType`` attribute names.
_MLFLOW_DATA_TYPE: dict[protogen.Kind, str] = {
    protogen.Kind.DOUBLE: 'double',
    protogen.Kind.FLOAT: 'float',
    protogen.Kind.INT64: 'long',
    protogen.Kind.UINT64: 'long',
    protogen.Kind.INT32: 'integer',
    protogen.Kind.FIXED64: 'long',
    protogen.Kind.FIXED32: 'integer',
    protogen.Kind.BOOL: 'boolean',
    protogen.Kind.STRING: 'string',
    protogen.Kind.BYTES: 'binary',
    protogen.Kind.UINT32: 'integer',
    protogen.Kind.ENUM: 'string',
    protogen.Kind.SFIXED32: 'integer',
    protogen.Kind.SFIXED64: 'long',
    protogen.Kind.SINT32: 'integer',
    protogen.Kind.SINT64: 'long',
}


class MLflowGenerator(Generator):
    """Emit MLflow adapters for messages with ``(pgml.mlflow).enable``.

    ``RUN_CONFIG`` roots get ``start_*_run`` / ``log_*_params``; ``METRIC_SET``
    roots get ``log_*_metrics``. When ``registered_model_name`` is set, emit
    Model Registry helpers (signature / register / resolve). Field slots come
    from ``(pgml.tracking_field)`` with kind-based defaults (PARAM / METRIC).
    """

    name: ClassVar[str] = 'mlflow'
    output_suffix: ClassVar[Optional[str]] = MLFLOW_SUFFIX

    def __init__(
        self,
        gen: protogen.Plugin,
        suffix: Optional[str] = None,
        *,
        type_mapper: Optional[TypeMapper] = None,
    ) -> None:
        super().__init__(gen, type_mapper=type_mapper or PythonTypeMapper())
        self._suffix = suffix or MLFLOW_SUFFIX

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
        g.P('import contextlib')
        g.P('import mlflow')
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
            self._generate_root_helpers(g, root, file)

        self._run_yapf(g)

    @staticmethod
    def _enabled_roots(file: protogen.File) -> list[protogen.Message]:
        roots: list[protogen.Message] = []
        for message in file.messages:
            opts = get_extension_value(message, 'mlflow', MLflow)
            if opts is not None and opts.enable:
                roots.append(message)
        return roots

    @staticmethod
    def _emit_flatten_helper(g: protogen.GeneratedFile) -> None:
        g.P(
            'def _mlflow_flatten(obj: BaseModel, paths: typing.Sequence[typing.Tuple[str, str]]) -> typing.Dict[str, typing.Any]:',
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
        file: protogen.File,
    ) -> None:
        opts = some(get_extension_value(root, 'mlflow', MLflow))
        kind = get_message_kind(root)
        class_name = root.proto.name
        helper = snake_case(class_name)

        if opts.registered_model_name:
            self._emit_registry_helpers(g, root, opts, file, helper)

        if kind == RUN_CONFIG:
            self._emit_run_config_helpers(g, root, opts, class_name, helper)
        elif kind == METRIC_SET:
            self._emit_metric_set_helpers(g, root, class_name, helper)
        elif not opts.registered_model_name:
            logger.warning(
                'Message %s has (pgml.mlflow).enable but kind is not RUN_CONFIG '
                'or METRIC_SET and registered_model_name is unset; emitting '
                'flatten helpers only for PARAM/METRIC/TAG',
                class_name,
            )
            self._emit_generic_log_helpers(g, root, class_name, helper)

    def _emit_registry_helpers(
        self,
        g: protogen.GeneratedFile,
        root: protogen.Message,
        opts: MLflow,
        file: protogen.File,
        helper: str,
    ) -> None:
        registered_name = opts.registered_model_name
        const_name = f'{helper.upper()}_REGISTERED_NAME'
        g.P(f'{const_name} = {registered_name!r}')
        g.P()
        g.P()

        input_cols = self._col_specs_literal(file, opts.signature_input, root.proto.name, 'signature_input')
        output_cols = self._col_specs_literal(file, opts.signature_output, root.proto.name, 'signature_output')

        g.P(f'def {helper}_signature() -> typing.Any:')
        g.set_indent(4)
        g.P(f'"""Build an MLflow ``ModelSignature`` for ``{root.proto.name}``."""')
        g.P('from mlflow.models.signature import ModelSignature')
        g.P('from mlflow.types.schema import Array, ColSpec, DataType, Schema')
        g.P()
        g.P('return ModelSignature(')
        g.set_indent(8)
        g.P(f'inputs=Schema({input_cols}),')
        g.P(f'outputs=Schema({output_cols}),')
        g.set_indent(4)
        g.P(')')
        g.set_indent(0)
        g.P()
        g.P()

        g.P(
            f'def register_{helper}('
            f'model_uri: str, *, '
            f'name: typing.Optional[str] = None, '
            f'await_registration_for: int = 300'
            f') -> typing.Any:',
        )
        g.set_indent(4)
        g.P(
            f'"""Register ``model_uri`` as ``{registered_name}`` (or ``name``) '
            f'in the MLflow Model Registry."""',
        )
        g.P(f'model_name = name if name is not None else {const_name}')
        g.P(
            'return mlflow.register_model('
            'model_uri, model_name, await_registration_for=await_registration_for)',
        )
        g.set_indent(0)
        g.P()
        g.P()

        g.P(
            f'def resolve_{helper}_uri('
            f'*, '
            f'name: typing.Optional[str] = None, '
            f'stage: typing.Optional[str] = None, '
            f'version: typing.Optional[str] = None, '
            f'alias: typing.Optional[str] = None'
            f') -> str:',
        )
        g.set_indent(4)
        g.P(
            f'"""Build a ``models:/...`` URI for the ``{registered_name}`` registry entry."""',
        )
        g.P(f'model_name = name if name is not None else {const_name}')
        g.P('if alias is not None:')
        g.set_indent(8)
        g.P('return f"models:/{model_name}@{alias}"')
        g.set_indent(4)
        g.P('if version is not None:')
        g.set_indent(8)
        g.P('return f"models:/{model_name}/{version}"')
        g.set_indent(4)
        g.P('if stage is not None:')
        g.set_indent(8)
        g.P('return f"models:/{model_name}/{stage}"')
        g.set_indent(4)
        g.P('return f"models:/{model_name}/latest"')
        g.set_indent(0)
        g.P()
        g.P()

    def _col_specs_literal(
        self,
        file: protogen.File,
        message_name: str,
        root_name: str,
        option_name: str,
    ) -> str:
        if not message_name:
            logger.warning(
                'Message %s has registered_model_name but empty %s; '
                'emitting an empty Schema',
                root_name,
                option_name,
            )
            return '[]'

        message = self._find_message(file, message_name)
        if message is None:
            raise ValueError(
                f'(pgml.mlflow).{option_name}={message_name!r} on {root_name} '
                f'was not found in {file.proto.name}',
            )

        specs: list[str] = []
        for field in message.fields:
            if field.kind == protogen.Kind.MESSAGE:
                logger.warning(
                    'Skipping nested message field %s.%s in MLflow signature '
                    '(scalars / repeated scalars only)',
                    message_name,
                    field.proto.name,
                )
                continue
            type_attr = _MLFLOW_DATA_TYPE.get(field.kind)
            if type_attr is None:
                logger.warning(
                    'Skipping unsupported field kind %s on %s.%s for MLflow signature',
                    field.kind,
                    message_name,
                    field.proto.name,
                )
                continue
            dtype = f'DataType.{type_attr}'
            if field.is_list():
                dtype = f'Array({dtype})'
            specs.append(f'ColSpec({dtype}, {field.proto.name!r})')
        return '[' + ', '.join(specs) + ']'

    @staticmethod
    def _find_message(file: protogen.File, name: str) -> Optional[protogen.Message]:
        for message in file.messages:
            if message.proto.name == name:
                return message
        return None

    def _emit_run_config_helpers(
        self,
        g: protogen.GeneratedFile,
        root: protogen.Message,
        opts: MLflow,
        class_name: str,
        helper: str,
    ) -> None:
        param_paths = collect_slot_paths(root, PARAM)
        tag_paths = collect_slot_paths(root, TAG)
        experiment = opts.experiment_name or ''
        run_name_field = opts.run_name_field or ''

        g.P(f'_{helper}_PARAM_PATHS: typing.List[typing.Tuple[str, str]] = {format_paths_literal(param_paths)}')
        g.P()
        g.P()
        g.P(f'_{helper}_TAG_PATHS: typing.List[typing.Tuple[str, str]] = {format_paths_literal(tag_paths)}')
        g.P()
        g.P()

        g.P(f'def {helper}_params(config: {class_name}) -> typing.Dict[str, typing.Any]:')
        g.set_indent(4)
        g.P(f'"""Flatten PARAM (+ TAG as string params) fields of ``{class_name}`` for MLflow."""')
        g.P(f'params = _mlflow_flatten(config, _{helper}_PARAM_PATHS)')
        g.P(f'tags = _mlflow_flatten(config, _{helper}_TAG_PATHS)')
        g.P('params.update({f"tag.{k}": v for k, v in tags.items()})')
        g.P('return params')
        g.set_indent(0)
        g.P()
        g.P()

        g.P(f'def log_{helper}_params(config: {class_name}) -> None:')
        g.set_indent(4)
        g.P(f'"""Log ``{class_name}`` PARAM/TAG fields via ``mlflow.log_params``."""')
        g.P(f'mlflow.log_params({helper}_params(config))')
        g.set_indent(0)
        g.P()
        g.P()

        g.P('@contextlib.contextmanager')
        g.P(
            f'def start_{helper}_run('
            f'config: {class_name}, *, '
            f'experiment_name: typing.Optional[str] = None, '
            f'run_name: typing.Optional[str] = None'
            f') -> typing.Iterator[typing.Any]:',
        )
        g.set_indent(4)
        g.P(f'"""Start an MLflow run for ``{class_name}``, logging params on enter."""')
        if experiment:
            g.P(f'exp = experiment_name if experiment_name is not None else {experiment!r}')
        else:
            g.P('exp = experiment_name')
        g.P('if exp:')
        g.set_indent(8)
        g.P('mlflow.set_experiment(exp)')
        g.set_indent(4)
        if run_name_field:
            g.P(f'name = run_name if run_name is not None else getattr(config, {run_name_field!r}, None)')
        else:
            g.P('name = run_name')
        g.P('with mlflow.start_run(run_name=name) as run:')
        g.set_indent(8)
        g.P(f'log_{helper}_params(config)')
        g.P(f'for key, value in _mlflow_flatten(config, _{helper}_TAG_PATHS).items():')
        g.set_indent(12)
        g.P('mlflow.set_tag(key, value)')
        g.set_indent(8)
        g.P('yield run')
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

        g.P(f'def {helper}_metrics(metrics: {class_name}) -> typing.Dict[str, float]:')
        g.set_indent(4)
        g.P(f'"""Flatten METRIC fields of ``{class_name}`` to floats for MLflow."""')
        g.P(f'raw = _mlflow_flatten(metrics, _{helper}_METRIC_PATHS)')
        g.P('return {k: float(v) for k, v in raw.items()}')
        g.set_indent(0)
        g.P()
        g.P()

        g.P(
            f'def log_{helper}('
            f'metrics: {class_name}, *, step: typing.Optional[int] = None'
            f') -> None:',
        )
        g.set_indent(4)
        g.P(f'"""Log ``{class_name}`` metrics via ``mlflow.log_metrics``."""')
        g.P(f'mlflow.log_metrics({helper}_metrics(metrics), step=step)')
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
        g.P(f'def log_{helper}_params(obj: {class_name}) -> None:')
        g.set_indent(4)
        g.P(f'mlflow.log_params(_mlflow_flatten(obj, _{helper}_PARAM_PATHS))')
        g.set_indent(0)
        g.P()
        g.P()
        g.P(f'def log_{helper}_metrics(obj: {class_name}, *, step: typing.Optional[int] = None) -> None:')
        g.set_indent(4)
        g.P(f'raw = _mlflow_flatten(obj, _{helper}_METRIC_PATHS)')
        g.P('mlflow.log_metrics({k: float(v) for k, v in raw.items()}, step=step)')
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


mlflow_spec = GeneratorSpec(
    name='mlflow',
    factory=lambda plugin: MLflowGenerator(plugin),
    enabled_by_default=False,
    description='MLflow run/param/metric/registry helpers for (pgml.mlflow) messages.',
)
