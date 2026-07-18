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
    pgml.NestedChoice[SentimentExampleSweep, patch.SentimentExamplePatch],  # type: ignore
]

