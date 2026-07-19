from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MessageKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MESSAGE_KIND_UNSPECIFIED: _ClassVar[MessageKind]
    FEATURE_ROW: _ClassVar[MessageKind]
    LABEL: _ClassVar[MessageKind]
    PREDICTION: _ClassVar[MessageKind]
    FEEDBACK: _ClassVar[MessageKind]
    RUN_CONFIG: _ClassVar[MessageKind]
    METRIC_SET: _ClassVar[MessageKind]

class ArgillaSlot(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ARGILLA_SLOT_UNSPECIFIED: _ClassVar[ArgillaSlot]
    FIELD: _ClassVar[ArgillaSlot]
    QUESTION: _ClassVar[ArgillaSlot]
    METADATA: _ClassVar[ArgillaSlot]

class TrackingSlot(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TRACKING_SLOT_UNSPECIFIED: _ClassVar[TrackingSlot]
    PARAM: _ClassVar[TrackingSlot]
    METRIC: _ClassVar[TrackingSlot]
    TAG: _ClassVar[TrackingSlot]
MESSAGE_KIND_UNSPECIFIED: MessageKind
FEATURE_ROW: MessageKind
LABEL: MessageKind
PREDICTION: MessageKind
FEEDBACK: MessageKind
RUN_CONFIG: MessageKind
METRIC_SET: MessageKind
ARGILLA_SLOT_UNSPECIFIED: ArgillaSlot
FIELD: ArgillaSlot
QUESTION: ArgillaSlot
METADATA: ArgillaSlot
TRACKING_SLOT_UNSPECIFIED: TrackingSlot
PARAM: TrackingSlot
METRIC: TrackingSlot
TAG: TrackingSlot
ENABLE_FIELD_NUMBER: _ClassVar[int]
enable: _descriptor.FieldDescriptor
FACTORY_FIELD_NUMBER: _ClassVar[int]
factory: _descriptor.FieldDescriptor
CLI_FIELD_NUMBER: _ClassVar[int]
cli: _descriptor.FieldDescriptor
LANCEDB_FIELD_NUMBER: _ClassVar[int]
lancedb: _descriptor.FieldDescriptor
KIND_FIELD_NUMBER: _ClassVar[int]
kind: _descriptor.FieldDescriptor
BENTOML_CONFIG_FIELD_NUMBER: _ClassVar[int]
bentoml_config: _descriptor.FieldDescriptor
LITSERVE_CONFIG_FIELD_NUMBER: _ClassVar[int]
litserve_config: _descriptor.FieldDescriptor
PYDANTIC_AI_FIELD_NUMBER: _ClassVar[int]
pydantic_ai: _descriptor.FieldDescriptor
ARGILLA_FIELD_NUMBER: _ClassVar[int]
argilla: _descriptor.FieldDescriptor
MAPPER_CONFIG_FIELD_NUMBER: _ClassVar[int]
mapper_config: _descriptor.FieldDescriptor
MLFLOW_FIELD_NUMBER: _ClassVar[int]
mlflow: _descriptor.FieldDescriptor
WANDB_FIELD_NUMBER: _ClassVar[int]
wandb: _descriptor.FieldDescriptor
BENTOML_FIELD_NUMBER: _ClassVar[int]
bentoml: _descriptor.FieldDescriptor
LITSERVE_FIELD_NUMBER: _ClassVar[int]
litserve: _descriptor.FieldDescriptor
BENTOML_METHOD_FIELD_NUMBER: _ClassVar[int]
bentoml_method: _descriptor.FieldDescriptor
LITSERVE_METHOD_FIELD_NUMBER: _ClassVar[int]
litserve_method: _descriptor.FieldDescriptor
DEFAULT_FIELD_NUMBER: _ClassVar[int]
default: _descriptor.FieldDescriptor
AS_VARARGS_FIELD_NUMBER: _ClassVar[int]
as_varargs: _descriptor.FieldDescriptor
LANCEDB_FIELD_FIELD_NUMBER: _ClassVar[int]
lancedb_field: _descriptor.FieldDescriptor
ARGILLA_FIELD_FIELD_NUMBER: _ClassVar[int]
argilla_field: _descriptor.FieldDescriptor
MAPPER_FIELD_FIELD_NUMBER: _ClassVar[int]
mapper_field: _descriptor.FieldDescriptor
TRACKING_FIELD_FIELD_NUMBER: _ClassVar[int]
tracking_field: _descriptor.FieldDescriptor

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

class LanceDB(_message.Message):
    __slots__ = ("enable", "table_name")
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    enable: bool
    table_name: str
    def __init__(self, enable: bool = ..., table_name: _Optional[str] = ...) -> None: ...

class LanceDBField(_message.Message):
    __slots__ = ("vector_dim", "merge_key")
    VECTOR_DIM_FIELD_NUMBER: _ClassVar[int]
    MERGE_KEY_FIELD_NUMBER: _ClassVar[int]
    vector_dim: int
    merge_key: bool
    def __init__(self, vector_dim: _Optional[int] = ..., merge_key: bool = ...) -> None: ...

class BentoML(_message.Message):
    __slots__ = ("enable", "name")
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    enable: bool
    name: str
    def __init__(self, enable: bool = ..., name: _Optional[str] = ...) -> None: ...

class BentoMLMethod(_message.Message):
    __slots__ = ("route", "name", "batchable")
    ROUTE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    BATCHABLE_FIELD_NUMBER: _ClassVar[int]
    route: str
    name: str
    batchable: bool
    def __init__(self, route: _Optional[str] = ..., name: _Optional[str] = ..., batchable: bool = ...) -> None: ...

class BentoMLConfig(_message.Message):
    __slots__ = ("enable", "service")
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    enable: bool
    service: str
    def __init__(self, enable: bool = ..., service: _Optional[str] = ...) -> None: ...

class LitServe(_message.Message):
    __slots__ = ("enable", "name")
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    enable: bool
    name: str
    def __init__(self, enable: bool = ..., name: _Optional[str] = ...) -> None: ...

class LitServeMethod(_message.Message):
    __slots__ = ("api_path",)
    API_PATH_FIELD_NUMBER: _ClassVar[int]
    api_path: str
    def __init__(self, api_path: _Optional[str] = ...) -> None: ...

class LitServeConfig(_message.Message):
    __slots__ = ("enable", "service")
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    enable: bool
    service: str
    def __init__(self, enable: bool = ..., service: _Optional[str] = ...) -> None: ...

class PydanticAI(_message.Message):
    __slots__ = ("enable", "agent_name", "response_message")
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    AGENT_NAME_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    enable: bool
    agent_name: str
    response_message: str
    def __init__(self, enable: bool = ..., agent_name: _Optional[str] = ..., response_message: _Optional[str] = ...) -> None: ...

class Argilla(_message.Message):
    __slots__ = ("enable", "dataset_name")
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    DATASET_NAME_FIELD_NUMBER: _ClassVar[int]
    enable: bool
    dataset_name: str
    def __init__(self, enable: bool = ..., dataset_name: _Optional[str] = ...) -> None: ...

class ArgillaField(_message.Message):
    __slots__ = ("slot", "name", "field_type", "question_type", "labels", "required")
    SLOT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    FIELD_TYPE_FIELD_NUMBER: _ClassVar[int]
    QUESTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_FIELD_NUMBER: _ClassVar[int]
    slot: ArgillaSlot
    name: str
    field_type: str
    question_type: str
    labels: _containers.RepeatedScalarFieldContainer[str]
    required: bool
    def __init__(self, slot: _Optional[_Union[ArgillaSlot, str]] = ..., name: _Optional[str] = ..., field_type: _Optional[str] = ..., question_type: _Optional[str] = ..., labels: _Optional[_Iterable[str]] = ..., required: bool = ...) -> None: ...

class MapperConfig(_message.Message):
    __slots__ = ("enable",)
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    enable: bool
    def __init__(self, enable: bool = ...) -> None: ...

class MapperField(_message.Message):
    __slots__ = ("alias",)
    ALIAS_FIELD_NUMBER: _ClassVar[int]
    alias: str
    def __init__(self, alias: _Optional[str] = ...) -> None: ...

class TrackingField(_message.Message):
    __slots__ = ("slot", "name")
    SLOT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    slot: TrackingSlot
    name: str
    def __init__(self, slot: _Optional[_Union[TrackingSlot, str]] = ..., name: _Optional[str] = ...) -> None: ...

class MLflow(_message.Message):
    __slots__ = ("enable", "experiment_name", "run_name_field", "registered_model_name", "signature_input", "signature_output")
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    RUN_NAME_FIELD_FIELD_NUMBER: _ClassVar[int]
    REGISTERED_MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_INPUT_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_OUTPUT_FIELD_NUMBER: _ClassVar[int]
    enable: bool
    experiment_name: str
    run_name_field: str
    registered_model_name: str
    signature_input: str
    signature_output: str
    def __init__(self, enable: bool = ..., experiment_name: _Optional[str] = ..., run_name_field: _Optional[str] = ..., registered_model_name: _Optional[str] = ..., signature_input: _Optional[str] = ..., signature_output: _Optional[str] = ...) -> None: ...

class Wandb(_message.Message):
    __slots__ = ("enable", "project", "run_name_field")
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    RUN_NAME_FIELD_FIELD_NUMBER: _ClassVar[int]
    enable: bool
    project: str
    run_name_field: str
    def __init__(self, enable: bool = ..., project: _Optional[str] = ..., run_name_field: _Optional[str] = ...) -> None: ...

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
