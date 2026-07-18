"""Sentiment flywheel demo: IMDB seeds → synthesize → Argilla HITL → train.

Run from ``docs/snippets`` after codegen::

    uv sync --extra bridges --extra pydantic-ai --extra argilla --extra lancedb

    export OPENAI_API_KEY=...
    export OPENAI_ENDPOINT=https://YOUR_RESOURCE.openai.azure.com/
    export OPENAI_MODEL=gpt-4o
    export OPENAI_API_VERSION=2024-12-01-preview

    # optional: log records to a live Argilla server
    # export ARGILLA_API_URL=...
    # export ARGILLA_API_KEY=...

    uv run python -m snippets.sentiment_flywheel_demo
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import List, Sequence

import argilla as rg
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.azure import AzureProvider

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
from py_gen_ml.bridges.lancedb_rows import append_feature_rows
from py_gen_ml.bridges.synthesis_argilla import synthetic_rows_to_argilla_records

# .../docs/snippets/src/snippets/this_file.py → parents[2] == docs/snippets
SNIPPETS_ROOT = Path(__file__).resolve().parents[2]
SEEDS_PATH = SNIPPETS_ROOT / 'data' / 'imdb_sentiment_seeds.json'

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


def openai_model_from_env() -> OpenAIChatModel:
    """Build an OpenAI chat model from endpoint, key, model name, and API version."""
    return OpenAIChatModel(
        os.environ['OPENAI_MODEL'],
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


def train_sentiment_classifier(rows: Sequence[SentimentExample]) -> dict:
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
        test_size=0.25,
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


def run_flywheel(
    *,
    synthesize_count: int = 4,
    diversify_rounds: int = 1,
    use_lancedb: bool = True,
    push_to_argilla: bool = True,
) -> dict:
    """End-to-end: seeds → OpenAI synthesis → Argilla HITL → optional LanceDB → train."""
    seeds = load_imdb_seeds()
    synthetic = synthesize_sentiment_example_sync(
        model=openai_model_from_env(),
        system_prompt=SYSTEM_PROMPT,
        count=synthesize_count,
        examples=[
            SentimentExamplePartial.model_validate(s.model_dump()) for s in seeds
        ],
        diversify_rounds=diversify_rounds,
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
        'openai_model': os.environ['OPENAI_MODEL'],
    }

    if use_lancedb:
        with tempfile.TemporaryDirectory() as tmp:
            table_name = persist_to_lancedb(labeled, tmp)
            result['lancedb_table'] = table_name

    metrics = train_sentiment_classifier(labeled)
    result['train_accuracy'] = metrics['accuracy']
    result['n_train'] = metrics['n_train']
    result['n_test'] = metrics['n_test']
    return result


if __name__ == '__main__':
    summary = run_flywheel()
    print(json.dumps({k: v for k, v in summary.items() if k != 'pipeline'}, indent=2))
