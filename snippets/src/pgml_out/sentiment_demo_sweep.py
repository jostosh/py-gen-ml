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
    pgml.NestedChoice[SentimentMetricsSweep,
                      patch.SentimentMetricsPatch],  # type: ignore
]


class SentimentPredictRequestSweep(pgml.Sweeper[patch.SentimentPredictRequestPatch]):
    """Inference request for the online sentiment classifier."""

    id: typing.Optional[pgml.StrSweep] = None
    """Stable sample id (links prediction and feedback rows)."""

    text: typing.Optional[pgml.StrSweep] = None
    """Review text to classify."""


SentimentPredictRequestSweepField = typing.Union[
    SentimentPredictRequestSweep,
    pgml.NestedChoice[SentimentPredictRequestSweep,
                      patch.SentimentPredictRequestPatch],  # type: ignore
]


class SentimentPredictionSweep(pgml.Sweeper[patch.SentimentPredictionPatch]):
    """
    Model output for one scored review (separate from the labeled training row).
    """

    sample_id: typing.Optional[pgml.StrSweep] = None
    """Sample id matching SentimentPredictRequest.id."""

    text: typing.Optional[pgml.StrSweep] = None
    """Review text that was scored."""

    sentiment: typing.Optional[pgml.StrSweep] = None
    """Predicted sentiment: "negative" or "positive"."""

    score: typing.Optional[pgml.FloatSweep] = None
    """Model confidence for the predicted class."""

    model_version: typing.Optional[pgml.StrSweep] = None
    """Deployed model / pipeline version tag."""


SentimentPredictionSweepField = typing.Union[
    SentimentPredictionSweep,
    pgml.NestedChoice[SentimentPredictionSweep,
                      patch.SentimentPredictionPatch],  # type: ignore
]


class SentimentFeedbackSweep(pgml.Sweeper[patch.SentimentFeedbackPatch]):
    """Human correction / re-label for a scored review."""

    sample_id: typing.Optional[pgml.StrSweep] = None
    """Sample id matching SentimentPrediction.sample_id."""

    text: typing.Optional[pgml.StrSweep] = None
    """Review text shown to the annotator."""

    predicted_sentiment: typing.Optional[pgml.StrSweep] = None
    """Model-predicted sentiment (for comparison; not the Argilla question)."""

    sentiment: typing.Optional[pgml.StrSweep] = None
    """
    Corrected sentiment after review: "negative" or "positive". When logging a draft
    from a prediction, set this to the predicted label so Argilla records it as a
    Suggestion.
    """

    source: typing.Optional[pgml.StrSweep] = None
    """Provenance: "model" for suggestion drafts, "human" after correction."""


SentimentFeedbackSweepField = typing.Union[
    SentimentFeedbackSweep,
    pgml.NestedChoice[SentimentFeedbackSweep,
                      patch.SentimentFeedbackPatch],  # type: ignore
]


class SentimentServeConfigSweep(pgml.Sweeper[patch.SentimentServeConfigPatch]):
    """LitServe / client settings for SentimentClassifier."""

    url: typing.Optional[pgml.StrSweep] = None
    timeout_s: typing.Optional[pgml.FloatSweep] = None
    workers_per_device: typing.Optional[pgml.IntSweep] = None
    accelerator: typing.Optional[pgml.StrSweep] = None


SentimentServeConfigSweepField = typing.Union[
    SentimentServeConfigSweep,
    pgml.NestedChoice[SentimentServeConfigSweep,
                      patch.SentimentServeConfigPatch],  # type: ignore
]


class SentimentOnlineMetricsSweep(pgml.Sweeper[patch.SentimentOnlineMetricsPatch]):
    """Online-loop metrics (predictions vs human feedback)."""

    n_predictions: typing.Optional[pgml.IntSweep] = None
    n_feedback: typing.Optional[pgml.IntSweep] = None
    agreement_rate: typing.Optional[pgml.FloatSweep] = None



SentimentOnlineMetricsSweepField = typing.Union[
    SentimentOnlineMetricsSweep,
    pgml.NestedChoice[SentimentOnlineMetricsSweep, patch.SentimentOnlineMetricsPatch],  # type: ignore
]

