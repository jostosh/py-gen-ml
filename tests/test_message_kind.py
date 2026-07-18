"""Tests for message kind helpers and fixture annotations."""
from __future__ import annotations

from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock, patch

import networkx
import pytest

from py_gen_ml.extensions_pb2 import FEATURE_ROW, LABEL, MESSAGE_KIND_UNSPECIFIED
from py_gen_ml.plugin.message_kind import (
    collect_message_closure,
    get_message_kind,
    messages_with_kind,
    ordered_messages,
)


class _FakeField:
    def __init__(self, message: Optional[object] = None) -> None:
        self.message = message


class _FakeMessage:
    def __init__(self, name: str, fields: Optional[list[_FakeField]] = None) -> None:
        self.fields = fields or []
        self.proto = MagicMock()
        self.proto.name = name


def test_get_message_kind_defaults_to_unspecified() -> None:
    message = MagicMock()
    with patch('py_gen_ml.plugin.message_kind.get_extension_value', return_value=None):
        assert get_message_kind(message) == MESSAGE_KIND_UNSPECIFIED


def test_get_message_kind_reads_extension() -> None:
    message = MagicMock()
    with patch('py_gen_ml.plugin.message_kind.get_extension_value', return_value=FEATURE_ROW):
        assert get_message_kind(message) == FEATURE_ROW


def test_messages_with_kind_filters_exact_kind() -> None:
    feature = MagicMock()
    label = MagicMock()
    other = MagicMock()
    file = MagicMock()
    file.messages = [feature, label, other]

    def kind_for(message: object) -> object:
        return {
            id(feature): FEATURE_ROW,
            id(label): LABEL,
            id(other): None,
        }[id(message)]

    with patch(
        'py_gen_ml.plugin.message_kind.get_extension_value',
        side_effect=lambda message, *_args: kind_for(message),
    ):
        assert messages_with_kind(file, FEATURE_ROW) == [feature]
        assert messages_with_kind(file, LABEL) == [label]


def test_collect_message_closure_walks_nested_same_file() -> None:
    meta = _FakeMessage('Meta')
    root = _FakeMessage('Root', fields=[_FakeField(meta)])
    other = _FakeMessage('Other')
    file = MagicMock()
    file.messages = [root, meta, other]

    assert collect_message_closure([root], file) == {root, meta}


def test_collect_message_closure_ignores_out_of_file_nested() -> None:
    external = _FakeMessage('External')
    root = _FakeMessage('Root', fields=[_FakeField(external)])
    file = MagicMock()
    file.messages = [root]

    assert collect_message_closure([root], file) == {root}


def test_ordered_messages_topo_then_unseen() -> None:
    nested = _FakeMessage('Nested')
    root = _FakeMessage('Root')
    orphan = _FakeMessage('Orphan')
    file = MagicMock()

    graph = networkx.MultiDiGraph()
    graph.add_edge(nested, root)

    with patch(
        'py_gen_ml.plugin.message_kind.get_element_subgraphs',
        return_value=[graph],
    ):
        ordered = ordered_messages(file, {root, nested, orphan})

    assert set(ordered) == {nested, root, orphan}
    assert ordered.index(nested) < ordered.index(root)
    assert orphan in ordered


@pytest.mark.parametrize(
    'proto_path',
    [
        Path(__file__).parent / 'protos' / 'unit.proto',
        Path(__file__).resolve().parents[1] / 'docs' / 'snippets' / 'proto' / 'lancedb_demo.proto',
    ],
)
def test_feature_row_kind_annotated_on_lancedb_roots(proto_path: Path) -> None:
    source = proto_path.read_text()
    assert 'option (pgml.kind) = FEATURE_ROW;' in source


def test_unit_lancedb_fixture_still_emits_models() -> None:
    source = Path(__file__).parent.joinpath('pgml_out_test', 'unit_lancedb.py').read_text()
    assert 'class LanceDBRecordTest(LanceModel):' in source
