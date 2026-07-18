"""Runtime bridges composing generated py-gen-ml adapters across tools."""
from __future__ import annotations

from py_gen_ml.bridges.flywheel import annotated_rows_to_dicts, seeds_to_dicts
from py_gen_ml.bridges.lancedb_rows import (
    append_feature_rows,
    append_rows,
    load_seeds_from_table,
)
from py_gen_ml.bridges.serving_argilla import log_prediction_for_review
from py_gen_ml.bridges.synthesis_argilla import (
    synthetic_rows_to_argilla_records,
)

__all__ = [
    'append_feature_rows',
    'append_rows',
    'load_seeds_from_table',
    'log_prediction_for_review',
    'seeds_to_dicts',
    'annotated_rows_to_dicts',
    'synthetic_rows_to_argilla_records',
]
