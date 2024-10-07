import typing

import py_gen_ml as pgml

from . import proto_intro_patch as patch
from . import proto_intro_base as base


class MLPSweep(pgml.Sweeper[patch.MLPPatch]):
    """Multi-layer perceptron configuration"""

    num_layers: pgml.IntSweep | None = None
    """Number of layers"""

    num_units: pgml.IntSweep | None = None
    """Number of units"""

    activation: pgml.StrSweep | None = None
    """Activation function"""



MLPSweepField = typing.Union[
    MLPSweep,
    pgml.NestedChoice[MLPSweep, patch.MLPPatch],  # type: ignore
]

