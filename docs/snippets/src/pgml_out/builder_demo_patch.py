# Autogenerated code. DO NOT EDIT.
import typing
import py_gen_ml as pgml


class LinearPatch(pgml.YamlBaseModel):
    """Linear layer configuration"""

    in_features: typing.Optional[int] = None
    """Number of input features"""

    out_features: typing.Optional[int] = None
    """Number of output features"""

    bias: typing.Optional[bool] = None
    """Bias"""


class MLPPatch(pgml.YamlBaseModel):
    """MLP configuration"""

    layers: typing.Optional[typing.List[LinearPatch]] = None
    """Linear layers"""
