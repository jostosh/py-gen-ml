"""Smoke tests for Argilla generated Settings / records."""
from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip('argilla')

REPO = Path(__file__).resolve().parents[1]
SNIPPETS_SRC = REPO / 'docs' / 'snippets' / 'src'


def test_build_settings_and_roundtrip(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(SNIPPETS_SRC))
    from unittest.mock import MagicMock

    from pgml_out.flywheel_demo_argilla import (
        ReviewExample,
        build_review_example_settings,
        from_review_example_record,
        to_review_example_record,
    )

    client = MagicMock()
    settings = build_review_example_settings(client=client)
    field_names = {f.name for f in settings.fields}
    question_names = {q.name for q in settings.questions}
    assert field_names == {'instruction', 'generation'}
    assert question_names == {'quality'}
    assert 'id' not in field_names

    row = ReviewExample(
        id='ex-1',
        instruction='Say hello',
        generation='Hello!',
        quality='good',
    )
    record = to_review_example_record(row)
    assert record.fields['instruction'] == 'Say hello'
    assert record.metadata['id'] == 'ex-1'
    back = from_review_example_record(record)
    assert back.instruction == row.instruction
    assert back.id == row.id
