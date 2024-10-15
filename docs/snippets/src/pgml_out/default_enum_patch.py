# Autogenerated code. DO NOT EDIT.
import py_gen_ml as pgml

from . import default_enum_base as base


class LinearPatch(pgml.YamlBaseModel):
    """Linear layer"""

    in_features: int | None = None
    """Number of input features"""

    out_features: int | None = None
    """Number of output features"""

    activation: base.Activation | None = None
    """Activation function"""
