# Autogenerated code. DO NOT EDIT.
import py_gen_ml as pgml
import typing

import pydantic
import typer

from . import cli_extension_demo_base as base


class CliExtensionDemoArgs(pgml.YamlBaseModel):
    """Global configuration"""

    train_path: typing.Annotated[
        typing.Optional[str],
        typer.Option(help="Path to the dataset. Maps to 'data.train_dataset.path'"),
        pydantic.Field(None),
        pgml.ArgRef("data.train_dataset.path"),
    ]
    """Path to the dataset"""

    test_path: typing.Annotated[
        typing.Optional[str],
        typer.Option(help="Path to the dataset. Maps to 'data.test_dataset.path'"),
        pydantic.Field(None),
        pgml.ArgRef("data.test_dataset.path"),
    ]
    """Path to the dataset"""

    num_epochs: typing.Annotated[
        typing.Optional[int],
        typer.Option(help="Number of epochs. Maps to 'num_epochs'"),
        pydantic.Field(None),
        pgml.ArgRef("num_epochs"),
    ]
    """Number of epochs"""

    num_workers: typing.Annotated[
        typing.Optional[int],
        typer.
        Option(help="Number of workers for loading the dataset. Maps to 'num_workers'"),
        pydantic.Field(None),
        pgml.ArgRef("num_workers"),
    ]
    """Number of workers for loading the dataset"""

    num_layers: typing.Annotated[
        typing.Optional[int],
        typer.Option(help="Number of layers. Maps to 'num_layers'"),
        pydantic.Field(None),
        pgml.ArgRef("num_layers"),
    ]
    """Number of layers"""
