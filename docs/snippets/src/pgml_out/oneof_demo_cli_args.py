# Autogenerated code. DO NOT EDIT.
import py_gen_ml as pgml
import typing

import pydantic
import typer

from . import oneof_demo_base as base


class TransformerArgs(pgml.YamlBaseModel):
    """Transformer configuration"""

    num_layers: typing.Annotated[typing.Optional[int], typer.Option(help="Number of layers. Maps to 'num_layers'"), pydantic.Field(None), pgml.ArgRef("num_layers")]
    """Number of layers"""

    num_heads: typing.Annotated[typing.Optional[int], typer.Option(help="Number of heads. Maps to 'num_heads'"), pydantic.Field(None), pgml.ArgRef("num_heads")]
    """Number of heads"""

    activation: typing.Annotated[typing.Optional[str], typer.Option(help="Activation function. Maps to 'activation'"), pydantic.Field(None), pgml.ArgRef("activation")]
    """Activation function"""



class ConvBlockArgs(pgml.YamlBaseModel):
    """Conv block"""

    out_channels: typing.Annotated[typing.Optional[int], typer.Option(help="Number of output channels. Maps to 'out_channels'"), pydantic.Field(None), pgml.ArgRef("out_channels")]
    """Number of output channels"""

    kernel_size: typing.Annotated[typing.Optional[int], typer.Option(help="Kernel size. Maps to 'kernel_size'"), pydantic.Field(None), pgml.ArgRef("kernel_size")]
    """Kernel size"""

    activation: typing.Annotated[typing.Optional[str], typer.Option(help="Activation function. Maps to 'activation'"), pydantic.Field(None), pgml.ArgRef("activation")]
    """Activation function"""



class ConvNetArgs(pgml.YamlBaseModel):
    """Convolutional neural network configuration"""

    out_channels: typing.Annotated[typing.Optional[int], typer.Option(help="Number of output channels. Maps to 'layers.out_channels'"), pydantic.Field(None), pgml.ArgRef("layers.out_channels")]
    """Number of output channels"""

    kernel_size: typing.Annotated[typing.Optional[int], typer.Option(help="Kernel size. Maps to 'layers.kernel_size'"), pydantic.Field(None), pgml.ArgRef("layers.kernel_size")]
    """Kernel size"""

    activation: typing.Annotated[typing.Optional[str], typer.Option(help="Activation function. Maps to 'layers.activation'"), pydantic.Field(None), pgml.ArgRef("layers.activation")]
    """Activation function"""



class ModelArgs(pgml.YamlBaseModel):
    """Model configuration"""

    num_layers: typing.Annotated[typing.Optional[int], typer.Option(help="Number of layers. Maps to 'backbone.num_layers'"), pydantic.Field(None), pgml.ArgRef("backbone.num_layers")]
    """Number of layers"""

    num_heads: typing.Annotated[typing.Optional[int], typer.Option(help="Number of heads. Maps to 'backbone.num_heads'"), pydantic.Field(None), pgml.ArgRef("backbone.num_heads")]
    """Number of heads"""

    out_channels: typing.Annotated[typing.Optional[int], typer.Option(help="Number of output channels. Maps to 'backbone.layers.out_channels'"), pydantic.Field(None), pgml.ArgRef("backbone.layers.out_channels")]
    """Number of output channels"""

    kernel_size: typing.Annotated[typing.Optional[int], typer.Option(help="Kernel size. Maps to 'backbone.layers.kernel_size'"), pydantic.Field(None), pgml.ArgRef("backbone.layers.kernel_size")]
    """Kernel size"""


