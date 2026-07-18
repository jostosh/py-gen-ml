"""Validate the sentiment online loop demo (no live LitServe / Argilla)."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

pytest.importorskip('sklearn')
pytest.importorskip('lancedb')
pytest.importorskip('mlflow')

REPO = Path(__file__).resolve().parents[1]
SNIPPETS_SRC = REPO / 'docs' / 'snippets' / 'src'


@pytest.fixture
def online(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.syspath_prepend(str(SNIPPETS_SRC))
    from snippets import sentiment_online_demo as mod

    return mod


def test_merge_to_feedback(online) -> None:
    from pgml_out.sentiment_demo_litserve import SentimentPrediction

    pred = SentimentPrediction(
        sample_id='s1',
        text='great film',
        sentiment='positive',
        score=0.9,
        model_version='v1',
    )
    fb = online.merge_to_feedback(None, pred)
    assert fb.sample_id == 's1'
    assert fb.predicted_sentiment == 'positive'
    assert fb.sentiment == 'positive'
    assert fb.source == 'model'


def test_apply_human_corrections(online) -> None:
    from pgml_out.sentiment_demo_argilla import SentimentFeedback

    draft = SentimentFeedback(
        sample_id='s1',
        text='meh',
        predicted_sentiment='positive',
        sentiment='positive',
        source='model',
    )
    out = online.apply_human_corrections(
        [draft],
        ground_truth={'s1': 'negative'},
    )
    assert len(out) == 1
    assert out[0].sentiment == 'negative'
    assert out[0].predicted_sentiment == 'positive'
    assert out[0].source == 'human'


def test_score_batch(online, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(SNIPPETS_SRC))

    with patch.object(online, 'log_online_metrics_to_mlflow') as log_m:
        summary = online.score_batch(
            db_uri=str(tmp_path / 'online.lancedb'),
            push_to_argilla=False,
            use_ground_truth=True,
        )

    log_m.assert_called_once()
    assert summary['n_predictions'] >= 4
    assert summary['n_feedback'] == summary['n_predictions']
    assert summary['n_argilla_records'] == summary['n_predictions']
    assert summary['lancedb_predictions'] == 'sentiment_predictions'
    assert summary['lancedb_feedback'] == 'sentiment_feedback'
    assert 0.0 <= summary['agreement_rate'] <= 1.0

    import lancedb

    db = lancedb.connect(summary['db_uri'])
    assert db.open_table('sentiment_predictions').count_rows() == summary['n_predictions']
    assert db.open_table('sentiment_feedback').count_rows() == summary['n_feedback']


def test_log_online_metrics_to_mlflow(online, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(SNIPPETS_SRC))
    with patch('mlflow.set_experiment') as set_exp, patch('mlflow.start_run') as start, patch(
        'pgml_out.sentiment_demo_mlflow.log_sentiment_online_metrics',
    ) as log_m:
        start.return_value.__enter__ = MagicMock(return_value=None)
        start.return_value.__exit__ = MagicMock(return_value=False)
        online.log_online_metrics_to_mlflow(
            n_predictions=2,
            n_feedback=2,
            agreement=1.0,
        )
    set_exp.assert_called_once_with('imdb_sentiment_online')
    log_m.assert_called_once()
