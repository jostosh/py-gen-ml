import typing

import py_gen_ml as pgml

from . import flywheel_demo_patch as patch
from . import flywheel_demo_base as base


class ReviewExampleSweep(pgml.Sweeper[patch.ReviewExamplePatch]):
    """
    A single instruction–response example for LLM synthesis and Argilla review.
    """

    id: typing.Optional[pgml.StrSweep] = None
    """Stable identifier stored as Argilla metadata (not a primary UI field)."""

    instruction: typing.Optional[pgml.StrSweep] = None
    """
    User-facing task prompt the model should answer. Clear comments become JSON
    Schema descriptions used by PydanticAI NativeOutput.
    """

    generation: typing.Optional[pgml.StrSweep] = None
    """Complete answer or generation for the instruction."""

    quality: typing.Optional[pgml.StrSweep] = None
    """Human quality judgment for the generation (Argilla LabelQuestion)."""



ReviewExampleSweepField = typing.Union[
    ReviewExampleSweep,
    pgml.NestedChoice[ReviewExampleSweep, patch.ReviewExamplePatch],  # type: ignore
]

