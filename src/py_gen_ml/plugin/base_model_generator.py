from pathlib import Path
from typing import List, Set, TypeVar

import networkx
import protogen

from py_gen_ml.logging.setup_logger import setup_logger
from py_gen_ml.plugin.common import (
    field_to_default,
    generate_docstring,
    get_element_subgraphs,
    get_extension_value,
    py_import_for_source_file_derived_file,
    snake_case,
)
from py_gen_ml.plugin.constants import BASE_MODEL_ALIAS, PGML_ALIAS
from py_gen_ml.plugin.generator import Generator
from py_gen_ml.typing.some import some

logger = setup_logger(__name__)

T = TypeVar('T')


class BaseModelGenerator(Generator):
    """
    A generator that creates base models for a set of protobuf files.

    The generated file will be imported by the py-gen-ml CLI to generate base models for the given protobuf files.
    """

    def __init__(self, gen: protogen.Plugin, is_patch: bool, suffix: str) -> None:
        """
        Initialize the BaseModelGenerator.

        Args:
            gen (protogen.Plugin): The plugin instance.
            is_patch (bool): Whether this is a patch model.
            suffix (str): The suffix for the generated file.
        """
        super().__init__(gen)
        self._suffix = suffix
        self._is_patch = is_patch

    def _generate_code_for_file(self, file: protogen.File) -> None:
        """
        Generate base models for a specific file.

        This method creates a new generated file for the base models of the given file.
        It imports necessary modules and defines the base models for all messages and enums.
        """
        g = self._gen.new_generated_file(
            file.proto.name.replace('.proto', self._suffix),
            file.py_import_path,
        )
        g.P('# Autogenerated code. DO NOT EDIT.')
        if self._is_patch or self._requires_typing_import(file):
            g.P('import typing')
        if len(file.enums) > 0 and not self._is_patch:
            g.P('import enum')
            g.P()
        g.P(f'import py_gen_ml as {PGML_ALIAS}')
        g.P()
        if not self._is_patch and len(builder_imports := self.gather_factory_imports(file)) > 0:
            g.P('from typing import TYPE_CHECKING')
            g.P()
            g.P('if TYPE_CHECKING:')
            g.set_indent(4)
            for builder_import in builder_imports:
                g.P(f'import {builder_import}')
            g.set_indent(0)
            g.P()

        if self._is_patch and len(file.enums) > 0:
            import_file_path = str(Path(file.proto.name.replace('.proto', '_base')).name)
            g.P(f'from . import {import_file_path} as {BASE_MODEL_ALIAS}')
            g.P()
        g.P()

        dependency_subgraphs = get_element_subgraphs(file, include_elements={protogen.Kind.ENUM, protogen.Kind.MESSAGE})
        if not self._is_patch:
            for subgraph in dependency_subgraphs:
                for message in networkx.topological_sort(subgraph):
                    if not isinstance(message, protogen.Enum):
                        continue
                    self._generate_enum_base_model(g, message)

        for subgraph in dependency_subgraphs:
            for message in networkx.topological_sort(subgraph):
                if not isinstance(message, protogen.Message):
                    continue
                self._generate_message_base_model(g, message)

        self._run_yapf(g)

    def _generate_enum_base_model(self, g: protogen.GeneratedFile, enum: protogen.Enum) -> None:
        """
        Generate the base model for an enum.

        This method generates the class definition for the base model of the given enum.
        It includes the class name, inheritance, and docstring.
        """
        g.P(f'class {enum.proto.name}(str, enum.Enum):')
        g.set_indent(4)
        generate_docstring(g, enum)

        for value in enum.values:
            g.P(f"{value.proto.name} = \"{value.proto.name}\"")
            generate_docstring(g, value)

        g.set_indent(0)
        g.P()
        g.P()

    def _generate_message_base_model(self, g: protogen.GeneratedFile, message: protogen.Message) -> None:
        """
        Generate the base model for a message.

        This method generates the class definition for the base model of the given message.
        It includes the class name, inheritance, and docstring.
        """
        patch = 'Patch' if self._is_patch else ''
        g.P(f'class {message.proto.name}{patch}({PGML_ALIAS}.YamlBaseModel):')
        g.set_indent(4)
        generate_docstring(g, message)

        for field in message.fields:
            if field.oneof and len(field.oneof.fields) > 1:
                continue
            g.P(f'{field.py_name}: {self.field_to_annotation(field)}')
            generate_docstring(g, field)

        # Add oneof fields
        for oneof in message.oneofs:
            if len(oneof.fields) == 1:
                continue
            self._generate_oneof_field(g, oneof)

        if self._is_patch:
            g.set_indent(0)
            g.P()
            g.P()

            self._add_json_schema_gen_task(
                obj_path=py_import_for_source_file_derived_file(g, '_patch'),
                obj_name=message.py_ident.py_name + 'Patch',
                path=f'{self._configs_dir}/patch/schemas/' + snake_case(message.proto.name) + '.json',
            )
            return

        if (builder_import_path := get_extension_value(message, 'factory', str)) is not None:
            dot_index = builder_import_path.rfind('.')
            if dot_index == -1:
                raise ValueError(f'Invalid builder import path: {builder_import_path}')

            g.P()
            g.P("def build(self) -> \"", builder_import_path, "\":")

            g.set_indent(8)
            if (idx := builder_import_path.rfind('.')) == -1:
                raise ValueError(f'Invalid builder import {builder_import_path}')
            g.P('import ', builder_import_path[:idx])
            g.P()
            g.P('return ', builder_import_path, '(')

            g.set_indent(12)
            for field in message.fields:
                if ((field_message := field.message) is not None and
                    get_extension_value(field_message, 'factory', str) is not None):
                    build_field = True
                else:
                    build_field = False

                as_varargs = get_extension_value(field, 'as_varargs', bool) or False
                is_list = field.is_list()
                if as_varargs and build_field and is_list:
                    g.P(f'*(elem.build() for elem in self.{field.py_name}),')
                elif not as_varargs and build_field and is_list:
                    g.P(f'{field.py_name}=[elem.build() for elem in self.{field.py_name}],')
                elif not as_varargs and build_field and not is_list:
                    g.P(f'{field.py_name}=self.{field.py_name}.build(),')
                elif not as_varargs and not build_field:
                    g.P(field.py_name, '=self.', field.py_name, ',')
                else:
                    raise ValueError(f'Unsupported case {message.full_name}.{field.py_name}')

            g.set_indent(8)
            g.P(')')

            g.set_indent(4)

        g.set_indent(0)
        g.P()
        g.P()

        self._add_json_schema_gen_task(
            obj_path=py_import_for_source_file_derived_file(g, '_base'),
            obj_name=message.py_ident.py_name,
            path=f'{self._configs_dir}/base/schemas/' + snake_case(message.proto.name) + '.json',
        )

    def _generate_oneof_field(self, g: protogen.GeneratedFile, oneof: protogen.OneOf) -> None:
        """
        Generate the base model for a oneof field.

        This method generates the class definition for the base model of the given oneof field.
        It includes the class name, inheritance, and docstring.

        Args:
            g (protogen.GeneratedFile): The generated file to write to.
            oneof (protogen.OneOf): The oneof field to generate the base model for.
        """
        oneof_name = oneof.proto.name
        g.P(f'{oneof_name}: {self.oneof_to_annotation(oneof)}')
        generate_docstring(g, oneof)

    def oneof_to_annotation(self, oneof: protogen.OneOf) -> str:
        """
        Convert the oneof field to its corresponding annotation.

        This method determines the appropriate annotation for the given oneof field.
        It returns the annotation as a string.

        Args:
            oneof (protogen.OneOf): The oneof field to convert to an annotation.

        Returns:
            str: The annotation for the oneof field.
        """
        if len(oneof.fields) == 1:
            return self.field_to_type(oneof.fields[0])
        types = [self.field_to_type(field) for field in oneof.fields]
        union_type = ', '.join(types)
        return f'typing.Union[{union_type}]'

    @staticmethod
    def gather_factory_imports(file: protogen.File) -> List[str]:
        """
        Gather the builder imports for a specific file.

        This method collects the import paths for the factories of all messages in the given file.
        It ensures that each builder import path is unique and returns a sorted list of these paths.

        Args:
            file (protogen.File): The file to gather builder imports from.

        Returns:
            List[str]: A sorted list of unique builder import paths.
        """
        imports: Set[str] = set()
        for message in file.messages:
            factory_import_path = get_extension_value(message, 'factory', str)
            if factory_import_path is None:
                continue

            if (idx := factory_import_path.rfind('.')) == -1:
                raise ValueError(f'Invalid factory import {factory_import_path}')
            imports.add(factory_import_path[:idx])
        return sorted(imports)

    def field_to_annotation(self, field: protogen.Field) -> str:
        """
        Convert the field to its corresponding annotation.

        This method determines the appropriate annotation for the given field based on its type.
        It returns the annotation as a string.

        Args:
            field (protogen.Field): The field to convert to an annotation.

        Returns:
            str: The annotation for the field.
        """
        annotation = self.field_to_type(field)
        default = field_to_default(field)
        if field.is_list():
            annotation = f'typing.List[{annotation}]'
        if field.proto.proto3_optional or self._is_patch:
            annotation = f'typing.Optional[{annotation}]'
            if default is None or self._is_patch:
                default = 'None'

        if default is not None:
            return f'{annotation} = {default}'

        return annotation

    def field_to_type(self, field: protogen.Field) -> str:
        """
        Convert the field to its corresponding type.

        This method determines the appropriate type for the given field based on its kind.
        It returns the type as a string.

        Args:
            field (protogen.Field): The field to convert to a type.

        Returns:
            str: The type for the field.
        """
        if field.kind == protogen.Kind.MESSAGE:
            message = some(field.message)
            if self._is_patch:
                return message.py_ident.py_name + 'Patch'
            return message.py_ident.py_name
        elif field.kind == protogen.Kind.DOUBLE:
            return 'float'
        elif field.kind == protogen.Kind.FLOAT:
            return 'float'
        elif field.kind == protogen.Kind.INT64:
            return 'int'
        elif field.kind == protogen.Kind.UINT64:
            return 'int'
        elif field.kind == protogen.Kind.INT32:
            return 'int'
        elif field.kind == protogen.Kind.FIXED64:
            return 'int'
        elif field.kind == protogen.Kind.FIXED32:
            return 'int'
        elif field.kind == protogen.Kind.BOOL:
            return 'bool'
        elif field.kind == protogen.Kind.STRING:
            return 'str'
        elif field.kind == protogen.Kind.BYTES:
            return 'bytes'
        elif field.kind == protogen.Kind.UINT32:
            return 'int'
        elif field.kind == protogen.Kind.ENUM:
            enum = some(field.enum)
            if self._is_patch:
                return f'{BASE_MODEL_ALIAS}.{enum.py_ident.py_name}'
            return enum.py_ident.py_name
        elif field.kind == protogen.Kind.SFIXED32:
            return 'int'
        elif field.kind == protogen.Kind.SFIXED64:
            return 'int'
        elif field.kind == protogen.Kind.SINT32:
            return 'int'
        elif field.kind == protogen.Kind.SINT64:
            return 'int'
        else:
            raise ValueError(f'Unknown field kind: {field.kind}')
