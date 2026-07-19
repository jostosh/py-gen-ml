import typing

import py_gen_ml as pgml

from . import quickstart_b_patch as patch
from . import quickstart_b_base as base


class MLPQuickstartSweep(pgml.Sweeper[patch.MLPQuickstartPatch]):
    """Multi-layer perceptron configuration"""

    num_layers: typing.Optional[pgml.IntSweep] = None
    """Number of layers"""

    num_units: typing.Optional[pgml.IntSweep] = None
    """Number of units"""

    activation: typing.Optional[pgml.StrSweep] = None
    """Activation function"""



MLPQuickstartSweepField = typing.Union[
    MLPQuickstartSweep,
    pgml.NestedChoice[MLPQuickstartSweep, patch.MLPQuickstartPatch],  # type: ignore
]

