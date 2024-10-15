from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor
ENABLE_FIELD_NUMBER: _ClassVar[int]
enable: _descriptor.FieldDescriptor
FACTORY_FIELD_NUMBER: _ClassVar[int]
factory: _descriptor.FieldDescriptor
CLI_FIELD_NUMBER: _ClassVar[int]
cli: _descriptor.FieldDescriptor
DEFAULT_FIELD_NUMBER: _ClassVar[int]
default: _descriptor.FieldDescriptor
AS_VARARGS_FIELD_NUMBER: _ClassVar[int]
as_varargs: _descriptor.FieldDescriptor

class Arg(_message.Message):
    __slots__ = ("name", "path")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    name: str
    path: str
    def __init__(self, name: _Optional[str] = ..., path: _Optional[str] = ...) -> None: ...

class CLI(_message.Message):
    __slots__ = ("arg", "enable")
    ARG_FIELD_NUMBER: _ClassVar[int]
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    arg: _containers.RepeatedCompositeFieldContainer[Arg]
    enable: bool
    def __init__(self, arg: _Optional[_Iterable[_Union[Arg, _Mapping]]] = ..., enable: bool = ...) -> None: ...

class FieldDefaults(_message.Message):
    __slots__ = ("float", "double", "int32", "int64", "uint32", "uint64", "sint32", "sint64", "fixed32", "fixed64", "sfixed32", "sfixed64", "bool", "string", "bytes", "enum")
    FLOAT_FIELD_NUMBER: _ClassVar[int]
    DOUBLE_FIELD_NUMBER: _ClassVar[int]
    INT32_FIELD_NUMBER: _ClassVar[int]
    INT64_FIELD_NUMBER: _ClassVar[int]
    UINT32_FIELD_NUMBER: _ClassVar[int]
    UINT64_FIELD_NUMBER: _ClassVar[int]
    SINT32_FIELD_NUMBER: _ClassVar[int]
    SINT64_FIELD_NUMBER: _ClassVar[int]
    FIXED32_FIELD_NUMBER: _ClassVar[int]
    FIXED64_FIELD_NUMBER: _ClassVar[int]
    SFIXED32_FIELD_NUMBER: _ClassVar[int]
    SFIXED64_FIELD_NUMBER: _ClassVar[int]
    BOOL_FIELD_NUMBER: _ClassVar[int]
    STRING_FIELD_NUMBER: _ClassVar[int]
    BYTES_FIELD_NUMBER: _ClassVar[int]
    ENUM_FIELD_NUMBER: _ClassVar[int]
    float: float
    double: float
    int32: int
    int64: int
    uint32: int
    uint64: int
    sint32: int
    sint64: int
    fixed32: int
    fixed64: int
    sfixed32: int
    sfixed64: int
    bool: bool
    string: str
    bytes: bytes
    enum: str
    def __init__(self, float: _Optional[float] = ..., double: _Optional[float] = ..., int32: _Optional[int] = ..., int64: _Optional[int] = ..., uint32: _Optional[int] = ..., uint64: _Optional[int] = ..., sint32: _Optional[int] = ..., sint64: _Optional[int] = ..., fixed32: _Optional[int] = ..., fixed64: _Optional[int] = ..., sfixed32: _Optional[int] = ..., sfixed64: _Optional[int] = ..., bool: bool = ..., string: _Optional[str] = ..., bytes: _Optional[bytes] = ..., enum: _Optional[str] = ...) -> None: ...
