"""Generator that emits PydanticAI synthesis helpers from protobuf messages."""
from __future__ import annotations

from typing import ClassVar, Optional

import protogen

from py_gen_ml.extensions_pb2 import PydanticAI
from py_gen_ml.logging.setup_logger import setup_logger
from py_gen_ml.plugin.common import get_extension_value, snake_case
from py_gen_ml.plugin.constants import PYDANTIC_AI_SUFFIX
from py_gen_ml.plugin.generator import Generator
from py_gen_ml.plugin.message_kind import (
    collect_message_closure,
    ordered_messages,
)
from py_gen_ml.plugin.registry import GeneratorSpec
from py_gen_ml.plugin.schema_emit import (
    emit_pydantic_model,
    field_leading_comment,
    message_leading_comment,
)
from py_gen_ml.plugin.type_mapping import PythonTypeMapper, TypeMapper
from py_gen_ml.typing.some import some

logger = setup_logger(__name__)


class PydanticAIGenerator(Generator):
    """Emit PydanticAI synthesis adapters for ``(pgml.pydantic_ai).enable``.

    Generates full + Partial Pydantic models (with ``Field(description=...)`` from
    proto comments), agent factory using ``NativeOutput``, and ``synthesize_*``
    helpers (Path A full generation / Path B gap ``create_model`` completion).
    """

    name: ClassVar[str] = 'pydantic_ai'
    output_suffix: ClassVar[Optional[str]] = PYDANTIC_AI_SUFFIX

    def __init__(
        self,
        gen: protogen.Plugin,
        suffix: Optional[str] = None,
        *,
        type_mapper: Optional[TypeMapper] = None,
    ) -> None:
        super().__init__(gen, type_mapper=type_mapper or PythonTypeMapper())
        self._suffix = suffix or PYDANTIC_AI_SUFFIX

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
        g.P('import json')
        g.P('from pydantic import BaseModel, Field, create_model')
        g.P('from pydantic_ai import Agent')
        g.P('from pydantic_ai.models import Model')
        g.P('from pydantic_ai.output import NativeOutput')
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
            emit_pydantic_model(
                g,
                message,
                base_class='BaseModel',
                field_annotation=self._field_annotation,
                field_type=self._field_type,
                class_name=f'{message.proto.name}Partial',
                use_field_descriptions=True,
                all_optional=True,
            )

        for root in sorted(roots, key=lambda m: m.proto.name):
            self._generate_synthesis_helpers(g, root, file)

        self._run_yapf(g)

    @staticmethod
    def _enabled_roots(file: protogen.File) -> list[protogen.Message]:
        roots: list[protogen.Message] = []
        for message in file.messages:
            opts = get_extension_value(message, 'pydantic_ai', PydanticAI)
            if opts is not None and opts.enable:
                roots.append(message)
        return roots

    def _resolve_response_message(
        self,
        root: protogen.Message,
        file: protogen.File,
    ) -> protogen.Message:
        opts = some(get_extension_value(root, 'pydantic_ai', PydanticAI))
        if not opts.response_message:
            return root
        for message in file.messages:
            if message.proto.name == opts.response_message:
                return message
        raise ValueError(
            f'pydantic_ai.response_message={opts.response_message!r} not found '
            f'in {file.proto.name} (from {root.proto.name})',
        )

    def _generate_synthesis_helpers(
        self,
        g: protogen.GeneratedFile,
        root: protogen.Message,
        file: protogen.File,
    ) -> None:
        opts = some(get_extension_value(root, 'pydantic_ai', PydanticAI))
        response = self._resolve_response_message(root, file)
        full_name = response.proto.name
        partial_name = f'{full_name}Partial'
        helper = snake_case(full_name)
        agent_name = opts.agent_name or full_name
        message_description = message_leading_comment(response)

        # Field description map for gap models
        g.P(f'_{helper}_FIELD_DESCRIPTIONS: typing.Dict[str, str] = {{')
        g.set_indent(4)
        for field in response.fields:
            if field.oneof and len(field.oneof.fields) > 1:
                continue
            comment = field_leading_comment(field)
            if comment:
                g.P(f'{field.py_name!r}: {comment!r},')
        g.set_indent(0)
        g.P('}')
        g.P()
        g.P()

        g.P(f'_{helper}_FIELD_ANNOTATIONS: typing.Dict[str, typing.Any] = {{')
        g.set_indent(4)
        for field in response.fields:
            if field.oneof and len(field.oneof.fields) > 1:
                continue
            g.P(f'{field.py_name!r}: {full_name}.model_fields[{field.py_name!r}].annotation,')
        g.set_indent(0)
        g.P('}')
        g.P()
        g.P()

        g.P(
            f'def _{helper}_gap_model('
            f'partial: {partial_name}'
            f') -> typing.Type[BaseModel]:',
        )
        g.set_indent(4)
        g.P('"""Build a Pydantic model containing only fields that are ``None`` on ``partial``."""')
        g.P('fields: typing.Dict[str, typing.Any] = {}')
        g.P(f'for name, annotation in _{helper}_FIELD_ANNOTATIONS.items():')
        g.set_indent(8)
        g.P('if getattr(partial, name, None) is None:')
        g.set_indent(12)
        g.P(f'desc = _{helper}_FIELD_DESCRIPTIONS.get(name)')
        g.P('kwargs: typing.Dict[str, typing.Any] = {}')
        g.P('if desc is not None:')
        g.set_indent(16)
        g.P('kwargs["description"] = desc')
        g.set_indent(12)
        g.P('fields[name] = (annotation, Field(**kwargs))')
        g.set_indent(4)
        g.P(f'return create_model(f"{full_name}Gap", __base__=BaseModel, **fields)')
        g.set_indent(0)
        g.P()
        g.P()

        g.P(f'def _{helper}_examples_prompt(examples: typing.Sequence[{partial_name}]) -> str:')
        g.set_indent(4)
        g.P('payload = [ex.model_dump(mode="json") for ex in examples]')
        g.P('return "Examples (JSON, null means unspecified):\\n" + json.dumps(payload, indent=2)')
        g.set_indent(0)
        g.P()
        g.P()

        g.P(
            f'def create_{helper}_agent('
            f'model: typing.Union[str, Model], *, '
            f'system_prompt: str, '
            f'output_type: typing.Any'
            f') -> Agent:',
        )
        g.set_indent(4)
        g.P(f'"""Build a PydanticAI ``Agent`` for ``{full_name}`` using ``NativeOutput``."""')
        if message_description is not None:
            g.P(
                f'return Agent('
                f'model, '
                f'output_type=NativeOutput('
                f'output_type, '
                f'name={agent_name!r}, '
                f'description={message_description!r}'
                f'), '
                f'system_prompt=system_prompt'
                f')',
            )
        else:
            g.P(
                f'return Agent('
                f'model, '
                f'output_type=NativeOutput(output_type, name={agent_name!r}), '
                f'system_prompt=system_prompt'
                f')',
            )
        g.set_indent(0)
        g.P()
        g.P()

        # async synthesize
        g.P(
            f'async def synthesize_{helper}('
            f'*, '
            f'model: typing.Union[str, Model], '
            f'system_prompt: str, '
            f'count: int = 1, '
            f'examples: typing.Optional[typing.Sequence[{partial_name}]] = None, '
            f'incomplete: typing.Optional[typing.Sequence[{partial_name}]] = None, '
            f'diversify_rounds: int = 0'
            f') -> typing.List[{full_name}]:',
        )
        g.set_indent(4)
        g.P(f'"""Synthesize ``{full_name}`` instances via PydanticAI ``NativeOutput``.')
        g.P()
        g.P('Path A (``incomplete`` is None): generate ``count`` full models, optionally')
        g.P('conditioned on ``examples`` (None-friendly partials). ``diversify_rounds``')
        g.P('feeds prior outputs back as examples for subsequent rounds.')
        g.P()
        g.P('Path B (``incomplete`` set): for each partial, ``create_model`` a gap schema')
        g.P('of only ``None`` fields, fill via NativeOutput, merge to a full model.')
        g.P('``count`` is ignored; ``diversify_rounds`` must be 0.')
        g.P('"""')
        g.P('if incomplete is not None and diversify_rounds > 0:')
        g.set_indent(8)
        g.P('raise ValueError("incomplete cannot be combined with diversify_rounds>0")')
        g.set_indent(4)
        g.P('if incomplete is not None:')
        g.set_indent(8)
        g.P(
            f'return await _{helper}_complete(model=model, system_prompt=system_prompt, incomplete=incomplete, examples=examples)',
        )
        g.set_indent(4)
        g.P(
            f'return await _{helper}_generate(model=model, system_prompt=system_prompt, count=count, examples=examples, diversify_rounds=diversify_rounds)',
        )
        g.set_indent(0)
        g.P()
        g.P()

        g.P(
            f'def synthesize_{helper}_sync('
            f'*, '
            f'model: typing.Union[str, Model], '
            f'system_prompt: str, '
            f'count: int = 1, '
            f'examples: typing.Optional[typing.Sequence[{partial_name}]] = None, '
            f'incomplete: typing.Optional[typing.Sequence[{partial_name}]] = None, '
            f'diversify_rounds: int = 0'
            f') -> typing.List[{full_name}]:',
        )
        g.set_indent(4)
        g.P(f'"""Sync wrapper around :func:`synthesize_{helper}`."""')
        g.P('import asyncio')
        g.P(
            f'return asyncio.run('
            f'synthesize_{helper}(model=model, system_prompt=system_prompt, count=count, examples=examples, incomplete=incomplete, diversify_rounds=diversify_rounds)'
            f')',
        )
        g.set_indent(0)
        g.P()
        g.P()

        # Path A helper
        g.P(
            f'async def _{helper}_generate('
            f'*, model: typing.Union[str, Model], system_prompt: str, count: int, '
            f'examples: typing.Optional[typing.Sequence[{partial_name}]], diversify_rounds: int'
            f') -> typing.List[{full_name}]:',
        )
        g.set_indent(4)
        g.P(f'results: typing.List[{full_name}] = []')
        g.P(f'example_buf: typing.List[{partial_name}] = list(examples or [])')
        g.P('rounds = max(diversify_rounds, 0) + 1')
        g.P('for round_idx in range(rounds):')
        g.set_indent(8)
        g.P(f'agent = create_{helper}_agent(model, system_prompt=system_prompt, output_type={full_name})')
        g.P('for _ in range(count):')
        g.set_indent(12)
        g.P('parts = ["Generate one new instance matching the output schema."]')
        g.P('if example_buf:')
        g.set_indent(16)
        g.P('if round_idx > 0:')
        g.set_indent(20)
        g.P('parts.append("Prefer diversity relative to the examples.")')
        g.set_indent(16)
        g.P(f'parts.append(_{helper}_examples_prompt(example_buf))')
        g.set_indent(12)
        g.P('run = await agent.run("\\n\\n".join(parts))')
        g.P(f'item = {full_name}.model_validate(run.output)')
        g.P('results.append(item)')
        g.P(f'example_buf.append({partial_name}.model_validate(item.model_dump()))')
        g.set_indent(4)
        g.P('return results')
        g.set_indent(0)
        g.P()
        g.P()

        # Path B helper
        g.P(
            f'async def _{helper}_complete('
            f'*, model: typing.Union[str, Model], system_prompt: str, '
            f'incomplete: typing.Sequence[{partial_name}], '
            f'examples: typing.Optional[typing.Sequence[{partial_name}]]'
            f') -> typing.List[{full_name}]:',
        )
        g.set_indent(4)
        g.P(f'results: typing.List[{full_name}] = []')
        g.P('for partial in incomplete:')
        g.set_indent(8)
        g.P(f'gap_cls = _{helper}_gap_model(partial)')
        g.P('if not gap_cls.model_fields:')
        g.set_indent(12)
        g.P(f'results.append({full_name}.model_validate(partial.model_dump(exclude_none=True)))')
        g.P('continue')
        g.set_indent(8)
        g.P(f'agent = create_{helper}_agent(model, system_prompt=system_prompt, output_type=gap_cls)')
        g.P('parts = [')
        g.set_indent(12)
        g.P('"Fill only the missing fields for this partial example.",')
        g.P('"Partial (JSON): " + json.dumps(partial.model_dump(mode="json"), indent=2),')
        g.set_indent(8)
        g.P(']')
        g.P('if examples:')
        g.set_indent(12)
        g.P(f'parts.append(_{helper}_examples_prompt(examples))')
        g.set_indent(8)
        g.P('run = await agent.run("\\n\\n".join(parts))')
        g.P('gap = run.output')
        g.P('merged = {**partial.model_dump(exclude_none=True), **gap.model_dump()}')
        g.P(f'results.append({full_name}.model_validate(merged))')
        g.set_indent(4)
        g.P('return results')
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


pydantic_ai_spec = GeneratorSpec(
    name='pydantic_ai',
    factory=lambda plugin: PydanticAIGenerator(plugin),
    enabled_by_default=False,
    description='PydanticAI NativeOutput synthesis helpers for (pgml.pydantic_ai) messages.',
)
