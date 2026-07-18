"""Unit tests for shared tracking slot / flatten helpers."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import protogen

from py_gen_ml.extensions_pb2 import PARAM
from py_gen_ml.plugin.tracking import (
    format_paths_literal,
    is_scalar_leaf,
    tracking_key,
)


def test_format_paths_literal() -> None:
    assert format_paths_literal([]) == '[]'
    assert format_paths_literal([('a.b', 'a.b')]) == "[('a.b', 'a.b')]"


def test_is_scalar_leaf_rejects_lists_and_messages() -> None:
    field = MagicMock()
    field.is_list.return_value = True
    field.kind = protogen.Kind.INT32
    assert is_scalar_leaf(field) is False

    field = MagicMock()
    field.is_list.return_value = False
    field.kind = protogen.Kind.MESSAGE
    assert is_scalar_leaf(field) is False

    field = MagicMock()
    field.is_list.return_value = False
    field.kind = protogen.Kind.FLOAT
    assert is_scalar_leaf(field) is True


def test_tracking_key_uses_alias_when_present(monkeypatch) -> None:
    field = MagicMock()
    field.py_name = 'learning_rate'
    opts = SimpleNamespace(name='lr', slot=PARAM)
    monkeypatch.setattr(
        'py_gen_ml.plugin.tracking.get_extension_value',
        lambda *_a,
        **_k: opts,
    )
    assert tracking_key(field) == 'lr'
    assert tracking_key(field, prefix='optimizer') == 'optimizer.lr'
