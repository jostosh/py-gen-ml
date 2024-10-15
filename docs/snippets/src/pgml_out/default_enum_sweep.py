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

    in_features: pgml.IntSweep | None = None
    """Number of input features"""

    out_features: pgml.IntSweep | None = None
    """Number of output features"""

    activation: ActivationSweepField | None = None
    """Activation function"""



LinearSweepField = typing.Union[
    LinearSweep,
    pgml.NestedChoice[LinearSweep, patch.LinearPatch],  # type: ignore
]

