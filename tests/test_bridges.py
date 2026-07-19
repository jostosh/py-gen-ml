"""Tests for py_gen_ml.bridges helpers."""
from __future__ import annotations

import pytest

from py_gen_ml.bridges.flywheel import seeds_to_dicts
from py_gen_ml.bridges.lancedb_rows import append_rows, merge_rows
from py_gen_ml.bridges.serving_argilla import log_prediction_for_review
from py_gen_ml.bridges.synthesis_argilla import (
    synthetic_rows_to_argilla_records,
)


class _Row:

    def __init__(self, x: int) -> None:
        self.x = x

    def model_dump(self, mode: str = 'python'):
        return {'x': self.x}


class _FakeMergeBuilder:

    def __init__(self, table: '_FakeTable', on: list[str]) -> None:
        self._table = table
        self._on = on

    def when_matched_update_all(self) -> '_FakeMergeBuilder':
        return self

    def when_not_matched_insert_all(self) -> '_FakeMergeBuilder':
        return self

    def execute(self, rows: list[dict]) -> None:
        self._table.executed.append((self._on, rows))


class _FakeTable:

    def __init__(self) -> None:
        self.executed: list[tuple[list[str], list[dict]]] = []
        self.added: list[dict] = []

    def merge_insert(self, on: list[str]) -> _FakeMergeBuilder:
        return _FakeMergeBuilder(self, on)

    def add(self, rows: list[dict]) -> None:
        self.added.extend(rows)


def test_seeds_to_dicts() -> None:
    assert seeds_to_dicts([_Row(1), _Row(2)]) == [{'x': 1}, {'x': 2}]


def test_synthetic_rows_to_argilla_records() -> None:
    records = synthetic_rows_to_argilla_records([_Row(1)], to_record=lambda r: {'v': r.x})
    assert records == [{'v': 1}]


def test_log_prediction_for_review() -> None:
    logged: list[object] = []
    record = log_prediction_for_review(
        {'f': 1.0},
        {'y': 0},
        merge=lambda req,
        resp: {
            **req,
            **resp,
        },
        to_record=lambda row: row,
        log=logged.append,
    )
    assert record == {'f': 1.0, 'y': 0}
    assert logged == [record]


def test_append_rows() -> None:
    table = _FakeTable()
    append_rows(table, [_Row(1), _Row(2)])  # type: ignore[arg-type]
    assert table.added == [{'x': 1}, {'x': 2}]


def test_merge_rows() -> None:
    table = _FakeTable()
    merge_rows(table, [_Row(1), _Row(2)], on=['x'])  # type: ignore[arg-type]
    assert table.executed == [(['x'], [{'x': 1}, {'x': 2}])]


def test_merge_rows_requires_on() -> None:
    with pytest.raises(ValueError, match='at least one join column'):
        merge_rows(_FakeTable(), [_Row(1)], on=[])  # type: ignore[arg-type]
