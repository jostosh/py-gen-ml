# Autogenerated code. DO NOT EDIT.
import py_gen_ml as pgml

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import torch.nn


class Linear(pgml.YamlBaseModel):
    """Linear layer configuration"""

    in_features: int
    """Number of input features"""

    out_features: int
    """Number of output features"""

    bias: bool
    """Bias"""

    def build(self) -> "torch.nn.Linear":
        import torch.nn

        return torch.nn.Linear(
            in_features=self.in_features,
            out_features=self.out_features,
            bias=self.bias,
        )


class MLP(pgml.YamlBaseModel):
    """MLP configuration"""

    layers: list[Linear]
    """Linear layers"""

    def build(self) -> "torch.nn.Sequential":
        import torch.nn

        return torch.nn.Sequential(
            *(elem.build() for elem in self.layers),
        )
