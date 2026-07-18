"""Tests for shared schema emission helpers."""
from __future__ import annotations

from unittest.mock import MagicMock

from py_gen_ml.plugin.schema_emit import emit_pydantic_model


class _Buf:

    def __init__(self) -> None:
        self.lines: list[str] = []
        self._indent = 0

    def P(self, *parts: object) -> None:
        text = ''.join(str(p) for p in parts)
        self.lines.append((' ' * self._indent) + text if text else text)

    def set_indent(self, n: int) -> None:
        self._indent = n


def _message(
    name: str,
    *,
    fields: list[object] | None = None,
    oneofs: list[object] | None = None,
    comment: str = '',
) -> MagicMock:
    message = MagicMock()
    message.proto.name = name
    message.fields = fields or []
    message.oneofs = oneofs or []
    message.location.leading_comments = comment
    return message


def _field(py_name: str, annotation: str = 'int', *, oneof: object | None = None) -> MagicMock:
    field = MagicMock()
    field.py_name = py_name
    field.oneof = oneof
    field.location.leading_comments = ''
    field._annotation = annotation
    return field


def test_emit_pydantic_model_emits_fields_and_base() -> None:
    g = _Buf()
    message = _message('Foo', fields=[_field('x'), _field('y')])

    emit_pydantic_model(
        g,  # type: ignore[arg-type]
        message,
        base_class='BaseModel',
        field_annotation=lambda f: f._annotation,
        field_type=lambda f: f._annotation,
    )

    text = '\n'.join(g.lines)
    assert 'class Foo(BaseModel):' in text
    assert 'x: int' in text
    assert 'y: int' in text


def test_emit_pydantic_model_empty_message_uses_pass() -> None:
    g = _Buf()
    message = _message('Empty')

    emit_pydantic_model(
        g,  # type: ignore[arg-type]
        message,
        base_class='LanceModel',
        field_annotation=lambda f: 'str',
        field_type=lambda f: 'str',
    )

    text = '\n'.join(g.lines)
    assert 'class Empty(LanceModel):' in text
    assert 'pass' in text


def test_emit_pydantic_model_field_descriptions() -> None:
    g = _Buf()
    field = _field('instruction', 'str')
    field.location.leading_comments = 'User-facing task prompt.'
    message = _message('Ex', fields=[field])

    emit_pydantic_model(
        g,  # type: ignore[arg-type]
        message,
        base_class='BaseModel',
        field_annotation=lambda f: f._annotation,
        field_type=lambda f: f._annotation,
        use_field_descriptions=True,
    )

    text = '\n'.join(g.lines)
    assert "Field(description='User-facing task prompt.')" in text


def test_emit_pydantic_model_all_optional_partial() -> None:
    g = _Buf()
    message = _message('Ex', fields=[_field('instruction', 'str')])

    emit_pydantic_model(
        g,  # type: ignore[arg-type]
        message,
        base_class='BaseModel',
        field_annotation=lambda f: f._annotation,
        field_type=lambda f: f._annotation,
        class_name='ExPartial',
        use_field_descriptions=True,
        all_optional=True,
    )

    text = '\n'.join(g.lines)
    assert 'class ExPartial(BaseModel):' in text
    assert 'typing.Optional[str]' in text
    assert 'default=None' in text


def test_emit_pydantic_model_multi_oneof_as_union() -> None:
    g = _Buf()
    oneof = MagicMock()
    oneof.proto.name = 'choice'
    oneof.location.leading_comments = ''
    a = _field('a', 'int', oneof=oneof)
    b = _field('b', 'str', oneof=oneof)
    oneof.fields = [a, b]
    message = _message('WithOneof', fields=[a, b], oneofs=[oneof])

    emit_pydantic_model(
        g,  # type: ignore[arg-type]
        message,
        base_class='BaseModel',
        field_annotation=lambda f: f._annotation,
        field_type=lambda f: f._annotation,
    )

    text = '\n'.join(g.lines)
    assert 'a: int' not in text.split('choice:')[0] or 'choice: typing.Union[int, str]' in text
    assert 'choice: typing.Union[int, str]' in text
    # Individual oneof members should not appear as fields.
    assert '\na: int\n' not in f'\n{text}\n'
    assert '\nb: str\n' not in f'\n{text}\n'
