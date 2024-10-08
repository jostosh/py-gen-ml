# Autogenerated code. DO NOT EDIT.
import py_gen_ml as pgml
import typing

import pydantic
import typer

from . import enum_demo_base as base


class MLPArgs(pgml.YamlBaseModel):
    """MLP configuration"""

    activation: typing.Annotated[typing.Optional[base.Activation], typer.Option(help="Activation function. Maps to 'activation'"), pydantic.Field(None), pgml.ArgRef("activation")]
    """Activation function"""

    num_layers: typing.Annotated[typing.Optional[int], typer.Option(help="Number of layers. Maps to 'num_layers'"), pydantic.Field(None), pgml.ArgRef("num_layers")]
    """Number of layers"""


