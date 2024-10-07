import typing

import py_gen_ml as pgml

from . import advanced_patch as patch
from . import advanced_base as base


class LinearBlockSweep(pgml.Sweeper[patch.LinearBlockPatch]):
    """Linear block configuration"""

    num_units: pgml.IntSweep | None = None
    """Number of units"""

    activation: pgml.StrSweep | None = None
    """Activation function"""



LinearBlockSweepField = typing.Union[
    LinearBlockSweep,
    pgml.NestedChoice[LinearBlockSweep, patch.LinearBlockPatch],  # type: ignore
]


class OptimizerSweep(pgml.Sweeper[patch.OptimizerPatch]):
    """Optimizer configuration"""

    type: pgml.StrSweep | None = None
    """Type of optimizer"""

    learning_rate: pgml.FloatSweep | None = None
    """Learning rate"""



OptimizerSweepField = typing.Union[
    OptimizerSweep,
    pgml.NestedChoice[OptimizerSweep, patch.OptimizerPatch],  # type: ignore
]


class MLPSweep(pgml.Sweeper[patch.MLPPatch]):
    """Multi-layer perceptron configuration"""

    layers: LinearBlockSweepField | None = None
    """List of linear blocks"""



MLPSweepField = typing.Union[
    MLPSweep,
    pgml.NestedChoice[MLPSweep, patch.MLPPatch],  # type: ignore
]


class TrainingSweep(pgml.Sweeper[patch.TrainingPatch]):
    """Training configuration"""

    mlp: MLPSweepField | None = None
    """Multi-layer perceptron configuration"""

    optimizer: OptimizerSweepField | None = None
    """Optimizer configuration"""



TrainingSweepField = typing.Union[
    TrainingSweep,
    pgml.NestedChoice[TrainingSweep, patch.TrainingPatch],  # type: ignore
]

