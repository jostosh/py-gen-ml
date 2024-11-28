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

    num_layers: typing.Optional[pgml.IntSweep] = None
    """Number of layers in the MLP."""

    num_units: typing.Optional[pgml.IntSweep] = None
    """Number of units in each layer."""

    activation: typing.Optional[ActivationSweepField] = None
    """Activation function to use."""



MLPParsingDemoSweepField = typing.Union[
    MLPParsingDemoSweep,
    pgml.NestedChoice[MLPParsingDemoSweep, patch.MLPParsingDemoPatch],  # type: ignore
]

