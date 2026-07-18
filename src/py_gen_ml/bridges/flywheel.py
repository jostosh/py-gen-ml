"""Thin flywheel orchestration helpers (docs / demos)."""
from __future__ import annotations

from typing import Any, Callable, Iterable, List, TypeVar

T = TypeVar('T')


def seeds_to_dicts(
    rows: Iterable[T],
    *,
    dump: Callable[[T], dict[str, Any]] | None = None,
) -> List[dict[str, Any]]:
    """Serialize seed / feature rows to JSON-friendly dicts."""
    if dump is None:
        return [
            row.model_dump(mode='json') if hasattr(row, 'model_dump') else dict(row)  # type: ignore[arg-type]
            for row in rows
        ]
    return [dump(row) for row in rows]


def annotated_rows_to_dicts(
    rows: Iterable[T],
    *,
    dump: Callable[[T], dict[str, Any]] | None = None,
) -> List[dict[str, Any]]:
    """Serialize annotated / feedback rows for LanceDB or downstream stores."""
    return seeds_to_dicts(rows, dump=dump)
