import typing

import py_gen_ml as pgml

from . import builder_demo_patch as patch
from . import builder_demo_base as base


class LinearSweep(pgml.Sweeper[patch.LinearPatch]):
    """Linear layer configuration"""

    in_features: pgml.IntSweep | None = None
    """Number of input features"""

    out_features: pgml.IntSweep | None = None
    """Number of output features"""

    bias: pgml.BoolSweep | None = None
    """Bias"""


LinearSweepField = typing.Union[
    LinearSweep,
    pgml.NestedChoice[LinearSweep, patch.LinearPatch],  # type: ignore
]


class MLPSweep(pgml.Sweeper[patch.MLPPatch]):
    """MLP configuration"""

    layers: LinearSweepField | None = None
    """Linear layers"""



MLPSweepField = typing.Union[
    MLPSweep,
    pgml.NestedChoice[MLPSweep, patch.MLPPatch],  # type: ignore
]

