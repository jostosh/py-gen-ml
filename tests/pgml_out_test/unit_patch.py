# Autogenerated code. DO NOT EDIT.
import typing

import py_gen_ml as pgml

from . import unit_base as base


class Int32TestPatch(pgml.YamlBaseModel):
    value: typing.Optional[int] = None


class Int64TestPatch(pgml.YamlBaseModel):
    value: typing.Optional[int] = None


class Uint32TestPatch(pgml.YamlBaseModel):
    value: typing.Optional[int] = None


class Uint64TestPatch(pgml.YamlBaseModel):
    value: typing.Optional[int] = None


class Sint32TestPatch(pgml.YamlBaseModel):
    value: typing.Optional[int] = None


class Sint64TestPatch(pgml.YamlBaseModel):
    value: typing.Optional[int] = None


class Fixed32TestPatch(pgml.YamlBaseModel):
    value: typing.Optional[int] = None


class Fixed64TestPatch(pgml.YamlBaseModel):
    value: typing.Optional[int] = None


class Sfixed32TestPatch(pgml.YamlBaseModel):
    value: typing.Optional[int] = None


class Sfixed64TestPatch(pgml.YamlBaseModel):
    value: typing.Optional[int] = None


class BoolTestPatch(pgml.YamlBaseModel):
    value: typing.Optional[bool] = None


class FloatTestPatch(pgml.YamlBaseModel):
    value: typing.Optional[float] = None


class DoubleTestPatch(pgml.YamlBaseModel):
    value: typing.Optional[float] = None


class StringTestPatch(pgml.YamlBaseModel):
    value: typing.Optional[str] = None


class BytesTestPatch(pgml.YamlBaseModel):
    value: typing.Optional[bytes] = None


class EnumTestPatch(pgml.YamlBaseModel):
    value: typing.Optional[base.Enum] = None


class EnumDefaultTestPatch(pgml.YamlBaseModel):
    value: typing.Optional[base.Enum] = None


class OneofTestPatch(pgml.YamlBaseModel):
    value: typing.Union[int, str]


class RepeatedTestPatch(pgml.YamlBaseModel):
    values: typing.Optional[list[int]] = None


class OptionalTestPatch(pgml.YamlBaseModel):
    value: typing.Optional[int] = None


class Int32DefaultTestPatch(pgml.YamlBaseModel):
    value: typing.Optional[int] = None


class Int64DefaultTestPatch(pgml.YamlBaseModel):
    value: typing.Optional[int] = None


class Uint32DefaultTestPatch(pgml.YamlBaseModel):
    value: typing.Optional[int] = None


class Uint64DefaultTestPatch(pgml.YamlBaseModel):
    value: typing.Optional[int] = None


class Sint32DefaultTestPatch(pgml.YamlBaseModel):
    value: typing.Optional[int] = None


class Sint64DefaultTestPatch(pgml.YamlBaseModel):
    value: typing.Optional[int] = None


class Fixed32DefaultTestPatch(pgml.YamlBaseModel):
    value: typing.Optional[int] = None


class Fixed64DefaultTestPatch(pgml.YamlBaseModel):
    value: typing.Optional[int] = None


class Sfixed32DefaultTestPatch(pgml.YamlBaseModel):
    value: typing.Optional[int] = None


class Sfixed64DefaultTestPatch(pgml.YamlBaseModel):
    value: typing.Optional[int] = None


class BoolDefaultTestPatch(pgml.YamlBaseModel):
    value: typing.Optional[bool] = None


class FloatDefaultTestPatch(pgml.YamlBaseModel):
    value: typing.Optional[float] = None


class DoubleDefaultTestPatch(pgml.YamlBaseModel):
    value: typing.Optional[float] = None


class StringDefaultTestPatch(pgml.YamlBaseModel):
    value: typing.Optional[str] = None


class BytesDefaultTestPatch(pgml.YamlBaseModel):
    value: typing.Optional[bytes] = None


class OneofDefaultTestPatch(pgml.YamlBaseModel):
    value: typing.Union[int, str]


class OptionalDefaultTestPatch(pgml.YamlBaseModel):
    value: typing.Optional[int] = None


class ExplicitCLIArgTestPatch(pgml.YamlBaseModel):
    bar: typing.Optional[str] = None


class ImplicitCLIArgTestPatch(pgml.YamlBaseModel):
    bar: typing.Optional[str] = None


class NestedFooTestPatch(pgml.YamlBaseModel):
    foo: typing.Optional[str] = None


class NestedBarTestPatch(pgml.YamlBaseModel):
    foo_0: typing.Optional[NestedFooTestPatch] = None
    foo_1: typing.Optional[NestedFooTestPatch] = None


class RepeatedNestedBarTestPatch(pgml.YamlBaseModel):
    bar: typing.Optional[list[NestedBarTestPatch]] = None
