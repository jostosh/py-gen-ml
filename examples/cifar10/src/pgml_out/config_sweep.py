import typing

import py_gen_ml as pgml

from . import config_patch as patch
from . import config_base as base

ActivationSweepField = typing.Union[
    pgml.Choice[base.Activation],
    typing.Literal['any'],
    base.Activation,
]


class OptimizerSweep(pgml.Sweeper[patch.OptimizerPatch]):
    """Optimizer configuration"""

    learning_rate: pgml.FloatSweep | None = None
    """Learning rate"""

    beta1: pgml.FloatSweep | None = None
    """Decay rate"""


OptimizerSweepField = typing.Union[
    OptimizerSweep,
    pgml.NestedChoice[OptimizerSweep, patch.OptimizerPatch],  # type: ignore
]


class DataSweep(pgml.Sweeper[patch.DataPatch]):
    """Data configuration"""

    batch_size: pgml.IntSweep | None = None
    """Batch size for a single GPU"""

    num_epochs: pgml.IntSweep | None = None
    """Number of epochs to train"""


DataSweepField = typing.Union[
    DataSweep,
    pgml.NestedChoice[DataSweep, patch.DataPatch],  # type: ignore
]


class ConvBlockSweep(pgml.Sweeper[patch.ConvBlockPatch]):
    """Convolutional layer configuration"""

    out_channels: pgml.IntSweep | None = None
    """Number of output channels"""

    kernel_size: pgml.IntSweep | None = None
    """Square kernel size"""

    pool_size: pgml.IntSweep | None = None
    """Square pool size"""

    activation: ActivationSweepField | None = None
    """Activation function"""


ConvBlockSweepField = typing.Union[
    ConvBlockSweep,
    pgml.NestedChoice[ConvBlockSweep, patch.ConvBlockPatch],  # type: ignore
]


class LinearBlockSweep(pgml.Sweeper[patch.LinearBlockPatch]):
    """Linear layer configuration"""

    out_features: pgml.IntSweep | None = None
    """Number of output features"""

    activation: ActivationSweepField | None = None
    """Activation function"""


LinearBlockSweepField = typing.Union[
    LinearBlockSweep,
    pgml.NestedChoice[LinearBlockSweep, patch.LinearBlockPatch],  # type: ignore
]


class ConvNetSweep(pgml.Sweeper[patch.ConvNetPatch]):
    """Convolutional neural network configuration"""

    block: ConvBlockSweepField | None = None
    """Conv layer configuration"""

    num_layers: pgml.IntSweep | None = None
    """Number of layers"""


ConvNetSweepField = typing.Union[
    ConvNetSweep,
    pgml.NestedChoice[ConvNetSweep, patch.ConvNetPatch],  # type: ignore
]


class MLPSweep(pgml.Sweeper[patch.MLPPatch]):
    """Multi-layer perceptron configuration"""

    block: LinearBlockSweepField | None = None
    """Linear layer configuration"""

    num_layers: pgml.IntSweep | None = None
    """Number of layers"""


MLPSweepField = typing.Union[
    MLPSweep,
    pgml.NestedChoice[MLPSweep, patch.MLPPatch],  # type: ignore
]


class ModelSweep(pgml.Sweeper[patch.ModelPatch]):
    """Model configuration"""

    conv_net: ConvNetSweepField | None = None
    """Conv blocks"""

    head: MLPSweepField | None = None
    """MLP head"""


ModelSweepField = typing.Union[
    ModelSweep,
    pgml.NestedChoice[ModelSweep, patch.ModelPatch],  # type: ignore
]


class ProjectSweep(pgml.Sweeper[patch.ProjectPatch]):
    """Global configuration"""

    net: ModelSweepField | None = None
    """Model configuration"""

    optimizer: OptimizerSweepField | None = None
    """Optimizer configuration"""

    data: DataSweepField | None = None
    """Data configuration"""



ProjectSweepField = typing.Union[
    ProjectSweep,
    pgml.NestedChoice[ProjectSweep, patch.ProjectPatch],  # type: ignore
]

