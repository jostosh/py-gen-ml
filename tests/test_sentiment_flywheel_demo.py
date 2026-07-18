"""Validate the IMDB sentiment flywheel demo helpers (no live API calls)."""
from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip('sklearn')
pytest.importorskip('lancedb')
pytest.importorskip('argilla')
pytest.importorskip('pydantic_ai')

REPO = Path(__file__).resolve().parents[1]
SNIPPETS = REPO / 'docs' / 'snippets'
SNIPPETS_SRC = SNIPPETS / 'src'


@pytest.fixture
def demo(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.syspath_prepend(str(SNIPPETS_SRC))
    from snippets import sentiment_flywheel_demo as mod

    return mod


def test_imdb_seeds_load(demo) -> None:
    seeds = demo.load_imdb_seeds()
    assert len(seeds) >= 4
    assert {s.sentiment for s in seeds} == {'positive', 'negative'}
    assert all(s.source == 'imdb' for s in seeds)


def test_openai_model_from_env_requires_vars(demo, monkeypatch: pytest.MonkeyPatch) -> None:
    for key in ('OPENAI_API_KEY', 'OPENAI_ENDPOINT', 'OPENAI_MODEL', 'OPENAI_API_VERSION'):
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(KeyError, match='OPENAI_'):
        demo.openai_model_from_env()


def test_openai_model_from_env_builds_model(demo, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv('OPENAI_API_KEY', 'test-key')
    monkeypatch.setenv('OPENAI_ENDPOINT', 'https://example.openai.azure.com/')
    monkeypatch.setenv('OPENAI_MODEL', 'gpt-4o')
    monkeypatch.setenv('OPENAI_API_VERSION', '2024-12-01-preview')
    model = demo.openai_model_from_env()
    assert model.model_name == 'gpt-4o'


def test_json_schema_descriptions_present(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(SNIPPETS_SRC))
    from pgml_out.sentiment_demo_pydantic_ai import SentimentExample

    props = SentimentExample.model_json_schema()['properties']
    assert 'IMDB' in props['text']['description'] or 'review' in props['text']['description'].lower()
    assert (
        'positive' in props['sentiment']['description'].lower()
        or 'negative' in props['sentiment']['description'].lower()
    )


@pytest.mark.skipif(
    not all(
        __import__('os').environ.get(k)
        for k in (
            'OPENAI_API_KEY',
            'OPENAI_ENDPOINT',
            'OPENAI_MODEL',
            'OPENAI_API_VERSION',
            'ARGILLA_API_URL',
            'ARGILLA_API_KEY',
        )
    ),
    reason='Live OpenAI + Argilla credentials not configured',
)
def test_run_flywheel_live(demo) -> None:
    summary = demo.run_flywheel(synthesize_count=1, diversify_rounds=0, use_lancedb=True)
    assert summary['n_seeds'] == 8
    assert summary['n_synthetic'] >= 1
    assert summary['n_argilla_records'] == summary['n_labeled']
    assert summary['lancedb_table'] == 'sentiment_examples'
    assert 0.0 <= summary['train_accuracy'] <= 1.0
