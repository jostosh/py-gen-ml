import typing

import py_gen_ml as pgml

from . import builder_custom_class_demo_patch as patch
from . import builder_custom_class_demo_base as base


class LinearBlockSweep(pgml.Sweeper[patch.LinearBlockPatch]):
    """Linear block configuration"""

    in_features: typing.Optional[pgml.IntSweep] = None
    """Number of input features"""

    out_features: typing.Optional[pgml.IntSweep] = None
    """Number of output features"""

    bias: typing.Optional[pgml.BoolSweep] = None
    """Bias"""

    dropout: typing.Optional[pgml.FloatSweep] = None
    """Dropout probability"""

    activation: typing.Optional[pgml.StrSweep] = None
    """Activation function"""


LinearBlockSweepField = typing.Union[
    LinearBlockSweep,
    pgml.NestedChoice[LinearBlockSweep, patch.LinearBlockPatch],  # type: ignore
]


class MLPSweep(pgml.Sweeper[patch.MLPPatch]):
    """MLP configuration"""

    layers: typing.Optional[LinearBlockSweepField] = None
    """Linear blocks"""



MLPSweepField = typing.Union[
    MLPSweep,
    pgml.NestedChoice[MLPSweep, patch.MLPPatch],  # type: ignore
]

