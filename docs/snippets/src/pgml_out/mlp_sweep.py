import typing

import py_gen_ml as pgml

from . import mlp_patch as patch
from . import mlp_base as base

ActivationSweepField = typing.Union[
    pgml.Choice[base.Activation],
    typing.Literal['any'],
    base.Activation,
]


class MLPParsingDemoSweep(pgml.Sweeper[patch.MLPParsingDemoPatch]):
    """MLP is a simple multi-layer perceptron."""

    num_layers: pgml.IntSweep | None = None
    """Number of layers in the MLP."""

    num_units: pgml.IntSweep | None = None
    """Number of units in each layer."""

    activation: ActivationSweepField | None = None
    """Activation function to use."""



MLPParsingDemoSweepField = typing.Union[
    MLPParsingDemoSweep,
    pgml.NestedChoice[MLPParsingDemoSweep, patch.MLPParsingDemoPatch],  # type: ignore
]

