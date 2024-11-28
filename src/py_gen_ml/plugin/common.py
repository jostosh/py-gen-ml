import re
import textwrap
import typing
from typing import Final, Literal, Optional, Set, TypeVar, Union

import google.protobuf.json_format
import more_itertools
import networkx
import protogen
from google.protobuf.descriptor import FieldDescriptor

from py_gen_ml.extensions_pb2 import FieldDefaults
from py_gen_ml.logging.setup_logger import setup_logger
from py_gen_ml.typing.some import some

logger = setup_logger(__name__)

WRAP_WIDTH: Final[int] = 84

T = TypeVar('T')


def get_extension_value(
    element: Union[protogen.Field, protogen.Message, protogen.File],
    extension_name: str,
    extension_type: type[T],
) -> Optional[T]:
    """
    Get the value of an extension field from the proto options.

    This function searches for an extension field with the given name in the
    options of the provided element (which can be a Field, Message, or File).
    If found, it returns the value of the extension field. Otherwise, it returns None.

    Args:
        element (typing.Union[protogen.Field, protogen.Message, protogen.File]): The element to search for the extension field.
        extension_name (str): The name of the extension field to search for.
        extension_type (type[T]): The type of the extension field.

    Returns:
        Optional[T]: The value of the extension field if found, otherwise None.
    """
    option: typing.Optional[tuple[FieldDescriptor, T]] = more_itertools.first_true(
        element.proto.options.ListFields(),
        None,
        lambda x: x[0].name == extension_name,
    )

    if option is None:
        return None
    return option[1]


def field_to_default(field: protogen.Field, import_prefix: str = '') -> typing.Optional[str]:
    """
    Convert the default value of a field to its corresponding Python representation.

    This function retrieves the default value of a field using the `FieldDefaults`
    extension and converts it to its Python string representation. The conversion
    depends on the type of the field (e.g., int, float, string, etc.).

    Args:
        field (protogen.Field): The field to get the default value for.
        import_prefix (str): The prefix to use for imports in the generated code.

    Returns:
        Optional[str]: The default value of the field as a Python string, or None if no default is set.
    """
    proto_default = get_extension_value(field, 'default', FieldDefaults)
    if proto_default is None:
        return None
    if field.kind == protogen.Kind.DOUBLE:
        default_field_name = 'double'
        default_value = proto_default.double
    elif field.kind == protogen.Kind.FLOAT:
        default_field_name = 'float'
        default_value = proto_default.float
    elif field.kind == protogen.Kind.INT64:
        default_field_name = 'int64'
        default_value = proto_default.int64
    elif field.kind == protogen.Kind.UINT64:
        default_field_name = 'uint64'
        default_value = proto_default.uint64
    elif field.kind == protogen.Kind.INT32:
        default_field_name = 'int32'
        default_value = proto_default.int32
    elif field.kind == protogen.Kind.FIXED64:
        default_field_name = 'fixed64'
        default_value = proto_default.fixed64
    elif field.kind == protogen.Kind.FIXED32:
        default_field_name = 'fixed32'
        default_value = proto_default.fixed32
    elif field.kind == protogen.Kind.BOOL:
        default_field_name = 'bool'
        default_value = proto_default.bool
    elif field.kind == protogen.Kind.STRING:
        default_field_name = 'string'
        default_value = f"\"{proto_default.string}\""
    elif field.kind == protogen.Kind.BYTES:
        default_field_name = 'bytes'
        default_value = proto_default.bytes
    elif field.kind == protogen.Kind.UINT32:
        default_field_name = 'uint32'
        default_value = proto_default.uint32
    elif field.kind == protogen.Kind.SFIXED32:
        default_field_name = 'sfixed32'
        default_value = proto_default.sfixed32
    elif field.kind == protogen.Kind.SFIXED64:
        default_field_name = 'sfixed64'
        default_value = proto_default.sfixed64
    elif field.kind == protogen.Kind.SINT32:
        default_field_name = 'sint32'
        default_value = proto_default.sint32
    elif field.kind == protogen.Kind.SINT64:
        default_field_name = 'sint64'
        default_value = proto_default.sint64
    elif field.kind == protogen.Kind.ENUM:
        default_field_name = 'enum'
        enum = some(field.enum)
        names = [v.name for v in enum.proto.value]
        if proto_default.enum not in names:
            raise ValueError(f'Invalid enum value: {proto_default.enum}')
        default_value = f'{import_prefix}{enum.py_ident.py_name}.{proto_default.enum}'
    else:
        raise ValueError(f'Default not supported for kind: {field.kind}')
    if field.kind in {
        protogen.Kind.FLOAT,
        protogen.Kind.DOUBLE,
    }:
        as_json = google.protobuf.json_format.MessageToJson(field.proto.options, indent=None)
        pattern = re.compile(rf'"{default_field_name}"\s*:\s*([+-]?\d*(?:\.\d+)?)')
        default_value = some(pattern.search(as_json)).group(1)
    return str(default_value) if default_value is not None else None


def generate_docstring(
    g: protogen.GeneratedFile,
    element: Union[protogen.Field, protogen.Message, protogen.Enum, protogen.EnumValue, protogen.OneOf],
) -> None:
    """
    Generate a docstring for the given element.

    This function generates a docstring for the provided element (which can be a Field, Message, Enum, or EnumValue).
    It wraps the leading comments of the element and formats them as a Python docstring.

    Args:
        g (protogen.GeneratedFile): The generated file to write the docstring to.
        element (Union[protogen.Field, protogen.Message, protogen.Enum, protogen.EnumValue]): The element to generate a docstring for.
    """
    if not element.location.leading_comments:
        return

    if WRAP_WIDTH - 6 - 4 >= len(element.location.leading_comments):
        g.P(f'"""{element.location.leading_comments}"""')
    else:
        g.P('"""')
        lines = textwrap.wrap(element.location.leading_comments, width=WRAP_WIDTH - 4)
        for line in lines:
            g.P(line)
        g.P('"""')
    g.P()


def get_element_subgraphs(
    file: protogen.File,
    include_elements: Optional[Set[Literal[protogen.Kind.MESSAGE, protogen.Kind.ENUM]]] = None,
) -> list[networkx.MultiDiGraph]:
    """
    Get the message subgraphs from a file.

    This function creates a multi-directed graph of messages and their dependencies.
    It adds nodes for each message and edges for each field that is a message type.
    The function then returns the connected components of the graph as subgraphs.

    Args:
        file (protogen.File): The file to get the message subgraphs from.

    Returns:
        List[networkx.MultiDiGraph]: The list of message subgraphs.
    """
    if include_elements is None:
        include_elements = {protogen.Kind.MESSAGE}
    graph = networkx.MultiDiGraph()
    for message in file.messages:
        graph.add_node(message)
        for field in message.fields:
            if field.kind not in include_elements:
                continue
            field_name = field.py_name
            if field.oneof is not None:
                field_name = field.oneof.proto.name
            if field.kind == protogen.Kind.MESSAGE:
                graph.add_edge(field.message, message, key=field_name)
            elif field.kind == protogen.Kind.ENUM:
                graph.add_edge(field.enum, message, key=field_name)
            else:
                raise ValueError(f'Unsupported field kind: {field.kind}')
    return [graph.subgraph(c).copy() for c in networkx.connected_components(graph.to_undirected())]  # type: ignore


def snake_case(name: str) -> str:
    """
    Convert a string to snake case.

    This function converts the given string to snake case by:
    1. Inserting underscores between transitions from lowercase to uppercase
    2. Inserting underscores between transitions from uppercase to lowercase (if not at the start of a word)
    3. Replacing spaces and punctuation with underscores
    4. Converting all characters to lowercase

    Args:
        name (str): The string to convert to snake case.

    Returns:
        str: The snake case version of the input string.
    """
    # Insert underscore between lowercase and uppercase transitions
    name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)

    # Insert underscore between uppercase and lowercase transitions (not at the start of a word)
    name = re.sub(r'([A-Z])([A-Z][a-z])', r'\1_\2', name)

    # Replace any remaining non-alphanumeric characters with underscores
    name = re.sub(r'[^a-zA-Z0-9]+', '_', name)

    # Convert to lowercase
    return name.lower()


def py_import_for_source_file_derived_file(file: protogen.GeneratedFile, name: str) -> str:
    """
    Get the Python import path for a file derived from a source file.

    This function returns the Python import path for a file that is derived from the
    given source file. The derived file is typically a version of the source file
    with a different extension or suffix.

    Args:
        file (protogen.File): The source file.
        name (str): The name of the derived file.

    Returns:
        str: The Python import path for the derived file.
    """
    return file._py_import_path._path.replace('_pb2', f'{name}')


def field_requires_typing_import(field: protogen.Field) -> bool:
    """
    Determine if field requires a typing import.

    Will be True if any of the following is true:
    - Field is part of a oneof
    - Field is optional
    - Field is repeated

    Args:
        field (protogen.Field): Field to check.

    Returns:
        bool: True if annotating the field requires a typing import
    """
    if field.oneof is not None:
        return True
    if field.proto.proto3_optional:
        return True
    if field.is_list():
        return True
    return False
