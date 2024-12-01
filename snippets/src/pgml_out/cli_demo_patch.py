# Autogenerated code. DO NOT EDIT.
import typing
import py_gen_ml as pgml


class ModelPatch(pgml.YamlBaseModel):
    """Model configuration"""

    num_layers: typing.Optional[int] = None
    """Number of layers"""


class TrainingPatch(pgml.YamlBaseModel):
    """Training configuration"""

    num_epochs: typing.Optional[int] = None
    """Number of epochs"""


class DatasetPatch(pgml.YamlBaseModel):
    """Dataset configuration"""

    path: typing.Optional[str] = None
    """Path to the dataset"""


class DataPatch(pgml.YamlBaseModel):
    """Data config"""

    dataset: typing.Optional[DatasetPatch] = None
    """Path to the dataset"""

    num_workers: typing.Optional[int] = None
    """Number of workers for loading the dataset"""


class CLIDemoPatch(pgml.YamlBaseModel):
    """Global configuration"""

    data: typing.Optional[DataPatch] = None
    """Dataset configuration"""

    model: typing.Optional[ModelPatch] = None
    """Model configuration"""

    training: typing.Optional[TrainingPatch] = None
    """Training configuration"""