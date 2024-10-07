import typing

import py_gen_ml as pgml

from . import cli_extension_demo_patch as patch
from . import cli_extension_demo_base as base


class ModelSweep(pgml.Sweeper[patch.ModelPatch]):
    """Model configuration"""

    num_layers: pgml.IntSweep | None = None
    """Number of layers"""



ModelSweepField = typing.Union[
    ModelSweep,
    pgml.NestedChoice[ModelSweep, patch.ModelPatch],  # type: ignore
]


class TrainingSweep(pgml.Sweeper[patch.TrainingPatch]):
    """Training configuration"""

    num_epochs: pgml.IntSweep | None = None
    """Number of epochs"""



TrainingSweepField = typing.Union[
    TrainingSweep,
    pgml.NestedChoice[TrainingSweep, patch.TrainingPatch],  # type: ignore
]


class DatasetSweep(pgml.Sweeper[patch.DatasetPatch]):
    """Dataset configuration"""

    path: pgml.StrSweep | None = None
    """Path to the dataset"""



DatasetSweepField = typing.Union[
    DatasetSweep,
    pgml.NestedChoice[DatasetSweep, patch.DatasetPatch],  # type: ignore
]


class DataSweep(pgml.Sweeper[patch.DataPatch]):
    """Data config"""

    train_dataset: DatasetSweepField | None = None
    """Path to the dataset"""

    test_dataset: DatasetSweepField | None = None
    """Path to the dataset"""

    num_workers: pgml.IntSweep | None = None
    """Number of workers for loading the dataset"""



DataSweepField = typing.Union[
    DataSweep,
    pgml.NestedChoice[DataSweep, patch.DataPatch],  # type: ignore
]


class ProjectSweep(pgml.Sweeper[patch.ProjectPatch]):
    """Global configuration"""

    data: DataSweepField | None = None
    """Dataset configuration"""

    model: ModelSweepField | None = None
    """Model configuration"""

    training: TrainingSweepField | None = None
    """Training configuration"""



ProjectSweepField = typing.Union[
    ProjectSweep,
    pgml.NestedChoice[ProjectSweep, patch.ProjectPatch],  # type: ignore
]

