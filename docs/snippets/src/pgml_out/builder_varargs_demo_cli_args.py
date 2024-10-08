# Autogenerated code. DO NOT EDIT.
import py_gen_ml as pgml
import typing

import pydantic
import typer

from . import builder_varargs_demo_base as base


class LinearArgs(pgml.YamlBaseModel):
    """Linear layer configuration"""

    in_features: typing.Annotated[typing.Optional[int], typer.Option(help="Number of input features. Maps to 'in_features'"), pydantic.Field(None), pgml.ArgRef("in_features")]
    """Number of input features"""

    out_features: typing.Annotated[typing.Optional[int], typer.Option(help="Number of output features. Maps to 'out_features'"), pydantic.Field(None), pgml.ArgRef("out_features")]
    """Number of output features"""

    bias: typing.Annotated[typing.Optional[bool], typer.Option(help="Bias. Maps to 'bias'"), pydantic.Field(None), pgml.ArgRef("bias")]
    """Bias"""



class MLPArgs(pgml.YamlBaseModel):
    """MLP configuration"""

    in_features: typing.Annotated[typing.Optional[int], typer.Option(help="Number of input features. Maps to 'layers.in_features'"), pydantic.Field(None), pgml.ArgRef("layers.in_features")]
    """Number of input features"""

    out_features: typing.Annotated[typing.Optional[int], typer.Option(help="Number of output features. Maps to 'layers.out_features'"), pydantic.Field(None), pgml.ArgRef("layers.out_features")]
    """Number of output features"""

    bias: typing.Annotated[typing.Optional[bool], typer.Option(help="Bias. Maps to 'layers.bias'"), pydantic.Field(None), pgml.ArgRef("layers.bias")]
    """Bias"""


