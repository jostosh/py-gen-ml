"""Shared experiment-tracking slot resolution and flatten helpers for codegen."""
from __future__ import annotations

from typing import List, Optional, Tuple

import protogen

from py_gen_ml.extensions_pb2 import (
    METRIC,
    METRIC_SET,
    PARAM,
    RUN_CONFIG,
    TRACKING_SLOT_UNSPECIFIED,
    TrackingField,
    TrackingSlot,
)
from py_gen_ml.plugin.common import get_extension_value
from py_gen_ml.plugin.message_kind import get_message_kind

_SCALAR_KINDS = {
    protogen.Kind.DOUBLE,
    protogen.Kind.FLOAT,
    protogen.Kind.INT64,
    protogen.Kind.UINT64,
    protogen.Kind.INT32,
    protogen.Kind.FIXED64,
    protogen.Kind.FIXED32,
    protogen.Kind.BOOL,
    protogen.Kind.STRING,
    protogen.Kind.BYTES,
    protogen.Kind.UINT32,
    protogen.Kind.ENUM,
    protogen.Kind.SFIXED32,
    protogen.Kind.SFIXED64,
    protogen.Kind.SINT32,
    protogen.Kind.SINT64,
}


def default_slot_for_kind(message: protogen.Message) -> Optional[TrackingSlot]:
    """Default tracking slot from ``(pgml.kind)``: RUN_CONFIG→PARAM, METRIC_SET→METRIC."""
    kind = get_message_kind(message)
    if kind == RUN_CONFIG:
        return PARAM
    if kind == METRIC_SET:
        return METRIC
    return None


def resolve_field_slot(
    field: protogen.Field,
    *,
    default_slot: Optional[TrackingSlot],
) -> Optional[TrackingSlot]:
    """Resolve PARAM/METRIC/TAG for ``field`` given the enclosing message default."""
    opts = get_extension_value(field, 'tracking_field', TrackingField)
    if opts is not None and opts.slot != TRACKING_SLOT_UNSPECIFIED:
        return opts.slot
    return default_slot


def tracking_key(field: protogen.Field, prefix: str = '') -> str:
    """Log key for ``field`` (optional alias from ``tracking_field.name``)."""
    opts = get_extension_value(field, 'tracking_field', TrackingField)
    name = (opts.name if opts is not None and opts.name else field.py_name)
    return f'{prefix}.{name}' if prefix else name


def is_scalar_leaf(field: protogen.Field) -> bool:
    """True when ``field`` is a non-list scalar/enum suitable for flattening."""
    if field.is_list():
        return False
    if field.kind == protogen.Kind.MESSAGE:
        return False
    return field.kind in _SCALAR_KINDS


def collect_slot_paths(
    message: protogen.Message,
    slot: TrackingSlot,
    *,
    prefix: str = '',
    default_slot: Optional[TrackingSlot] = None,
) -> List[Tuple[str, str]]:
    """Collect ``(dotted_attr_path, log_key)`` pairs for fields with ``slot``.

    Nested message fields are walked; leaf scalars matching ``slot`` are kept.
    ``default_slot`` is inherited from the root ``RUN_CONFIG`` / ``METRIC_SET``
    kind when not passed explicitly.
    """
    if default_slot is None:
        default_slot = default_slot_for_kind(message)

    paths: List[Tuple[str, str]] = []
    for field in message.fields:
        if field.oneof and len(field.oneof.fields) > 1:
            continue
        attr = f'{prefix}.{field.py_name}' if prefix else field.py_name
        if field.kind == protogen.Kind.MESSAGE and field.message is not None and not field.is_list():
            paths.extend(
                collect_slot_paths(
                    field.message,
                    slot,
                    prefix=attr,
                    default_slot=default_slot,
                ),
            )
            continue
        if not is_scalar_leaf(field):
            continue
        resolved = resolve_field_slot(field, default_slot=default_slot)
        if resolved != slot:
            continue
        key = tracking_key(field, prefix=prefix)
        paths.append((attr, key))
    return paths


def format_paths_literal(paths: List[Tuple[str, str]]) -> str:
    """Python list literal of ``(attr_path, log_key)`` tuples for codegen."""
    if not paths:
        return '[]'
    items = ', '.join(f'({attr!r}, {key!r})' for attr, key in paths)
    return f'[{items}]'


def getattr_chain_expr(attr_path: str, root_var: str = 'obj') -> str:
    """Python expression that reads a dotted path from ``root_var``."""
    parts = attr_path.split('.')
    expr = root_var
    for part in parts:
        expr = f'getattr({expr}, {part!r})'
    return expr
