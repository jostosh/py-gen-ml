# Autogenerated code. DO NOT EDIT.
import py_gen_ml as pgml


class Transformer(pgml.YamlBaseModel):
    """Transformer configuration"""

    num_layers: int
    """Number of layers"""

    num_heads: int
    """Number of heads"""

    activation: str
    """Activation function"""



class ConvBlock(pgml.YamlBaseModel):
    """Conv block"""

    out_channels: int
    """Number of output channels"""

    kernel_size: int
    """Kernel size"""

    activation: str
    """Activation function"""



class ConvNet(pgml.YamlBaseModel):
    """Convolutional neural network configuration"""

    layers: list[ConvBlock]
    """Conv layer configuration"""



class Model(pgml.YamlBaseModel):
    """Model configuration"""

    backbone: Transformer | ConvNet

