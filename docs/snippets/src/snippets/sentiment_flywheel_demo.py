"""Sentiment flywheel demo: IMDB seeds → synthesize → Argilla HITL → train + MLflow.

Run from ``docs/snippets`` after codegen::

    uv sync --extra bridges --extra pydantic-ai --extra argilla --extra lancedb --extra mlflow

    export OPENAI_API_KEY=...
    export OPENAI_ENDPOINT=https://YOUR_RESOURCE.openai.azure.com/
    export OPENAI_API_VERSION=2024-12-01-preview

    # optional: log records to a live Argilla server
    # export ARGILLA_API_URL=...
    # export ARGILLA_API_KEY=...

    uv run python -m snippets.sentiment_flywheel_demo \\
      --config-paths configs/base/sentiment_train_config.yaml

    # override fields via generated CLI flags (same as CIFAR):
    #   --synthesize-count 2 --openai-model gpt-4o --run-name my-run
"""
import json
import os
import tempfile
from pathlib import Path
from typing import List, Optional, Sequence

import argilla as rg
import pgml_out.sentiment_demo_base as base
import pgml_out.sentiment_demo_cli_args as cli_args
import typer
from pgml_out.sentiment_demo_argilla import (
    build_sentiment_example_settings,
    sentiment_example_dataset_name,
    to_sentiment_example_record,
)
from pgml_out.sentiment_demo_lancedb import (
    SentimentExample as LanceSentimentExample,
    create_sentiment_example_table,
    sentiment_example_table_name,
)
from pgml_out.sentiment_demo_pydantic_ai import (
    SentimentExample,
    SentimentExamplePartial,
    synthesize_sentiment_example_sync,
)
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.azure import AzureProvider

import py_gen_ml as pgml
from py_gen_ml.bridges.lancedb_rows import append_feature_rows
from py_gen_ml.bridges.synthesis_argilla import synthetic_rows_to_argilla_records

# .../docs/snippets/src/snippets/this_file.py → parents[2] == docs/snippets
SNIPPETS_ROOT = Path(__file__).resolve().parents[2]
SEEDS_PATH = SNIPPETS_ROOT / 'data' / 'imdb_sentiment_seeds.json'
DEFAULT_CONFIG_PATH = SNIPPETS_ROOT / 'configs' / 'base' / 'sentiment_train_config.yaml'

SYSTEM_PROMPT = """\
You generate realistic IMDB-style movie reviews for binary sentiment classification.
Each example must include:
- text: a short user review (1-4 sentences, informal, specific to a fictional film)
- sentiment: exactly "positive" or "negative"
- source: always "synthetic"
- id: a unique string like "synth-001"
Match the tone and length of the few-shot IMDB seeds. Prefer diversity across genres,
tone, and vocabulary. Do not copy seed text verbatim.
"""

app = typer.Typer(pretty_exceptions_enable=False)


def openai_model_from_env(*, model: Optional[str] = None) -> OpenAIChatModel:
    """Build an OpenAI chat model from endpoint, key, API version, and model name.

    ``model`` comes from ``SentimentTrainConfig.openai_model`` when running the
    flywheel; otherwise ``OPENAI_MODEL`` is required.
    """
    return OpenAIChatModel(
        model if model is not None else os.environ['OPENAI_MODEL'],
        provider=AzureProvider(
            azure_endpoint=os.environ['OPENAI_ENDPOINT'],
            api_version=os.environ['OPENAI_API_VERSION'],
            api_key=os.environ['OPENAI_API_KEY'],
        ),
    )


def argilla_client_from_env() -> rg.Argilla:
    """Build an Argilla client from ``ARGILLA_API_URL`` / ``ARGILLA_API_KEY``."""
    return rg.Argilla(
        api_url=os.environ['ARGILLA_API_URL'],
        api_key=os.environ['ARGILLA_API_KEY'],
    )


def load_imdb_seeds(path: Path = SEEDS_PATH) -> List[SentimentExample]:
    """Load bundled IMDB-style seed reviews as full ``SentimentExample`` rows."""
    raw = json.loads(path.read_text())
    return [SentimentExample.model_validate(row) for row in raw]


def push_argilla_dataset(
    *,
    client: rg.Argilla,
    settings: rg.Settings,
    records: Sequence[rg.Record],
) -> rg.Dataset:
    """Create (or reuse) the Argilla dataset and log ``records`` as suggestions."""
    name = sentiment_example_dataset_name()
    dataset = client.datasets(name=name)
    if dataset is None:
        dataset = rg.Dataset(name=name, settings=settings, client=client)
        dataset.create()
    dataset.records.log(list(records))
    return dataset


def train_sentiment_classifier(
    rows: Sequence[SentimentExample],
    *,
    test_size: float = 0.25,
) -> dict:
    """Train a small TF-IDF + logistic regression sentiment model.

    Returns accuracy on a simple holdout split.
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import Pipeline

    texts = [r.text for r in rows]
    labels = [r.sentiment for r in rows]
    x_train, x_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=test_size,
        random_state=42,
        stratify=labels if len(set(labels)) > 1 else None,
    )
    pipe = Pipeline(
        [
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
            ('clf', LogisticRegression(max_iter=1000)),
        ],
    )
    pipe.fit(x_train, y_train)
    pred = pipe.predict(x_test)
    return {
        'n_train': len(x_train),
        'n_test': len(x_test),
        'accuracy': float(accuracy_score(y_test, pred)),
        'pipeline': pipe,
    }


def persist_to_lancedb(rows: Sequence[SentimentExample], db_uri: str) -> str:
    """Write examples to a local LanceDB table; return table name."""
    import lancedb

    db = lancedb.connect(db_uri)
    table_name = sentiment_example_table_name()
    lance_rows = [LanceSentimentExample.model_validate(r.model_dump()) for r in rows]
    try:
        db.drop_table(table_name)
    except Exception:
        pass
    table = create_sentiment_example_table(db)
    append_feature_rows(table, lance_rows)
    return table_name


def log_training_to_mlflow(*, train_config: base.SentimentTrainConfig, metrics) -> None:
    """Log ``SentimentTrainConfig`` + ``SentimentMetrics`` to MLflow."""
    from pgml_out.sentiment_demo_mlflow import (
        SentimentTrainConfig as MlflowTrainConfig,
        log_sentiment_metrics,
        start_sentiment_train_config_run,
    )

    mlflow_config = MlflowTrainConfig.model_validate(train_config.model_dump())
    with start_sentiment_train_config_run(mlflow_config):
        log_sentiment_metrics(metrics)


def run_flywheel(
    train_config: base.SentimentTrainConfig,
    *,
    use_lancedb: bool = True,
    push_to_argilla: bool = True,
) -> dict:
    """End-to-end: seeds → OpenAI synthesis → Argilla HITL → LanceDB → train + MLflow."""
    from pgml_out.sentiment_demo_mlflow import SentimentMetrics

    seeds = load_imdb_seeds()
    synthetic = synthesize_sentiment_example_sync(
        model=openai_model_from_env(model=train_config.openai_model),
        system_prompt=SYSTEM_PROMPT,
        count=train_config.synthesize_count,
        examples=[
            SentimentExamplePartial.model_validate(s.model_dump()) for s in seeds
        ],
        diversify_rounds=train_config.diversify_rounds,
    )
    # Until humans respond in Argilla, train on model-suggested labels.
    # After HITL, replace with labels from Argilla responses.
    labeled = list(seeds) + list(synthetic)

    client = argilla_client_from_env()
    settings = build_sentiment_example_settings(client=client)
    records = synthetic_rows_to_argilla_records(
        labeled,
        to_record=to_sentiment_example_record,
    )
    if push_to_argilla:
        push_argilla_dataset(client=client, settings=settings, records=records)

    result: dict = {
        'n_seeds': len(seeds),
        'n_synthetic': len(synthetic),
        'n_labeled': len(labeled),
        'n_argilla_records': len(records),
        'n_settings_fields': len(settings.fields),
        'n_settings_questions': len(settings.questions),
        'argilla_dataset': sentiment_example_dataset_name(),
        'openai_model': train_config.openai_model,
        'run_name': train_config.run_name,
    }

    if use_lancedb:
        with tempfile.TemporaryDirectory() as tmp:
            table_name = persist_to_lancedb(labeled, tmp)
            result['lancedb_table'] = table_name

    train_metrics = train_sentiment_classifier(
        labeled,
        test_size=train_config.test_size,
    )
    result['train_accuracy'] = train_metrics['accuracy']
    result['n_train'] = train_metrics['n_train']
    result['n_test'] = train_metrics['n_test']

    metrics = SentimentMetrics(
        accuracy=train_metrics['accuracy'],
        n_train=train_metrics['n_train'],
        n_test=train_metrics['n_test'],
        n_labeled=len(labeled),
    )
    log_training_to_mlflow(train_config=train_config, metrics=metrics)
    result['mlflow_experiment'] = 'imdb_sentiment'
    return result


@pgml.pgml_cmd(app=app)
def main(
    config_paths: List[str] = typer.Option(
        default_factory=lambda: [str(DEFAULT_CONFIG_PATH)],
        help='Paths to SentimentTrainConfig YAML files',
    ),
    cli_args: cli_args.SentimentTrainConfigArgs = typer.Option(...),
    use_lancedb: bool = typer.Option(True, help='Write labeled rows to a temp LanceDB'),
    push_to_argilla: bool = typer.Option(True, help='Push records to Argilla'),
) -> None:
    train_config = base.SentimentTrainConfig.from_yaml_files(config_paths)
    train_config = train_config.apply_cli_args(cli_args)
    summary = run_flywheel(
        train_config,
        use_lancedb=use_lancedb,
        push_to_argilla=push_to_argilla,
    )
    print(json.dumps({k: v for k, v in summary.items() if k != 'pipeline'}, indent=2))


if __name__ == '__main__':
    app()
