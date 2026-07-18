import typing

import py_gen_ml as pgml

from . import bentoml_demo_patch as patch
from . import bentoml_demo_base as base


class PredictRequestSweep(pgml.Sweeper[patch.PredictRequestPatch]):
    """Inference request features."""

    features: typing.Optional[pgml.FloatSweep] = None


PredictRequestSweepField = typing.Union[
    PredictRequestSweep,
    pgml.NestedChoice[PredictRequestSweep, patch.PredictRequestPatch],  # type: ignore
]


class PredictResponseSweep(pgml.Sweeper[patch.PredictResponsePatch]):
    """Model prediction for a request."""

    label: typing.Optional[pgml.IntSweep] = None
    score: typing.Optional[pgml.FloatSweep] = None


PredictResponseSweepField = typing.Union[
    PredictResponseSweep,
    pgml.NestedChoice[PredictResponseSweep, patch.PredictResponsePatch],  # type: ignore
]


class ClassifierServeConfigSweep(pgml.Sweeper[patch.ClassifierServeConfigPatch]):
    """Serve / client settings for Classifier."""

    url: typing.Optional[pgml.StrSweep] = None
    workers: typing.Optional[pgml.IntSweep] = None
    timeout_s: typing.Optional[pgml.FloatSweep] = None



ClassifierServeConfigSweepField = typing.Union[
    ClassifierServeConfigSweep,
    pgml.NestedChoice[ClassifierServeConfigSweep, patch.ClassifierServeConfigPatch],  # type: ignore
]

