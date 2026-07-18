"""Generator that emits Argilla Settings and record helpers from protobufs."""
from __future__ import annotations

from typing import ClassVar, Optional

import protogen

from py_gen_ml.extensions_pb2 import (
    FIELD,
    METADATA,
    QUESTION,
    Argilla,
    ArgillaField,
    MapperConfig,
    MapperField,
)
from py_gen_ml.logging.setup_logger import setup_logger
from py_gen_ml.plugin.common import get_extension_value, snake_case
from py_gen_ml.plugin.constants import ARGILLA_SUFFIX
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


class ArgillaGenerator(Generator):
    """Emit Argilla adapters for messages with ``(pgml.argilla).enable``.

    Fields must declare ``(pgml.argilla_field).slot`` as FIELD, QUESTION, or
    METADATA. Emits Settings builders and record to/from mappers.
    """

    name: ClassVar[str] = 'argilla'
    output_suffix: ClassVar[Optional[str]] = ARGILLA_SUFFIX

    def __init__(
        self,
        gen: protogen.Plugin,
        suffix: Optional[str] = None,
        *,
        type_mapper: Optional[TypeMapper] = None,
    ) -> None:
        super().__init__(gen, type_mapper=type_mapper or PythonTypeMapper())
        self._suffix = suffix or ARGILLA_SUFFIX

    def _generate_code_for_file(self, file: protogen.File) -> None:
        roots = self._enabled_roots(file)
        if not roots:
            return

        for root in roots:
            self._assert_slots(root)

        messages = collect_message_closure(roots, file)
        g = self._new_python_file(
            file,
            self._suffix,
            emit_typing_import=True,
            emit_pgml_import=False,
        )
        g.P('import argilla as rg')
        g.P('from pydantic import BaseModel, Field')
        g.P()
        g.P()

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
            opts = get_extension_value(message, 'argilla', Argilla)
            if opts is not None and opts.enable:
                roots.append(message)
        return roots

    def _assert_slots(self, message: protogen.Message) -> None:
        for field in message.fields:
            if field.oneof and len(field.oneof.fields) > 1:
                continue
            opts = get_extension_value(field, 'argilla_field', ArgillaField)
            if opts is None or opts.slot == 0:
                raise ValueError(
                    f'Argilla-enabled message {message.proto.name} field '
                    f'{field.py_name} must set (pgml.argilla_field).slot to '
                    f'FIELD, QUESTION, or METADATA',
                )

    def _field_slot_info(
        self,
        field: protogen.Field,
    ) -> tuple[int, str, ArgillaField]:
        opts = some(get_extension_value(field, 'argilla_field', ArgillaField))
        name = opts.name or field.py_name
        return opts.slot, name, opts

    def _mapper_alias(self, field: protogen.Field) -> str:
        mapper = get_extension_value(field, 'mapper_field', MapperField)
        if mapper is not None and mapper.alias:
            return mapper.alias
        opts = get_extension_value(field, 'argilla_field', ArgillaField)
        if opts is not None and opts.name:
            return opts.name
        return field.py_name

    def _generate_root_helpers(
        self,
        g: protogen.GeneratedFile,
        root: protogen.Message,
    ) -> None:
        argilla_opts = some(get_extension_value(root, 'argilla', Argilla))
        class_name = root.proto.name
        helper = snake_case(class_name)
        dataset_name = argilla_opts.dataset_name or helper

        fields: list[tuple[protogen.Field, str, ArgillaField]] = []
        questions: list[tuple[protogen.Field, str, ArgillaField]] = []
        metadata: list[tuple[protogen.Field, str]] = []
        for field in root.fields:
            if field.oneof and len(field.oneof.fields) > 1:
                continue
            slot, name, opts = self._field_slot_info(field)
            if slot == FIELD:
                fields.append((field, name, opts))
            elif slot == QUESTION:
                questions.append((field, name, opts))
            elif slot == METADATA:
                metadata.append((field, name))

        g.P(f'def {helper}_dataset_name() -> str:')
        g.set_indent(4)
        g.P(f'return {dataset_name!r}')
        g.set_indent(0)
        g.P()
        g.P()

        g.P(
            f'def build_{helper}_settings('
            f'*, client: typing.Optional[rg.Argilla] = None'
            f') -> rg.Settings:',
        )
        g.set_indent(4)
        g.P(f'"""Build Argilla ``Settings`` for ``{class_name}`` (FIELD + QUESTION only).')
        g.P()
        g.P('Pass ``client=`` to avoid requiring a default Argilla API key at construction time.')
        g.P('"""')
        g.P('settings_fields: typing.List[typing.Any] = []')
        for field, name, opts in fields:
            field_type = (opts.field_type or 'text').lower()
            required = bool(opts.required)
            if field_type == 'chat':
                g.P(
                    f'settings_fields.append(rg.ChatField(name={name!r}, required={required}, client=client))',
                )
            elif field_type == 'image':
                g.P(
                    f'settings_fields.append(rg.ImageField(name={name!r}, required={required}, client=client))',
                )
            else:
                g.P(
                    f'settings_fields.append(rg.TextField(name={name!r}, required={required}, client=client))',
                )
        g.P('settings_questions: typing.List[typing.Any] = []')
        for field, name, opts in questions:
            qtype = (opts.question_type or 'text').lower()
            required = bool(opts.required)
            labels = list(opts.labels)
            if qtype in ('label', 'label_selection'):
                g.P(
                    f'settings_questions.append(rg.LabelQuestion(name={name!r}, labels={labels!r}, required={required}, client=client))',
                )
            elif qtype in ('multi_label', 'multi_label_selection'):
                g.P(
                    f'settings_questions.append(rg.MultiLabelQuestion(name={name!r}, labels={labels!r}, required={required}, client=client))',
                )
            elif qtype == 'rating':
                g.P(
                    f'settings_questions.append(rg.RatingQuestion(name={name!r}, values=[1, 2, 3, 4, 5], required={required}, client=client))',
                )
            else:
                g.P(
                    f'settings_questions.append(rg.TextQuestion(name={name!r}, required={required}, client=client))',
                )
        g.P('return rg.Settings(fields=settings_fields, questions=settings_questions)')
        g.set_indent(0)
        g.P()
        g.P()

        g.P(f'def to_{helper}_record(row: {class_name}) -> rg.Record:')
        g.set_indent(4)
        g.P(f'"""Map ``{class_name}`` to an Argilla ``Record`` by slot."""')
        g.P('record_fields: typing.Dict[str, typing.Any] = {}')
        for field, name, _opts in fields:
            g.P(f'record_fields[{name!r}] = getattr(row, {field.py_name!r})')
        g.P('record_metadata: typing.Dict[str, typing.Any] = {}')
        for field, name in metadata:
            g.P(f'record_metadata[{name!r}] = getattr(row, {field.py_name!r})')
        # Questions as suggestions when present on the same message
        if questions:
            g.P('suggestions: typing.List[typing.Any] = []')
            for field, name, opts in questions:
                g.P(f'_qval = getattr(row, {field.py_name!r}, None)')
                g.P('if _qval is not None:')
                g.set_indent(8)
                g.P(f'suggestions.append(rg.Suggestion(question_name={name!r}, value=_qval))')
                g.set_indent(4)
            g.P('return rg.Record(fields=record_fields, metadata=record_metadata or None, suggestions=suggestions or None)')
        else:
            g.P('return rg.Record(fields=record_fields, metadata=record_metadata or None)')
        g.set_indent(0)
        g.P()
        g.P()

        g.P(f'def from_{helper}_record(record: rg.Record) -> {class_name}:')
        g.set_indent(4)
        g.P(f'"""Map an Argilla ``Record`` back to ``{class_name}``."""')
        g.P('data: typing.Dict[str, typing.Any] = {}')
        for field, name, _opts in fields:
            g.P(f'data[{field.py_name!r}] = record.fields.get({name!r})')
        for field, name in metadata:
            g.P(f'data[{field.py_name!r}] = (record.metadata or {{}}).get({name!r})')
        for field, name, _opts in questions:
            g.P(f'# Question {name} may live in responses/suggestions; best-effort')
            g.P(f'data[{field.py_name!r}] = None')
            g.P('for _s in (record.suggestions or []):')
            g.set_indent(8)
            g.P(f'if getattr(_s, "question_name", None) == {name!r}:')
            g.set_indent(12)
            g.P(f'data[{field.py_name!r}] = getattr(_s, "value", None)')
            g.P('break')
            g.set_indent(4)
        g.P(f'return {class_name}.model_validate(data)')
        g.set_indent(0)
        g.P()
        g.P()

        # Mapper aliases when mapper_config enabled
        mapper_cfg = get_extension_value(root, 'mapper_config', MapperConfig)
        if mapper_cfg is not None and mapper_cfg.enable:
            g.P(f'{helper.upper()}_ALIASES: typing.Dict[str, str] = {{')
            g.set_indent(4)
            for field in root.fields:
                if field.oneof and len(field.oneof.fields) > 1:
                    continue
                alias = self._mapper_alias(field)
                g.P(f'{field.py_name!r}: {alias!r},')
            g.set_indent(0)
            g.P('}')
            g.P()
            g.P()
            g.P(f'def {helper}_to_row_dict(row: {class_name}) -> typing.Dict[str, typing.Any]:')
            g.set_indent(4)
            g.P(f'return {{{helper.upper()}_ALIASES[k]: v for k, v in row.model_dump().items() if k in {helper.upper()}_ALIASES}}')
            g.set_indent(0)
            g.P()
            g.P()
            g.P(f'def {helper}_from_row_dict(data: typing.Dict[str, typing.Any]) -> {class_name}:')
            g.set_indent(4)
            g.P(f'inv = {{v: k for k, v in {helper.upper()}_ALIASES.items()}}')
            g.P('mapped = {inv[k]: v for k, v in data.items() if k in inv}')
            g.P(f'return {class_name}.model_validate(mapped)')
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


argilla_spec = GeneratorSpec(
    name='argilla',
    factory=lambda plugin: ArgillaGenerator(plugin),
    enabled_by_default=False,
    description='Argilla Settings and record helpers for (pgml.argilla) messages.',
)
