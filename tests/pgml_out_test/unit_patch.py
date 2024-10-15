# Autogenerated code. DO NOT EDIT.
import py_gen_ml as pgml

from . import unit_base as base


class Int32TestPatch(pgml.YamlBaseModel):
    value: int | None = None


class Int64TestPatch(pgml.YamlBaseModel):
    value: int | None = None


class Uint32TestPatch(pgml.YamlBaseModel):
    value: int | None = None


class Uint64TestPatch(pgml.YamlBaseModel):
    value: int | None = None


class Sint32TestPatch(pgml.YamlBaseModel):
    value: int | None = None


class Sint64TestPatch(pgml.YamlBaseModel):
    value: int | None = None


class Fixed32TestPatch(pgml.YamlBaseModel):
    value: int | None = None


class Fixed64TestPatch(pgml.YamlBaseModel):
    value: int | None = None


class Sfixed32TestPatch(pgml.YamlBaseModel):
    value: int | None = None


class Sfixed64TestPatch(pgml.YamlBaseModel):
    value: int | None = None


class BoolTestPatch(pgml.YamlBaseModel):
    value: bool | None = None


class FloatTestPatch(pgml.YamlBaseModel):
    value: float | None = None


class DoubleTestPatch(pgml.YamlBaseModel):
    value: float | None = None


class StringTestPatch(pgml.YamlBaseModel):
    value: str | None = None


class BytesTestPatch(pgml.YamlBaseModel):
    value: bytes | None = None


class EnumTestPatch(pgml.YamlBaseModel):
    value: base.Enum | None = None


class EnumDefaultTestPatch(pgml.YamlBaseModel):
    value: base.Enum | None = None


class OneofTestPatch(pgml.YamlBaseModel):
    value: int | str


class RepeatedTestPatch(pgml.YamlBaseModel):
    values: list[int] | None = None


class OptionalTestPatch(pgml.YamlBaseModel):
    value: int | None = None


class Int32DefaultTestPatch(pgml.YamlBaseModel):
    value: int | None = None


class Int64DefaultTestPatch(pgml.YamlBaseModel):
    value: int | None = None


class Uint32DefaultTestPatch(pgml.YamlBaseModel):
    value: int | None = None


class Uint64DefaultTestPatch(pgml.YamlBaseModel):
    value: int | None = None


class Sint32DefaultTestPatch(pgml.YamlBaseModel):
    value: int | None = None


class Sint64DefaultTestPatch(pgml.YamlBaseModel):
    value: int | None = None


class Fixed32DefaultTestPatch(pgml.YamlBaseModel):
    value: int | None = None


class Fixed64DefaultTestPatch(pgml.YamlBaseModel):
    value: int | None = None


class Sfixed32DefaultTestPatch(pgml.YamlBaseModel):
    value: int | None = None


class Sfixed64DefaultTestPatch(pgml.YamlBaseModel):
    value: int | None = None


class BoolDefaultTestPatch(pgml.YamlBaseModel):
    value: bool | None = None


class FloatDefaultTestPatch(pgml.YamlBaseModel):
    value: float | None = None


class DoubleDefaultTestPatch(pgml.YamlBaseModel):
    value: float | None = None


class StringDefaultTestPatch(pgml.YamlBaseModel):
    value: str | None = None


class BytesDefaultTestPatch(pgml.YamlBaseModel):
    value: bytes | None = None


class OneofDefaultTestPatch(pgml.YamlBaseModel):
    value: int | str


class OptionalDefaultTestPatch(pgml.YamlBaseModel):
    value: int | None = None


class ExplicitCLIArgTestPatch(pgml.YamlBaseModel):
    bar: str | None = None


class ImplicitCLIArgTestPatch(pgml.YamlBaseModel):
    bar: str | None = None


class NestedFooTestPatch(pgml.YamlBaseModel):
    foo: str | None = None


class NestedBarTestPatch(pgml.YamlBaseModel):
    foo_0: NestedFooTestPatch | None = None
    foo_1: NestedFooTestPatch | None = None


class RepeatedNestedBarTestPatch(pgml.YamlBaseModel):
    bar: list[NestedBarTestPatch] | None = None