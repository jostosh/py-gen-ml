"""LanceDB table helpers for feature / prediction / feedback rows."""
from __future__ import annotations

from typing import List, Optional, Sequence, Type, TypeVar, Union

from lancedb.table import LanceTable
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


def append_rows(table: LanceTable, rows: Sequence[T]) -> None:
    """Append Pydantic/LanceModel rows via ``table.add(...)``.

    Use when there is no join key (no ``(pgml.lancedb_field).merge_key``).
    Prefer :func:`merge_rows` for upserts when merge keys are defined.
    """
    if not rows:
        return
    table.add([row.model_dump() for row in rows])


def merge_rows(
    table: LanceTable,
    rows: Sequence[T],
    *,
    on: Union[str, Sequence[str]],
) -> None:
    """Upsert Pydantic/LanceModel rows via ``table.merge_insert(on=...)``.

    Matched rows (join on ``on``) are updated; unmatched source rows are inserted.
    Pass join columns from generated ``*_merge_on()`` (fields with
    ``(pgml.lancedb_field).merge_key``). Use :func:`append_rows` when there is
    no merge key.
    """
    keys = [on] if isinstance(on, str) else list(on)
    if not keys:
        raise ValueError('merge_rows requires at least one join column in on=')
    if not rows:
        return
    (
        table.merge_insert(keys).when_matched_update_all().when_not_matched_insert_all().execute([
            row.model_dump() for row in rows
        ])
    )


def load_seeds_from_table(
    table: LanceTable,
    *,
    model_cls: Type[T],
    limit: Optional[int] = None,
) -> List[T]:
    """Load rows from a Lance table and validate as ``model_cls`` instances."""
    frame = table.to_pandas()
    if limit is not None:
        frame = frame.head(limit)
    return [model_cls.model_validate(row) for row in frame.to_dict(orient='records')]
