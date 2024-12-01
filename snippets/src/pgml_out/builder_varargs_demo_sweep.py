import typing

import py_gen_ml as pgml

from . import builder_varargs_demo_patch as patch
from . import builder_varargs_demo_base as base


class LinearSweep(pgml.Sweeper[patch.LinearPatch]):
    """Linear layer configuration"""

    in_features: typing.Optional[pgml.IntSweep] = None
    """Number of input features"""

    out_features: typing.Optional[pgml.IntSweep] = None
    """Number of output features"""

    bias: typing.Optional[pgml.BoolSweep] = None
    """Bias"""


LinearSweepField = typing.Union[
    LinearSweep,
    pgml.NestedChoice[LinearSweep, patch.LinearPatch],  # type: ignore
]


class MLPSweep(pgml.Sweeper[patch.MLPPatch]):
    """MLP configuration"""

    layers: typing.Optional[LinearSweepField] = None
    """Linear layers"""



MLPSweepField = typing.Union[
    MLPSweep,
    pgml.NestedChoice[MLPSweep, patch.MLPPatch],  # type: ignore
]

