# Autogenerated code. DO NOT EDIT.
import py_gen_ml as pgml
import typing

import pydantic
import typer

from . import advanced_base as base


class TrainingArgs(pgml.YamlBaseModel):
    """Training configuration"""

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

    type: typing.Annotated[
        typing.Optional[str],
        typer.Option(help="Type of optimizer. Maps to 'type'"),
        pydantic.Field(None),
        pgml.ArgRef("type"),
    ]
    """Type of optimizer"""

    learning_rate: typing.Annotated[
        typing.Optional[float],
        typer.Option(help="Learning rate. Maps to 'learning_rate'"),
        pydantic.Field(None),
        pgml.ArgRef("learning_rate"),
    ]
    """Learning rate"""
