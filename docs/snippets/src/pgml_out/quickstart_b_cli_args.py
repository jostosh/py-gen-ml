# Autogenerated code. DO NOT EDIT.
import py_gen_ml as pgml
import typing

import pydantic
import typer

from . import quickstart_b_base as base


class MLPQuickstartArgs(pgml.YamlBaseModel):
    """Multi-layer perceptron configuration"""

    num_layers: typing.Annotated[
        typing.Optional[int],
        typer.Option(help="Number of layers. Maps to 'num_layers'"),
        pydantic.Field(None),
        pgml.ArgRef("num_layers"),
    ]
    """Number of layers"""

    num_units: typing.Annotated[
        typing.Optional[int],
        typer.Option(help="Number of units. Maps to 'num_units'"),
        pydantic.Field(None),
        pgml.ArgRef("num_units"),
    ]
    """Number of units"""

    activation: typing.Annotated[
        typing.Optional[str],
        typer.Option(help="Activation function. Maps to 'activation'"),
        pydantic.Field(None),
        pgml.ArgRef("activation"),
    ]
    """Activation function"""
