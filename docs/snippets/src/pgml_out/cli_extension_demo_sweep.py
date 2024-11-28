import typing

import py_gen_ml as pgml

from . import cli_extension_demo_patch as patch
from . import cli_extension_demo_base as base


class ModelSweep(pgml.Sweeper[patch.ModelPatch]):
    """Model configuration"""

    num_layers: typing.Optional[pgml.IntSweep] = None
    """Number of layers"""


ModelSweepField = typing.Union[
    ModelSweep,
    pgml.NestedChoice[ModelSweep, patch.ModelPatch],  # type: ignore
]


class TrainingSweep(pgml.Sweeper[patch.TrainingPatch]):
    """Training configuration"""

    num_epochs: typing.Optional[pgml.IntSweep] = None
    """Number of epochs"""


TrainingSweepField = typing.Union[
    TrainingSweep,
    pgml.NestedChoice[TrainingSweep, patch.TrainingPatch],  # type: ignore
]


class DatasetSweep(pgml.Sweeper[patch.DatasetPatch]):
    """Dataset configuration"""

    path: typing.Optional[pgml.StrSweep] = None
    """Path to the dataset"""


DatasetSweepField = typing.Union[
    DatasetSweep,
    pgml.NestedChoice[DatasetSweep, patch.DatasetPatch],  # type: ignore
]


class DataSweep(pgml.Sweeper[patch.DataPatch]):
    """Data config"""

    train_dataset: typing.Optional[DatasetSweepField] = None
    """Path to the dataset"""

    test_dataset: typing.Optional[DatasetSweepField] = None
    """Path to the dataset"""

    num_workers: typing.Optional[pgml.IntSweep] = None
    """Number of workers for loading the dataset"""


DataSweepField = typing.Union[
    DataSweep,
    pgml.NestedChoice[DataSweep, patch.DataPatch],  # type: ignore
]


class CliExtensionDemoSweep(pgml.Sweeper[patch.CliExtensionDemoPatch]):
    """Global configuration"""

    data: typing.Optional[DataSweepField] = None
    """Dataset configuration"""

    model: typing.Optional[ModelSweepField] = None
    """Model configuration"""

    training: typing.Optional[TrainingSweepField] = None
    """Training configuration"""



CliExtensionDemoSweepField = typing.Union[
    CliExtensionDemoSweep,
    pgml.NestedChoice[CliExtensionDemoSweep, patch.CliExtensionDemoPatch],  # type: ignore
]

