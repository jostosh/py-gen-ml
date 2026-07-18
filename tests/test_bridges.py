"""Tests for py_gen_ml.bridges helpers."""
from __future__ import annotations

from py_gen_ml.bridges.flywheel import seeds_to_dicts
from py_gen_ml.bridges.serving_argilla import log_prediction_for_review
from py_gen_ml.bridges.synthesis_argilla import (
    synthetic_rows_to_argilla_records,
)


class _Row:

    def __init__(self, x: int) -> None:
        self.x = x

    def model_dump(self, mode: str = 'python'):
        return {'x': self.x}


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
