"""Shared emission of Pydantic-style model classes from protobuf messages."""
from __future__ import annotations

from typing import Callable, Optional

import protogen

from py_gen_ml.plugin.common import generate_docstring


def field_leading_comment(field: protogen.Field) -> Optional[str]:
    """Return stripped leading comment for ``field``, or ``None`` if absent."""
    comment = field.location.leading_comments
    if not comment:
        return None
    return ' '.join(comment.strip().split())


def message_leading_comment(message: protogen.Message) -> Optional[str]:
    """Return stripped leading comment for ``message``, or ``None`` if absent."""
    comment = message.location.leading_comments
    if not comment:
        return None
    return ' '.join(comment.strip().split())


def emit_pydantic_model(
    g: protogen.GeneratedFile,
    message: protogen.Message,
    *,
    base_class: str,
    field_annotation: Callable[[protogen.Field], str],
    field_type: Callable[[protogen.Field], str],
    class_name: Optional[str] = None,
    use_field_descriptions: bool = False,
    all_optional: bool = False,
) -> None:
    """Emit a ``class {message}({base_class}):`` body for ``message``.

    Shared by opt-in generators (LanceDB, BentoML, LitServe, PydanticAI, …)
    that need a Pydantic-like class for a message closure.

    When ``use_field_descriptions`` is true, proto field comments are emitted as
    ``pydantic.Field(description=...)`` so they appear in ``model_json_schema()``.
    When ``all_optional`` is true, every field is ``Optional[...] = None`` (Partial
    models for synthesis examples / incomplete rows).
    """
    name = class_name or message.proto.name
    g.P(f'class {name}({base_class}):')
    g.set_indent(4)
    generate_docstring(g, message)

    wrote_field = False
    for field in message.fields:
        if field.oneof and len(field.oneof.fields) > 1:
            continue
        annotation = field_annotation(field)
        if all_optional and not annotation.startswith('typing.Optional['):
            annotation = f'typing.Optional[{annotation}]'
        _emit_field_line(g, field.py_name, annotation, field, use_field_descriptions, all_optional)
        if not use_field_descriptions:
            generate_docstring(g, field)
        wrote_field = True

    for oneof in message.oneofs:
        if len(oneof.fields) == 1:
            continue
        types = [field_type(field) for field in oneof.fields]
        annotation = f'typing.Union[{", ".join(types)}]'
        if all_optional:
            annotation = f'typing.Optional[{annotation}]'
        _emit_field_line(g, oneof.proto.name, annotation, oneof, use_field_descriptions, all_optional)
        if not use_field_descriptions:
            generate_docstring(g, oneof)
        wrote_field = True

    if not wrote_field:
        g.P('pass')

    g.set_indent(0)
    g.P()
    g.P()


def _emit_field_line(
    g: protogen.GeneratedFile,
    py_name: str,
    annotation: str,
    element: protogen.Field | protogen.OneOf,
    use_field_descriptions: bool,
    all_optional: bool,
) -> None:
    description = None
    if use_field_descriptions and hasattr(element, 'location'):
        raw = element.location.leading_comments
        if raw:
            description = ' '.join(raw.strip().split())

    if use_field_descriptions or all_optional:
        field_args: list[str] = []
        if all_optional:
            field_args.append('default=None')
        if description is not None:
            field_args.append(f'description={description!r}')
        if field_args:
            g.P(f'{py_name}: {annotation} = Field({", ".join(field_args)})')
            return

    g.P(f'{py_name}: {annotation}')
