# Autogenerated code. DO NOT EDIT.
import typing
import py_gen_ml as pgml

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import example_project.modules


class LinearBlock(pgml.YamlBaseModel):
    """Linear block configuration"""

    in_features: int
    """Number of input features"""

    out_features: int
    """Number of output features"""

    bias: bool
    """Bias"""

    dropout: float
    """Dropout probability"""

    activation: str
    """Activation function"""

    def build(self) -> "example_project.modules.LinearBlock":
        import example_project.modules

        return example_project.modules.LinearBlock(
            in_features=self.in_features,
            out_features=self.out_features,
            bias=self.bias,
            dropout=self.dropout,
            activation=self.activation,
        )


class MLP(pgml.YamlBaseModel):
    """MLP configuration"""

    layers: typing.List[LinearBlock]
    """Linear blocks"""
