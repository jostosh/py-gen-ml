# Autogenerated code. DO NOT EDIT.
import enum

import py_gen_ml as pgml


class Activation(str, enum.Enum):
    """Activation is an enum of activation functions."""

    RELU = "RELU"
    """ReLU is the Rectified Linear Unit activation function."""

    TANH = "TANH"
    """TANH is the hyperbolic tangent activation function."""

    SIGMOID = "SIGMOID"
    """SIGMOID is the sigmoid activation function."""


class MLPParsingDemo(pgml.YamlBaseModel):
    """MLP is a simple multi-layer perceptron."""

    num_layers: int = 2
    """Number of layers in the MLP."""

    num_units: int
    """Number of units in each layer."""

    activation: Activation
    """Activation function to use."""
