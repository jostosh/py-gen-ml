import typing

import py_gen_ml as pgml

from . import default_patch as patch
from . import default_base as base


class OptimizerSweep(pgml.Sweeper[patch.OptimizerPatch]):
    """Optimizer configuration"""

    type: pgml.StrSweep | None = None
    """Optimizer type"""

    learning_rate: pgml.FloatSweep | None = None
    """Learning rate"""



OptimizerSweepField = typing.Union[
    OptimizerSweep,
    pgml.NestedChoice[OptimizerSweep, patch.OptimizerPatch],  # type: ignore
]

