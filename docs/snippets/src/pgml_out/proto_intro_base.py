# Autogenerated code. DO NOT EDIT.
import py_gen_ml as pgml


class MLP(pgml.YamlBaseModel):
    """Multi-layer perceptron configuration"""

    num_layers: int
    """Number of layers"""

    num_units: int
    """Number of units"""

    activation: str
    """Activation function"""
