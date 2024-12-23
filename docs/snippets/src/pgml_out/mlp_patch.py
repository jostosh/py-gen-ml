# Autogenerated code. DO NOT EDIT.
import typing
import py_gen_ml as pgml

from . import mlp_base as base


class MLPParsingDemoPatch(pgml.YamlBaseModel):
    """MLP is a simple multi-layer perceptron."""

    num_layers: typing.Optional[int] = None
    """Number of layers in the MLP."""

    num_units: typing.Optional[int] = None
    """Number of units in each layer."""

    activation: typing.Optional[base.Activation] = None
    """Activation function to use."""
