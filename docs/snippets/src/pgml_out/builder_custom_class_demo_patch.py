# Autogenerated code. DO NOT EDIT.
import typing
import py_gen_ml as pgml


class LinearBlockPatch(pgml.YamlBaseModel):
    """Linear block configuration"""

    in_features: typing.Optional[int] = None
    """Number of input features"""

    out_features: typing.Optional[int] = None
    """Number of output features"""

    bias: typing.Optional[bool] = None
    """Bias"""

    dropout: typing.Optional[float] = None
    """Dropout probability"""

    activation: typing.Optional[str] = None
    """Activation function"""


class MLPPatch(pgml.YamlBaseModel):
    """MLP configuration"""

    layers: typing.Optional[typing.List[LinearBlockPatch]] = None
    """Linear blocks"""
