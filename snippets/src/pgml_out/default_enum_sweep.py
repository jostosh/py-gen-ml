import typing

import py_gen_ml as pgml

from . import default_enum_patch as patch
from . import default_enum_base as base

ActivationSweepField = typing.Union[
    pgml.Choice[base.Activation],
    typing.Literal['any'],
    base.Activation,
]


class LinearSweep(pgml.Sweeper[patch.LinearPatch]):
    """Linear layer"""

    in_features: typing.Optional[pgml.IntSweep] = None
    """Number of input features"""

    out_features: typing.Optional[pgml.IntSweep] = None
    """Number of output features"""

    activation: typing.Optional[ActivationSweepField] = None
    """Activation function"""



LinearSweepField = typing.Union[
    LinearSweep,
    pgml.NestedChoice[LinearSweep, patch.LinearPatch],  # type: ignore
]

