"""Serving prediction → Argilla HITL helpers."""
from __future__ import annotations

from typing import Callable, Optional, TypeVar

TReq = TypeVar('TReq')
TResp = TypeVar('TResp')
TRec = TypeVar('TRec')


def log_prediction_for_review(
    request: TReq,
    response: TResp,
    *,
    merge: Callable[[TReq, TResp], TRec],
    to_record: Callable[[TRec], object],
    log: Optional[Callable[[object], None]] = None,
) -> object:
    """Build an Argilla record from a serving request/response pair.

    ``merge`` should produce the Argilla-enabled message model; ``to_record`` is
    typically a generated ``to_*_record``. Optional ``log`` persists the record.
    """
    row = merge(request, response)
    record = to_record(row)
    if log is not None:
        log(record)
    return record
