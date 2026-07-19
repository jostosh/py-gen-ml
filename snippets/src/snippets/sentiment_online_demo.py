"""Sentiment online loop: feature → LitServe → prediction → feedback → store / track.

Run from ``docs/snippets`` after codegen::

    uv sync --extra bridges --extra lancedb --extra argilla --extra litserve --extra mlflow

    # optional live Argilla for HITL push
    # export ARGILLA_API_URL=...
    # export ARGILLA_API_KEY=...

    # CI-friendly batch (no long-running server):
    uv run python -m snippets.sentiment_online_demo score-batch

    # Live LitServe:
    uv run python -m snippets.sentiment_online_demo serve
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import typer

from snippets.sentiment_flywheel_demo import (
    SEEDS_PATH,
    argilla_client_from_env,
    load_imdb_seeds,
    train_sentiment_classifier,
)

MODEL_VERSION = 'tfidf-logreg-v1'

app = typer.Typer(pretty_exceptions_enable=False)


def fit_pipeline_from_seeds(path: Path = SEEDS_PATH) -> Any:
    """Fit TF–IDF + LogReg on bundled IMDB seeds; return the sklearn pipeline."""
    seeds = load_imdb_seeds(path)
    metrics = train_sentiment_classifier(seeds, test_size=0.25)
    return metrics['pipeline']


def predict_sentiment(
    pipeline: Any,
    *,
    sample_id: str,
    text: str,
    model_version: str = MODEL_VERSION,
) -> Any:
    """Score one review; return a LitServe ``SentimentPrediction``."""
    from pgml_out.sentiment_demo_litserve import SentimentPrediction

    label = str(pipeline.predict([text])[0])
    proba = pipeline.predict_proba([text])[0]
    classes = list(pipeline.classes_)
    score = float(proba[classes.index(label)])
    return SentimentPrediction(
        sample_id=sample_id,
        text=text,
        sentiment=label,
        score=score,
        model_version=model_version,
    )


def merge_to_feedback(_request: Any, prediction: Any) -> Any:
    """Build a ``SentimentFeedback`` draft (predicted label as Argilla suggestion)."""
    from pgml_out.sentiment_demo_argilla import SentimentFeedback

    return SentimentFeedback(
        sample_id=prediction.sample_id,
        text=prediction.text,
        predicted_sentiment=prediction.sentiment,
        sentiment=prediction.sentiment,
        source='model',
    )


def apply_human_corrections(
    drafts: Sequence[Any],
    *,
    ground_truth: Optional[Dict[str, str]] = None,
) -> List[Any]:
    """Simulate HITL: set ``source=human`` and optionally override ``sentiment``.

    When ``ground_truth`` maps ``sample_id → label``, use that as the corrected
    label (demo / tests). Otherwise keep the predicted suggestion as the response.
    """
    from pgml_out.sentiment_demo_argilla import SentimentFeedback

    out: List[Any] = []
    for draft in drafts:
        corrected = (
            ground_truth.get(draft.sample_id, draft.sentiment)
            if ground_truth is not None
            else draft.sentiment
        )
        out.append(
            SentimentFeedback(
                sample_id=draft.sample_id,
                text=draft.text,
                predicted_sentiment=draft.predicted_sentiment,
                sentiment=corrected,
                source='human',
            ),
        )
    return out


def ensure_tables(db: Any) -> Tuple[Any, Any]:
    """Create (or open) prediction and feedback LanceDB tables."""
    from pgml_out.sentiment_demo_lancedb import (
        create_sentiment_feedback_table,
        create_sentiment_prediction_table,
    )

    return (
        create_sentiment_prediction_table(db, mode='overwrite', exist_ok=False),
        create_sentiment_feedback_table(db, mode='overwrite', exist_ok=False),
    )


def build_feedback_records(
    requests: Sequence[Any],
    predictions: Sequence[Any],
) -> Tuple[List[Any], List[Any]]:
    """Merge each request/prediction into a feedback draft and Argilla record."""
    from pgml_out.sentiment_demo_argilla import to_sentiment_feedback_record
    from py_gen_ml.bridges import log_prediction_for_review

    drafts: List[Any] = []
    records: List[Any] = []
    for req, pred in zip(requests, predictions):
        draft = merge_to_feedback(req, pred)
        drafts.append(draft)
        records.append(
            log_prediction_for_review(
                req,
                pred,
                merge=merge_to_feedback,
                to_record=to_sentiment_feedback_record,
            ),
        )
    return drafts, records


def push_feedback_argilla(*, records: Sequence[Any]) -> str:
    """Create (or reuse) the feedback dataset and log ``records``."""
    import argilla as rg
    from pgml_out.sentiment_demo_argilla import (
        build_sentiment_feedback_settings,
        sentiment_feedback_dataset_name,
    )

    name = sentiment_feedback_dataset_name()
    client = argilla_client_from_env()
    settings = build_sentiment_feedback_settings(client=client)
    dataset = client.datasets(name=name)
    if dataset is None:
        dataset = rg.Dataset(name=name, settings=settings, client=client)
        dataset.create()
    dataset.records.log(list(records))
    return name


def log_online_metrics_to_mlflow(
    *,
    n_predictions: int,
    n_feedback: int,
    agreement: float,
) -> None:
    """Log ``SentimentOnlineMetrics`` under a short-lived MLflow run."""
    import mlflow
    from pgml_out.sentiment_demo_mlflow import (
        SentimentOnlineMetrics,
        log_sentiment_online_metrics,
    )

    metrics = SentimentOnlineMetrics(
        n_predictions=n_predictions,
        n_feedback=n_feedback,
        agreement_rate=agreement,
    )
    mlflow.set_experiment('imdb_sentiment_online')
    with mlflow.start_run(run_name='online-batch'):
        log_sentiment_online_metrics(metrics)


def score_batch(
    *,
    db_uri: Optional[str] = None,
    push_to_argilla: bool = False,
    use_ground_truth: bool = True,
) -> dict:
    """Offline online-loop: fit → predict seeds → store → feedback → track."""
    import lancedb
    from pgml_out.sentiment_demo_lancedb import (
        SentimentFeedback as LanceFeedback,
        SentimentPrediction as LancePrediction,
        sentiment_feedback_merge_on,
        sentiment_prediction_merge_on,
    )
    from pgml_out.sentiment_demo_litserve import SentimentPredictRequest
    from pgml_out.sentiment_demo_argilla import sentiment_feedback_dataset_name
    from py_gen_ml.bridges import merge_rows

    seeds = load_imdb_seeds()
    pipeline = fit_pipeline_from_seeds()

    requests = [
        SentimentPredictRequest(id=s.id, text=s.text) for s in seeds
    ]
    predictions = [
        predict_sentiment(pipeline, sample_id=req.id, text=req.text) for req in requests
    ]
    drafts, records = build_feedback_records(requests, predictions)
    ground_truth = {s.id: s.sentiment for s in seeds} if use_ground_truth else None
    feedbacks = apply_human_corrections(drafts, ground_truth=ground_truth)

    dataset_name = sentiment_feedback_dataset_name()
    if push_to_argilla:
        dataset_name = push_feedback_argilla(records=records)

    owns_tmp = db_uri is None
    tmp_ctx = tempfile.TemporaryDirectory() if owns_tmp else None
    try:
        uri = db_uri if db_uri is not None else tmp_ctx.name  # type: ignore[union-attr]
        db = lancedb.connect(uri)
        pred_table, fb_table = ensure_tables(db)
        merge_rows(
            pred_table,
            [LancePrediction.model_validate(p.model_dump()) for p in predictions],
            on=sentiment_prediction_merge_on(),
        )
        merge_rows(
            fb_table,
            [LanceFeedback.model_validate(f.model_dump()) for f in feedbacks],
            on=sentiment_feedback_merge_on(),
        )
        pred_by_id = {p.sample_id: p.sentiment for p in predictions}
        matched = sum(1 for f in feedbacks if pred_by_id.get(f.sample_id) == f.sentiment)
        agreement = matched / len(feedbacks) if feedbacks else 0.0
        log_online_metrics_to_mlflow(
            n_predictions=len(predictions),
            n_feedback=len(feedbacks),
            agreement=agreement,
        )
        return {
            'n_predictions': len(predictions),
            'n_feedback': len(feedbacks),
            'n_argilla_records': len(records),
            'argilla_dataset': dataset_name,
            'agreement_rate': agreement,
            'lancedb_predictions': 'sentiment_predictions',
            'lancedb_feedback': 'sentiment_feedback',
            'mlflow_experiment': 'imdb_sentiment_online',
            'model_version': MODEL_VERSION,
            'db_uri': uri if not owns_tmp else None,
        }
    finally:
        if tmp_ctx is not None:
            tmp_ctx.cleanup()


@app.command('score-batch')
def score_batch_cmd(
    push_to_argilla: bool = typer.Option(False, help='Push feedback drafts to Argilla'),
    db_uri: Optional[str] = typer.Option(None, help='LanceDB URI (temp dir if omitted)'),
) -> None:
    """Run the online loop offline over seed texts (CI-friendly)."""
    summary = score_batch(db_uri=db_uri, push_to_argilla=push_to_argilla)
    print(json.dumps(summary, indent=2))


@app.command('serve')
def serve_cmd(
    port: int = typer.Option(8000, help='LitServe port'),
    db_uri: str = typer.Option('./sentiment_online.lancedb', help='LanceDB URI'),
) -> None:
    """Fit on seeds and serve ``SentimentClassifier`` via LitServe."""
    import lancedb
    from pgml_out.sentiment_demo_base import SentimentServeConfig
    from pgml_out.sentiment_demo_lancedb import (
        SentimentPrediction as LancePrediction,
        sentiment_prediction_merge_on,
    )
    from pgml_out.sentiment_demo_litserve import (
        SentimentPredictRequest,
        create_sentiment_classifier_server,
    )
    from py_gen_ml.bridges import merge_rows

    pipeline = fit_pipeline_from_seeds()
    db = lancedb.connect(db_uri)
    pred_table, _fb_table = ensure_tables(db)

    def predict(request: SentimentPredictRequest):
        prediction = predict_sentiment(
            pipeline,
            sample_id=request.id,
            text=request.text,
        )
        merge_rows(
            pred_table,
            [LancePrediction.model_validate(prediction.model_dump())],
            on=sentiment_prediction_merge_on(),
        )
        return prediction

    server = create_sentiment_classifier_server(
        predict=predict,
        config=SentimentServeConfig(
            accelerator='cpu',
            workers_per_device=1,
            timeout_s=30.0,
            url=f'http://127.0.0.1:{port}',
        ),
    )
    server.run(host='127.0.0.1', port=port, generate_client_file=False)


if __name__ == '__main__':
    app()
