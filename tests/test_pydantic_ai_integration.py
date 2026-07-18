"""Smoke tests for PydanticAI generated helpers (mocked Agent)."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytest.importorskip('pydantic_ai')

REPO = Path(__file__).resolve().parents[1]
SNIPPETS_SRC = REPO / 'docs' / 'snippets' / 'src'


@pytest.fixture
def synth_mod(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.syspath_prepend(str(SNIPPETS_SRC))
    from pgml_out import flywheel_demo_pydantic_ai as mod

    return mod


def test_field_descriptions_in_json_schema(synth_mod) -> None:
    schema = synth_mod.ReviewExample.model_json_schema()
    props = schema['properties']
    assert 'instruction' in props
    assert 'description' in props['instruction']
    assert 'prompt' in props['instruction']['description'].lower(
    ) or 'answer' in props['instruction']['description'].lower()


def test_gap_model_only_missing_fields(synth_mod) -> None:
    partial = synth_mod.ReviewExamplePartial(
        id='1',
        instruction='Explain gravity',
        generation=None,
        quality=None,
    )
    gap = synth_mod._review_example_gap_model(partial)
    assert set(gap.model_fields) == {'generation', 'quality'}


def test_synthesize_complete_path_merges(synth_mod) -> None:
    import asyncio

    partial = synth_mod.ReviewExamplePartial(
        id='1',
        instruction='Explain gravity',
        generation=None,
        quality=None,
    )

    class _Gap:

        def model_dump(self):
            return {'generation': 'Gravity pulls masses together.', 'quality': 'good'}

    run = MagicMock()
    run.output = _Gap()
    agent = MagicMock()
    agent.run = AsyncMock(return_value=run)

    with patch.object(synth_mod, 'create_review_example_agent', return_value=agent):
        rows = asyncio.run(
            synth_mod.synthesize_review_example(
                model='test',
                system_prompt='Fill gaps.',
                incomplete=[partial],
            ),
        )

    assert len(rows) == 1
    assert rows[0].instruction == 'Explain gravity'
    assert rows[0].generation.startswith('Gravity')
    assert rows[0].quality == 'good'
