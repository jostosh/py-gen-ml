"""Shared emission of Pydantic-style model classes from protobuf messages."""
from __future__ import annotations

from typing import Callable

import protogen

from py_gen_ml.plugin.common import generate_docstring


def emit_pydantic_model(
    g: protogen.GeneratedFile,
    message: protogen.Message,
    *,
    base_class: str,
    field_annotation: Callable[[protogen.Field], str],
    field_type: Callable[[protogen.Field], str],
) -> None:
    """Emit a ``class {message}({base_class}):`` body for ``message``.

    Shared by opt-in generators (LanceDB, BentoML, …) that need a Pydantic-like
    class for a message closure. Callers supply ``field_annotation`` /
    ``field_type`` for tool-specific types (e.g. ``Vector(dim)``, enum-as-str).

    Multi-field oneof members are skipped as individual fields and emitted as a
    single ``typing.Union[...]`` on the oneof name. Empty messages get ``pass``.
    """
    g.P(f'class {message.proto.name}({base_class}):')
    g.set_indent(4)
    generate_docstring(g, message)

    wrote_field = False
    for field in message.fields:
        if field.oneof and len(field.oneof.fields) > 1:
            continue
        g.P(f'{field.py_name}: {field_annotation(field)}')
        generate_docstring(g, field)
        wrote_field = True

    for oneof in message.oneofs:
        if len(oneof.fields) == 1:
            continue
        types = [field_type(field) for field in oneof.fields]
        g.P(f'{oneof.proto.name}: typing.Union[{", ".join(types)}]')
        generate_docstring(g, oneof)
        wrote_field = True

    if not wrote_field:
        g.P('pass')

    g.set_indent(0)
    g.P()
    g.P()
