"""LanceDB table helpers for feature-row seeds and annotated rows."""
from __future__ import annotations

from typing import Any, List, Optional, Sequence, Type, TypeVar

from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


def append_feature_rows(table: Any, rows: Sequence[T]) -> None:
    """Append Pydantic/LanceModel rows to an open LanceDB table."""
    table.add([row.model_dump() for row in rows])


def load_seeds_from_table(
    table: Any,
    *,
    model_cls: Type[T],
    limit: Optional[int] = None,
) -> List[T]:
    """Load rows from a Lance table and validate as ``model_cls`` instances."""
    if hasattr(table, 'to_pandas'):
        frame = table.to_pandas()
        if limit is not None:
            frame = frame.head(limit)
        return [model_cls.model_validate(row) for row in frame.to_dict(orient='records')]
    raise TypeError('table must support to_pandas() for load_seeds_from_table')
