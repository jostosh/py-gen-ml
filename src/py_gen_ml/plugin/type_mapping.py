"""Pluggable mapping from protobuf field kinds to language-level type names.

The default :class:`PythonTypeMapper` reproduces the kind-by-kind mapping used by
:mod:`py_gen_ml.plugin.base_model_generator` and
:mod:`py_gen_ml.plugin.cli_args_generator`. Future generators that emit non-Python
types (PyArrow schemas for LanceDB, torch dtypes for GPU loaders, etc.) can
implement the :class:`TypeMapper` protocol with their own kind table without
touching the plugin core.
"""
from typing import Optional, Protocol, runtime_checkable

import protogen

from py_gen_ml.typing.some import some

_PATCH_SUFFIX: str = 'Patch'


@runtime_checkable
class TypeMapper(Protocol):
    """Protocol mapping a protobuf field to its rendered type expression.

    Implementations are responsible for deciding how to render messages, enums,
    and scalars. Generators are expected to call :meth:`field_to_type` for each
    field they emit.
    """

    def field_to_type(self, field: protogen.Field) -> str:  # pragma: no cover - protocol
        """Return the rendered type expression for ``field``."""
        ...


class PythonTypeMapper:
    """Default :class:`TypeMapper` rendering Python type expressions.

    Args:
        is_patch: When ``True``, message types are suffixed with ``Patch`` so the
            mapping mirrors the patch-model output.
        enum_alias_prefix: Optional module alias used to qualify enum names
            (e.g. ``'base'`` so an enum renders as ``base.MyEnum``). When ``None``
            the bare enum name is used.
    """

    def __init__(
        self,
        *,
        is_patch: bool = False,
        enum_alias_prefix: Optional[str] = None,
        message_suffix: Optional[str] = None,
    ) -> None:
        self._is_patch = is_patch
        self._enum_alias_prefix = enum_alias_prefix
        self._message_suffix = message_suffix

    def field_to_type(self, field: protogen.Field) -> str:
        if field.kind == protogen.Kind.MESSAGE:
            message = some(field.message)
            name = message.py_ident.py_name
            if self._is_patch:
                return f'{name}{_PATCH_SUFFIX}'
            if self._message_suffix:
                return f'{name}{self._message_suffix}'
            return name
        if field.kind == protogen.Kind.ENUM:
            enum = some(field.enum)
            name = enum.py_ident.py_name
            prefix = self._enum_alias_prefix
            if self._is_patch and prefix is None:
                # Patch models import enums from the base module.
                prefix = 'base'
            if prefix:
                return f'{prefix}.{name}'
            return name
        try:
            return _SCALAR_KINDS[field.kind]
        except KeyError as exc:  # pragma: no cover - defensive
            raise ValueError(f'Unknown field kind: {field.kind}') from exc


_SCALAR_KINDS: dict[protogen.Kind, str] = {
    protogen.Kind.DOUBLE: 'float',
    protogen.Kind.FLOAT: 'float',
    protogen.Kind.INT64: 'int',
    protogen.Kind.UINT64: 'int',
    protogen.Kind.INT32: 'int',
    protogen.Kind.FIXED64: 'int',
    protogen.Kind.FIXED32: 'int',
    protogen.Kind.BOOL: 'bool',
    protogen.Kind.STRING: 'str',
    protogen.Kind.BYTES: 'bytes',
    protogen.Kind.UINT32: 'int',
    protogen.Kind.SFIXED32: 'int',
    protogen.Kind.SFIXED64: 'int',
    protogen.Kind.SINT32: 'int',
    protogen.Kind.SINT64: 'int',
}
