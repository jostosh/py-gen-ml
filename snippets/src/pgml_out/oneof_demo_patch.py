# Autogenerated code. DO NOT EDIT.
import typing
import py_gen_ml as pgml


class TransformerPatch(pgml.YamlBaseModel):
    """Transformer configuration"""

    num_layers: typing.Optional[int] = None
    """Number of layers"""

    num_heads: typing.Optional[int] = None
    """Number of heads"""

    activation: typing.Optional[str] = None
    """Activation function"""


class ConvBlockPatch(pgml.YamlBaseModel):
    """Conv block"""

    out_channels: typing.Optional[int] = None
    """Number of output channels"""

    kernel_size: typing.Optional[int] = None
    """Kernel size"""

    activation: typing.Optional[str] = None
    """Activation function"""


class ConvNetPatch(pgml.YamlBaseModel):
    """Convolutional neural network configuration"""

    layers: typing.Optional[typing.List[ConvBlockPatch]] = None
    """Conv layer configuration"""


class ModelPatch(pgml.YamlBaseModel):
    """Model configuration"""

    backbone: typing.Union[TransformerPatch, ConvNetPatch]