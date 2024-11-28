# Autogenerated code. DO NOT EDIT.
import typing
import py_gen_ml as pgml


class LinearBlockPatch(pgml.YamlBaseModel):
    """Linear block configuration"""

    num_units: typing.Optional[int] = None
    """Number of units"""

    activation: typing.Optional[str] = None
    """Activation function"""


class OptimizerPatch(pgml.YamlBaseModel):
    """Optimizer configuration"""

    type: typing.Optional[str] = None
    """Type of optimizer"""

    learning_rate: typing.Optional[float] = None
    """Learning rate"""


class MLPPatch(pgml.YamlBaseModel):
    """Multi-layer perceptron configuration"""

    layers: typing.Optional[typing.List[LinearBlockPatch]] = None
    """List of linear blocks"""


class TrainingPatch(pgml.YamlBaseModel):
    """Training configuration"""

    mlp: typing.Optional[MLPPatch] = None
    """Multi-layer perceptron configuration"""

    optimizer: typing.Optional[OptimizerPatch] = None
    """Optimizer configuration"""
