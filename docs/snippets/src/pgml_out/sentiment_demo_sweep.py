import typing

import py_gen_ml as pgml

from . import sentiment_demo_patch as patch
from . import sentiment_demo_base as base


class SentimentExampleSweep(pgml.Sweeper[patch.SentimentExamplePatch]):
    """
    Labeled movie-review example for sentiment classification. Field comments become
    JSON Schema descriptions for PydanticAI NativeOutput.
    """

    id: typing.Optional[pgml.StrSweep] = None
    """Stable row id (Argilla metadata; not a primary UI field)."""

    source: typing.Optional[pgml.StrSweep] = None
    """
    Provenance of the row: "imdb" for seed reviews, "synthetic" for LLM-generated
    ones.
    """

    text: typing.Optional[pgml.StrSweep] = None
    """
    Full movie-review text in the style of IMDB user reviews (may include spoilers,
    informal tone, and mixed praise/criticism). Used as the classifier input.
    """

    sentiment: typing.Optional[pgml.StrSweep] = None
    """Binary sentiment of the review: "negative" or "positive"."""


SentimentExampleSweepField = typing.Union[
    SentimentExampleSweep,
    pgml.NestedChoice[SentimentExampleSweep,
                      patch.SentimentExamplePatch],  # type: ignore
]


class SentimentTrainConfigSweep(pgml.Sweeper[patch.SentimentTrainConfigPatch]):
    """Hyperparameters for a sentiment flywheel training run."""

    run_name: typing.Optional[pgml.StrSweep] = None
    """Human-readable run name (logged as a tracker tag)."""

    synthesize_count: typing.Optional[pgml.IntSweep] = None
    """Number of synthetic examples requested per diversify round."""

    diversify_rounds: typing.Optional[pgml.IntSweep] = None
    """Extra synthesis rounds that feed prior outputs back as examples."""

    openai_model: typing.Optional[pgml.StrSweep] = None
    """OpenAI / Azure deployment name used for synthesis."""

    test_size: typing.Optional[pgml.FloatSweep] = None
    """TF-IDF + logistic regression holdout fraction."""


SentimentTrainConfigSweepField = typing.Union[
    SentimentTrainConfigSweep,
    pgml.NestedChoice[SentimentTrainConfigSweep,
                      patch.SentimentTrainConfigPatch],  # type: ignore
]


class SentimentMetricsSweep(pgml.Sweeper[patch.SentimentMetricsPatch]):
    """Holdout metrics from the sentiment classifier."""

    accuracy: typing.Optional[pgml.FloatSweep] = None
    n_train: typing.Optional[pgml.IntSweep] = None
    n_test: typing.Optional[pgml.IntSweep] = None
    n_labeled: typing.Optional[pgml.IntSweep] = None



SentimentMetricsSweepField = typing.Union[
    SentimentMetricsSweep,
    pgml.NestedChoice[SentimentMetricsSweep, patch.SentimentMetricsPatch],  # type: ignore
]

