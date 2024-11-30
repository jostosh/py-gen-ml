# Autogenerated code. DO NOT EDIT.
import py_gen_ml as pgml
import typing

import pydantic
import typer

from . import cli_demo_deep_base as base


class CliDemoDeepArgs(pgml.YamlBaseModel):
    """Global configuration"""

    num_layers: typing.Annotated[
        typing.Optional[int],
        typer.Option(help="Number of layers. Maps to 'model.num_layers'"),
        pydantic.Field(None),
        pgml.ArgRef("model.num_layers"),
    ]
    """Number of layers"""

    train_dataset_path: typing.Annotated[
        typing.Optional[str],
        typer.Option(help="Path to the dataset. Maps to 'data.train_dataset.path'"),
        pydantic.Field(None),
        pgml.ArgRef("data.train_dataset.path"),
    ]
    """Path to the dataset"""

    test_dataset_path: typing.Annotated[
        typing.Optional[str],
        typer.Option(help="Path to the dataset. Maps to 'data.test_dataset.path'"),
        pydantic.Field(None),
        pgml.ArgRef("data.test_dataset.path"),
    ]
    """Path to the dataset"""

    num_epochs: typing.Annotated[
        typing.Optional[int],
        typer.Option(help="Number of epochs. Maps to 'training.num_epochs'"),
        pydantic.Field(None),
        pgml.ArgRef("training.num_epochs"),
    ]
    """Number of epochs"""

    num_workers: typing.Annotated[
        typing.Optional[int],
        typer.Option(
            help="Number of workers for loading the dataset. Maps to 'data.num_workers'"
        ),
        pydantic.Field(None),
        pgml.ArgRef("data.num_workers"),
    ]
    """Number of workers for loading the dataset"""
