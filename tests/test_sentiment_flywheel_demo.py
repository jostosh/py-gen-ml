"""Validate the IMDB sentiment flywheel demo helpers (no live API calls)."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

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
    monkeypatch.setenv('OPENAI_API_VERSION', '2024-12-01-preview')
    monkeypatch.delenv('OPENAI_MODEL', raising=False)
    model = demo.openai_model_from_env(model='gpt-4o')
    assert model.model_name == 'gpt-4o'


def test_train_config_from_yaml_and_cli(demo, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(SNIPPETS_SRC))
    from pgml_out.sentiment_demo_base import SentimentTrainConfig
    from pgml_out.sentiment_demo_cli_args import SentimentTrainConfigArgs

    config = SentimentTrainConfig.from_yaml_files([str(demo.DEFAULT_CONFIG_PATH)])
    assert config.synthesize_count == 4
    assert config.openai_model == 'gpt-4o'
    patched = config.apply_cli_args(
        SentimentTrainConfigArgs(synthesize_count=2, run_name='cli-run'),
    )
    assert patched.synthesize_count == 2
    assert patched.run_name == 'cli-run'
    assert patched.openai_model == 'gpt-4o'


def test_json_schema_descriptions_present(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(SNIPPETS_SRC))
    from pgml_out.sentiment_demo_pydantic_ai import SentimentExample

    props = SentimentExample.model_json_schema()['properties']
    assert 'IMDB' in props['text']['description'] or 'review' in props['text']['description'].lower()
    assert (
        'positive' in props['sentiment']['description'].lower() or
        'negative' in props['sentiment']['description'].lower()
    )


def test_log_training_to_mlflow(demo, monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip('mlflow')
    monkeypatch.syspath_prepend(str(SNIPPETS_SRC))
    from pgml_out.sentiment_demo_base import SentimentTrainConfig
    from pgml_out.sentiment_demo_mlflow import SentimentMetrics

    config = SentimentTrainConfig(
        run_name='t',
        synthesize_count=1,
        diversify_rounds=0,
        openai_model='gpt-4o',
        test_size=0.25,
    )
    metrics = SentimentMetrics(accuracy=1.0, n_train=4, n_test=1, n_labeled=5)

    with patch('pgml_out.sentiment_demo_mlflow.start_sentiment_train_config_run') as start, patch(
        'pgml_out.sentiment_demo_mlflow.log_sentiment_metrics',
    ) as log_m:
        start.return_value.__enter__ = MagicMock(return_value=None)
        start.return_value.__exit__ = MagicMock(return_value=False)
        demo.log_training_to_mlflow(train_config=config, metrics=metrics)
    start.assert_called_once()
    log_m.assert_called_once_with(metrics)


@pytest.mark.skipif(
    not all(
        __import__('os').environ.get(k) for k in (
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
    from pgml_out.sentiment_demo_base import SentimentTrainConfig

    summary = demo.run_flywheel(
        SentimentTrainConfig(
            run_name='live',
            synthesize_count=1,
            diversify_rounds=0,
            openai_model=__import__('os').environ['OPENAI_MODEL'],
            test_size=0.25,
        ),
        use_lancedb=True,
    )
    assert summary['n_seeds'] == 8
    assert summary['n_synthetic'] >= 1
    assert summary['n_argilla_records'] == summary['n_labeled']
    assert summary['lancedb_table'] == 'sentiment_examples'
    assert 0.0 <= summary['train_accuracy'] <= 1.0
