import typing

import py_gen_ml as pgml

from . import unit_base as base
from . import unit_patch as patch

EnumSweepField = typing.Union[
    pgml.Choice[base.Enum],
    typing.Literal['any'],
    base.Enum,
]


class Int32TestSweep(pgml.Sweeper[patch.Int32TestPatch]):
    value: typing.Optional[pgml.IntSweep] = None


Int32TestSweepField = typing.Union[
    Int32TestSweep,
    pgml.NestedChoice[Int32TestSweep, patch.Int32TestPatch],  # type: ignore
]


class Int64TestSweep(pgml.Sweeper[patch.Int64TestPatch]):
    value: typing.Optional[pgml.IntSweep] = None


Int64TestSweepField = typing.Union[
    Int64TestSweep,
    pgml.NestedChoice[Int64TestSweep, patch.Int64TestPatch],  # type: ignore
]


class Uint32TestSweep(pgml.Sweeper[patch.Uint32TestPatch]):
    value: typing.Optional[pgml.IntSweep] = None


Uint32TestSweepField = typing.Union[
    Uint32TestSweep,
    pgml.NestedChoice[Uint32TestSweep, patch.Uint32TestPatch],  # type: ignore
]


class Uint64TestSweep(pgml.Sweeper[patch.Uint64TestPatch]):
    value: typing.Optional[pgml.IntSweep] = None


Uint64TestSweepField = typing.Union[
    Uint64TestSweep,
    pgml.NestedChoice[Uint64TestSweep, patch.Uint64TestPatch],  # type: ignore
]


class Sint32TestSweep(pgml.Sweeper[patch.Sint32TestPatch]):
    value: typing.Optional[pgml.IntSweep] = None


Sint32TestSweepField = typing.Union[
    Sint32TestSweep,
    pgml.NestedChoice[Sint32TestSweep, patch.Sint32TestPatch],  # type: ignore
]


class Sint64TestSweep(pgml.Sweeper[patch.Sint64TestPatch]):
    value: typing.Optional[pgml.IntSweep] = None


Sint64TestSweepField = typing.Union[
    Sint64TestSweep,
    pgml.NestedChoice[Sint64TestSweep, patch.Sint64TestPatch],  # type: ignore
]


class Fixed32TestSweep(pgml.Sweeper[patch.Fixed32TestPatch]):
    value: typing.Optional[pgml.IntSweep] = None


Fixed32TestSweepField = typing.Union[
    Fixed32TestSweep,
    pgml.NestedChoice[Fixed32TestSweep, patch.Fixed32TestPatch],  # type: ignore
]


class Fixed64TestSweep(pgml.Sweeper[patch.Fixed64TestPatch]):
    value: typing.Optional[pgml.IntSweep] = None


Fixed64TestSweepField = typing.Union[
    Fixed64TestSweep,
    pgml.NestedChoice[Fixed64TestSweep, patch.Fixed64TestPatch],  # type: ignore
]


class Sfixed32TestSweep(pgml.Sweeper[patch.Sfixed32TestPatch]):
    value: typing.Optional[pgml.IntSweep] = None


Sfixed32TestSweepField = typing.Union[
    Sfixed32TestSweep,
    pgml.NestedChoice[Sfixed32TestSweep, patch.Sfixed32TestPatch],  # type: ignore
]


class Sfixed64TestSweep(pgml.Sweeper[patch.Sfixed64TestPatch]):
    value: typing.Optional[pgml.IntSweep] = None


Sfixed64TestSweepField = typing.Union[
    Sfixed64TestSweep,
    pgml.NestedChoice[Sfixed64TestSweep, patch.Sfixed64TestPatch],  # type: ignore
]


class BoolTestSweep(pgml.Sweeper[patch.BoolTestPatch]):
    value: typing.Optional[pgml.BoolSweep] = None


BoolTestSweepField = typing.Union[
    BoolTestSweep,
    pgml.NestedChoice[BoolTestSweep, patch.BoolTestPatch],  # type: ignore
]


class FloatTestSweep(pgml.Sweeper[patch.FloatTestPatch]):
    value: typing.Optional[pgml.FloatSweep] = None


FloatTestSweepField = typing.Union[
    FloatTestSweep,
    pgml.NestedChoice[FloatTestSweep, patch.FloatTestPatch],  # type: ignore
]


class DoubleTestSweep(pgml.Sweeper[patch.DoubleTestPatch]):
    value: typing.Optional[pgml.FloatSweep] = None


DoubleTestSweepField = typing.Union[
    DoubleTestSweep,
    pgml.NestedChoice[DoubleTestSweep, patch.DoubleTestPatch],  # type: ignore
]


class StringTestSweep(pgml.Sweeper[patch.StringTestPatch]):
    value: typing.Optional[pgml.StrSweep] = None


StringTestSweepField = typing.Union[
    StringTestSweep,
    pgml.NestedChoice[StringTestSweep, patch.StringTestPatch],  # type: ignore
]


class BytesTestSweep(pgml.Sweeper[patch.BytesTestPatch]):
    value: typing.Optional[pgml.BytesSweep] = None


BytesTestSweepField = typing.Union[
    BytesTestSweep,
    pgml.NestedChoice[BytesTestSweep, patch.BytesTestPatch],  # type: ignore
]


class EnumTestSweep(pgml.Sweeper[patch.EnumTestPatch]):
    value: typing.Optional[EnumSweepField] = None


EnumTestSweepField = typing.Union[
    EnumTestSweep,
    pgml.NestedChoice[EnumTestSweep, patch.EnumTestPatch],  # type: ignore
]


class EnumDefaultTestSweep(pgml.Sweeper[patch.EnumDefaultTestPatch]):
    value: typing.Optional[EnumSweepField] = None


EnumDefaultTestSweepField = typing.Union[
    EnumDefaultTestSweep,
    pgml.NestedChoice[EnumDefaultTestSweep, patch.EnumDefaultTestPatch],  # type: ignore
]


class OneofTestSweep(pgml.Sweeper[patch.OneofTestPatch]):
    value: typing.Optional[typing.Union[pgml.Sweeper[pgml.IntSweep], pgml.Sweeper[pgml.StrSweep]]] = None


OneofTestSweepField = typing.Union[
    OneofTestSweep,
    pgml.NestedChoice[OneofTestSweep, patch.OneofTestPatch],  # type: ignore
]


class RepeatedTestSweep(pgml.Sweeper[patch.RepeatedTestPatch]):
    values: typing.Optional[pgml.IntSweep] = None


RepeatedTestSweepField = typing.Union[
    RepeatedTestSweep,
    pgml.NestedChoice[RepeatedTestSweep, patch.RepeatedTestPatch],  # type: ignore
]


class OptionalTestSweep(pgml.Sweeper[patch.OptionalTestPatch]):
    _value: typing.Optional[typing.Union[pgml.Sweeper[pgml.IntSweep]]] = None


OptionalTestSweepField = typing.Union[
    OptionalTestSweep,
    pgml.NestedChoice[OptionalTestSweep, patch.OptionalTestPatch],  # type: ignore
]


class Int32DefaultTestSweep(pgml.Sweeper[patch.Int32DefaultTestPatch]):
    value: typing.Optional[pgml.IntSweep] = None


Int32DefaultTestSweepField = typing.Union[
    Int32DefaultTestSweep,
    pgml.NestedChoice[Int32DefaultTestSweep, patch.Int32DefaultTestPatch],  # type: ignore
]


class Int64DefaultTestSweep(pgml.Sweeper[patch.Int64DefaultTestPatch]):
    value: typing.Optional[pgml.IntSweep] = None


Int64DefaultTestSweepField = typing.Union[
    Int64DefaultTestSweep,
    pgml.NestedChoice[Int64DefaultTestSweep, patch.Int64DefaultTestPatch],  # type: ignore
]


class Uint32DefaultTestSweep(pgml.Sweeper[patch.Uint32DefaultTestPatch]):
    value: typing.Optional[pgml.IntSweep] = None


Uint32DefaultTestSweepField = typing.Union[
    Uint32DefaultTestSweep,
    pgml.NestedChoice[Uint32DefaultTestSweep, patch.Uint32DefaultTestPatch],  # type: ignore
]


class Uint64DefaultTestSweep(pgml.Sweeper[patch.Uint64DefaultTestPatch]):
    value: typing.Optional[pgml.IntSweep] = None


Uint64DefaultTestSweepField = typing.Union[
    Uint64DefaultTestSweep,
    pgml.NestedChoice[Uint64DefaultTestSweep, patch.Uint64DefaultTestPatch],  # type: ignore
]


class Sint32DefaultTestSweep(pgml.Sweeper[patch.Sint32DefaultTestPatch]):
    value: typing.Optional[pgml.IntSweep] = None


Sint32DefaultTestSweepField = typing.Union[
    Sint32DefaultTestSweep,
    pgml.NestedChoice[Sint32DefaultTestSweep, patch.Sint32DefaultTestPatch],  # type: ignore
]


class Sint64DefaultTestSweep(pgml.Sweeper[patch.Sint64DefaultTestPatch]):
    value: typing.Optional[pgml.IntSweep] = None


Sint64DefaultTestSweepField = typing.Union[
    Sint64DefaultTestSweep,
    pgml.NestedChoice[Sint64DefaultTestSweep, patch.Sint64DefaultTestPatch],  # type: ignore
]


class Fixed32DefaultTestSweep(pgml.Sweeper[patch.Fixed32DefaultTestPatch]):
    value: typing.Optional[pgml.IntSweep] = None


Fixed32DefaultTestSweepField = typing.Union[
    Fixed32DefaultTestSweep,
    pgml.NestedChoice[Fixed32DefaultTestSweep, patch.Fixed32DefaultTestPatch],  # type: ignore
]


class Fixed64DefaultTestSweep(pgml.Sweeper[patch.Fixed64DefaultTestPatch]):
    value: typing.Optional[pgml.IntSweep] = None


Fixed64DefaultTestSweepField = typing.Union[
    Fixed64DefaultTestSweep,
    pgml.NestedChoice[Fixed64DefaultTestSweep, patch.Fixed64DefaultTestPatch],  # type: ignore
]


class Sfixed32DefaultTestSweep(pgml.Sweeper[patch.Sfixed32DefaultTestPatch]):
    value: typing.Optional[pgml.IntSweep] = None


Sfixed32DefaultTestSweepField = typing.Union[
    Sfixed32DefaultTestSweep,
    pgml.NestedChoice[Sfixed32DefaultTestSweep, patch.Sfixed32DefaultTestPatch],  # type: ignore
]


class Sfixed64DefaultTestSweep(pgml.Sweeper[patch.Sfixed64DefaultTestPatch]):
    value: typing.Optional[pgml.IntSweep] = None


Sfixed64DefaultTestSweepField = typing.Union[
    Sfixed64DefaultTestSweep,
    pgml.NestedChoice[Sfixed64DefaultTestSweep, patch.Sfixed64DefaultTestPatch],  # type: ignore
]


class BoolDefaultTestSweep(pgml.Sweeper[patch.BoolDefaultTestPatch]):
    value: typing.Optional[pgml.BoolSweep] = None


BoolDefaultTestSweepField = typing.Union[
    BoolDefaultTestSweep,
    pgml.NestedChoice[BoolDefaultTestSweep, patch.BoolDefaultTestPatch],  # type: ignore
]


class FloatDefaultTestSweep(pgml.Sweeper[patch.FloatDefaultTestPatch]):
    value: typing.Optional[pgml.FloatSweep] = None


FloatDefaultTestSweepField = typing.Union[
    FloatDefaultTestSweep,
    pgml.NestedChoice[FloatDefaultTestSweep, patch.FloatDefaultTestPatch],  # type: ignore
]


class DoubleDefaultTestSweep(pgml.Sweeper[patch.DoubleDefaultTestPatch]):
    value: typing.Optional[pgml.FloatSweep] = None


DoubleDefaultTestSweepField = typing.Union[
    DoubleDefaultTestSweep,
    pgml.NestedChoice[DoubleDefaultTestSweep, patch.DoubleDefaultTestPatch],  # type: ignore
]


class StringDefaultTestSweep(pgml.Sweeper[patch.StringDefaultTestPatch]):
    value: typing.Optional[pgml.StrSweep] = None


StringDefaultTestSweepField = typing.Union[
    StringDefaultTestSweep,
    pgml.NestedChoice[StringDefaultTestSweep, patch.StringDefaultTestPatch],  # type: ignore
]


class BytesDefaultTestSweep(pgml.Sweeper[patch.BytesDefaultTestPatch]):
    value: typing.Optional[pgml.BytesSweep] = None


BytesDefaultTestSweepField = typing.Union[
    BytesDefaultTestSweep,
    pgml.NestedChoice[BytesDefaultTestSweep, patch.BytesDefaultTestPatch],  # type: ignore
]


class OneofDefaultTestSweep(pgml.Sweeper[patch.OneofDefaultTestPatch]):
    value: typing.Optional[typing.Union[pgml.Sweeper[pgml.IntSweep], pgml.Sweeper[pgml.StrSweep]]] = None


OneofDefaultTestSweepField = typing.Union[
    OneofDefaultTestSweep,
    pgml.NestedChoice[OneofDefaultTestSweep, patch.OneofDefaultTestPatch],  # type: ignore
]


class OptionalDefaultTestSweep(pgml.Sweeper[patch.OptionalDefaultTestPatch]):
    _value: typing.Optional[typing.Union[pgml.Sweeper[pgml.IntSweep]]] = None


OptionalDefaultTestSweepField = typing.Union[
    OptionalDefaultTestSweep,
    pgml.NestedChoice[OptionalDefaultTestSweep, patch.OptionalDefaultTestPatch],  # type: ignore
]


class ExplicitCLIArgTestSweep(pgml.Sweeper[patch.ExplicitCLIArgTestPatch]):
    bar: typing.Optional[pgml.StrSweep] = None


ExplicitCLIArgTestSweepField = typing.Union[
    ExplicitCLIArgTestSweep,
    pgml.NestedChoice[ExplicitCLIArgTestSweep, patch.ExplicitCLIArgTestPatch],  # type: ignore
]


class ImplicitCLIArgTestSweep(pgml.Sweeper[patch.ImplicitCLIArgTestPatch]):
    bar: typing.Optional[pgml.StrSweep] = None


ImplicitCLIArgTestSweepField = typing.Union[
    ImplicitCLIArgTestSweep,
    pgml.NestedChoice[ImplicitCLIArgTestSweep, patch.ImplicitCLIArgTestPatch],  # type: ignore
]


class NestedFooTestSweep(pgml.Sweeper[patch.NestedFooTestPatch]):
    foo: typing.Optional[pgml.StrSweep] = None


NestedFooTestSweepField = typing.Union[
    NestedFooTestSweep,
    pgml.NestedChoice[NestedFooTestSweep, patch.NestedFooTestPatch],  # type: ignore
]


class NestedBarTestSweep(pgml.Sweeper[patch.NestedBarTestPatch]):
    foo_0: typing.Optional[NestedFooTestSweepField] = None
    foo_1: typing.Optional[NestedFooTestSweepField] = None


NestedBarTestSweepField = typing.Union[
    NestedBarTestSweep,
    pgml.NestedChoice[NestedBarTestSweep, patch.NestedBarTestPatch],  # type: ignore
]


class RepeatedNestedBarTestSweep(pgml.Sweeper[patch.RepeatedNestedBarTestPatch]):
    bar: typing.Optional[NestedBarTestSweepField] = None


RepeatedNestedBarTestSweepField = typing.Union[
    RepeatedNestedBarTestSweep,
    pgml.NestedChoice[RepeatedNestedBarTestSweep, patch.RepeatedNestedBarTestPatch],  # type: ignore
]
