"""Generator that emits ``lancedb.pydantic.LanceModel`` schemas from protobufs."""
from __future__ import annotations

from typing import ClassVar, Optional

import protogen

from py_gen_ml.extensions_pb2 import LanceDB, LanceDBField
from py_gen_ml.logging.setup_logger import setup_logger
from py_gen_ml.plugin.common import get_extension_value, snake_case
from py_gen_ml.plugin.constants import LANCEDB_SUFFIX
from py_gen_ml.plugin.generator import Generator
from py_gen_ml.plugin.message_kind import (
    collect_message_closure,
    ordered_messages,
)
from py_gen_ml.plugin.registry import GeneratorSpec
from py_gen_ml.plugin.schema_emit import emit_pydantic_model
from py_gen_ml.plugin.type_mapping import PythonTypeMapper, TypeMapper
from py_gen_ml.typing.some import some

logger = setup_logger(__name__)


class LanceDBGenerator(Generator):
    """Emit LanceModel classes for messages opted in via ``(pgml.lancedb)``.

    Only messages with ``(pgml.lancedb).enable = true`` and nested message types
    reachable from those roots are generated. Torch Dataset wrappers are not
    emitted: pass the LanceDB table to ``torch.utils.data.DataLoader`` directly.
    """

    name: ClassVar[str] = 'lancedb'
    output_suffix: ClassVar[Optional[str]] = LANCEDB_SUFFIX

    def __init__(
        self,
        gen: protogen.Plugin,
        suffix: Optional[str] = None,
        *,
        type_mapper: Optional[TypeMapper] = None,
    ) -> None:
        super().__init__(gen, type_mapper=type_mapper or PythonTypeMapper())
        self._suffix = suffix or LANCEDB_SUFFIX

    def _generate_code_for_file(self, file: protogen.File) -> None:
        roots = self._enabled_roots(file)
        if not roots:
            return

        messages = collect_message_closure(roots, file)
        if not messages:
            return

        g = self._new_python_file(
            file,
            self._suffix,
            emit_typing_import=True,
            emit_pgml_import=False,
        )
        g.P('from lancedb.db import DBConnection')
        g.P('from lancedb.pydantic import LanceModel, Vector')
        g.P('from lancedb.table import LanceTable')
        g.P()
        g.P()

        for message in ordered_messages(file, messages):
            emit_pydantic_model(
                g,
                message,
                base_class='LanceModel',
                field_annotation=self._field_annotation,
                field_type=self._field_type,
            )

        for root in sorted(roots, key=lambda m: m.proto.name):
            self._generate_root_helpers(g, root)

        self._run_yapf(g)

    @staticmethod
    def _enabled_roots(file: protogen.File) -> list[protogen.Message]:
        roots: list[protogen.Message] = []
        for message in file.messages:
            lancedb = get_extension_value(message, 'lancedb', LanceDB)
            if lancedb is not None and lancedb.enable:
                roots.append(message)
        return roots

    def _generate_root_helpers(
        self,
        g: protogen.GeneratedFile,
        root: protogen.Message,
    ) -> None:
        lancedb = some(get_extension_value(root, 'lancedb', LanceDB))
        table_name = lancedb.table_name or snake_case(root.proto.name)
        class_name = root.proto.name
        helper = snake_case(root.proto.name)
        merge_on = self._merge_on_fields(root)

        g.P(f'def {helper}_table_name() -> str:')
        g.set_indent(4)
        g.P(f'"""Default LanceDB table name for :class:`{class_name}`."""')
        g.P(f"return '{table_name}'")
        g.set_indent(0)
        g.P()
        g.P()

        g.P(f'def {helper}_merge_on() -> typing.List[str]:')
        g.set_indent(4)
        g.P(
            f'"""Join columns for ``merge_insert`` / ``merge_rows`` '
            f'(fields with ``(pgml.lancedb_field).merge_key``)."""',
        )
        g.P(f'return {merge_on!r}')
        g.set_indent(0)
        g.P()
        g.P()

        g.P(
            f'def create_{helper}_table('
            f'db: DBConnection, *, name: typing.Optional[str] = None, '
            f'exist_ok: bool = True, **kwargs: typing.Any'
            f') -> LanceTable:',
        )
        g.set_indent(4)
        g.P(f'"""Create a LanceDB table whose schema is :class:`{class_name}`.')
        g.P()
        g.P('``db`` is a connection from ``lancedb.connect(...)``.')
        g.P('By default ``exist_ok=True`` opens the table if it already exists.')
        g.P('Pass ``mode=\"overwrite\"`` (via kwargs) to replace an existing table.')
        g.P('Load rows for training via Arrow (``table.to_arrow()``) or LanceDB\'s')
        g.P('``Permutation`` streaming API, then hand tensors to')
        g.P('``torch.utils.data.DataLoader`` as needed.')
        g.P('"""')
        g.P(
            f'return db.create_table('
            f'name or {helper}_table_name(), schema={class_name}, '
            f'exist_ok=exist_ok, **kwargs)',
        )
        g.set_indent(0)
        g.P()
        g.P()

    def _field_annotation(self, field: protogen.Field) -> str:
        vector_dim = self._vector_dim(field)
        if vector_dim is not None:
            annotation = f'Vector({vector_dim})'
        else:
            annotation = self._field_type(field)
            if field.is_list():
                annotation = f'typing.List[{annotation}]'

        if field.proto.proto3_optional:
            annotation = f'typing.Optional[{annotation}]'
        return annotation

    def _field_type(self, field: protogen.Field) -> str:
        if field.kind == protogen.Kind.ENUM:
            # LanceDB Arrow conversion has no native enum; store as string.
            return 'str'
        assert self._type_mapper is not None
        return self._type_mapper.field_to_type(field)

    @staticmethod
    def _vector_dim(field: protogen.Field) -> Optional[int]:
        opts = get_extension_value(field, 'lancedb_field', LanceDBField)
        if opts is None or opts.vector_dim == 0:
            return None
        return int(opts.vector_dim)

    @staticmethod
    def _merge_on_fields(message: protogen.Message) -> list[str]:
        keys: list[str] = []
        for field in message.fields:
            if field.oneof and len(field.oneof.fields) > 1:
                continue
            opts = get_extension_value(field, 'lancedb_field', LanceDBField)
            if opts is not None and opts.merge_key:
                keys.append(field.py_name)
        return keys


lancedb_spec = GeneratorSpec(
    name='lancedb',
    factory=lambda plugin: LanceDBGenerator(plugin),
    enabled_by_default=False,
    description='LanceDB LanceModel schemas for messages with (pgml.lancedb).enable.',
)
