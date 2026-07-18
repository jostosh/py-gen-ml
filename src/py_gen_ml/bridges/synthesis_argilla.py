"""Bridge PydanticAI / synthesis rows into Argilla records."""
from __future__ import annotations

from typing import Any, Callable, Iterable, List, TypeVar

T = TypeVar('T')
R = TypeVar('R')


def synthetic_rows_to_argilla_records(
    rows: Iterable[T],
    *,
    to_record: Callable[[T], R],
) -> List[R]:
    """Map synthesized full models to Argilla records via a generated mapper."""
    return [to_record(row) for row in rows]


def log_records(
    dataset: Any,
    records: Iterable[Any],
) -> None:
    """Best-effort ``dataset.records.log`` wrapper (Argilla SDK)."""
    dataset.records.log(list(records))
