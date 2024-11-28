from pathlib import Path
from typing import TypeVar

import networkx
import protogen

from py_gen_ml.plugin.common import (
    generate_docstring,
    get_element_subgraphs,
    py_import_for_source_file_derived_file,
    snake_case,
)
from py_gen_ml.plugin.constants import (
    BASE_MODEL_ALIAS,
    PATCH_MODEL_ALIAS,
    PGML_ALIAS,
)
from py_gen_ml.plugin.generator import Generator
from py_gen_ml.typing.some import some

T = TypeVar('T')


class SweepModelGenerator(Generator):
    """
    Initialize the SweepModelGenerator.

    Args:
        gen (protogen.Plugin): The protogen plugin instance.
        suffix (str): The suffix to be added to the generated file names.

    This class is responsible for generating sweep models based on the input protobuf files.
    Sweep models are used to parameterize the values of fields in a message.
    """

    def __init__(self, gen: protogen.Plugin, suffix: str) -> None:
        """
        Initialize the SweepModelGenerator.

        Args:
            gen (protogen.Plugin): The protogen plugin instance.
            suffix (str): The suffix to be added to the generated file names.

        This class is responsible for generating sweep models based on the input protobuf files.
        Sweep models are used to parameterize the values of fields in a message.
        """
        super().__init__(gen)
        self._suffix = suffix

    def _generate_code_for_file(self, file: protogen.File) -> None:
        """
        Generate sweep models for a specific file.

        This method creates a new generated file for the sweep models of the given file.
        It imports necessary modules and defines the sweep models for all messages and enums.
        """
        g = self._gen.new_generated_file(
            file.proto.name.replace('.proto', self._suffix),
            file.py_import_path,
        )
        g.P('import typing')
        g.P()
        g.P(f'import py_gen_ml as {PGML_ALIAS}')
        g.P()

        import_file_path = str(Path(file.proto.name.replace('.proto', '_patch')).name)
        g.P(f'from . import {import_file_path} as {PATCH_MODEL_ALIAS}')

        import_file_path = str(Path(file.proto.name.replace('.proto', '_base')).name)
        g.P(f'from . import {import_file_path} as {BASE_MODEL_ALIAS}')

        g.P()
        g.P()

        dependency_subgraphs = get_element_subgraphs(file, include_elements={protogen.Kind.ENUM, protogen.Kind.MESSAGE})

        for subgraph in dependency_subgraphs:
            for message in networkx.topological_sort(subgraph):
                if not isinstance(message, protogen.Enum):
                    continue
                self._generate_sweep_field_for_enum(g, message)

        for subgraph in dependency_subgraphs:
            for message in networkx.topological_sort(subgraph):
                if not isinstance(message, protogen.Message):
                    continue
                self._generate_sweep_model_for_message(g, message)
                g.P()
                g.P()
                self._generate_sweep_field_for_message(g, message)

    def _generate_sweep_model_for_message(self, g: protogen.GeneratedFile, message: protogen.Message) -> None:
        """
        Generate the sweep model for a specific message.

        This method generates the class definition for the sweep model of the given message.
        It includes the class name, inheritance, and docstring.

        Args:
            g (protogen.GeneratedFile): The generated file to write the sweep model to.
            message (protogen.Message): The message to generate the sweep model for.
        """
        prefix = PATCH_MODEL_ALIAS + '.'
        g.P(f'class {message.proto.name}Sweep({PGML_ALIAS}.Sweeper[{prefix}{message.proto.name}Patch]):')
        g.set_indent(4)
        generate_docstring(g, message)

        for field in message.fields:
            if field.oneof:
                continue
            g.P(f'{field.py_name}: {self.field_to_sweep_annotation(field)}')
            generate_docstring(g, field)

        # Add oneof fields
        for oneof in message.oneofs:
            self._generate_oneof_field(g, oneof)

        g.set_indent(0)

        self._add_json_schema_gen_task(
            obj_path=py_import_for_source_file_derived_file(g, '_sweep'),
            obj_name=f'{message.proto.name}Sweep',
            path=f'{self._configs_dir}/sweep/schemas/' + snake_case(message.proto.name) + '.json',
        )

        self._run_yapf(g)

    def _generate_sweep_field_for_enum(self, g: protogen.GeneratedFile, enum: protogen.Enum) -> None:
        """
        Generate the sweep field for a specific enum.

        This method generates the union type for the sweep field of the given enum.
        It includes the union of the enum sweep, fixed, and base model.

        Args:
            g (protogen.GeneratedFile): The generated file to write the sweep field to.
            enum (protogen.Enum): The enum to generate the sweep field for.
        """
        base_model = f'{BASE_MODEL_ALIAS}.{enum.proto.name}'

        g.P(f'{enum.proto.name}SweepField = typing.Union[')
        g.set_indent(4)
        g.P(f'{PGML_ALIAS}.Choice[{base_model}],')
        g.P(f"typing.Literal['any'],")
        g.P(f'{base_model},')
        g.set_indent(0)
        g.P(']')
        g.P()
        g.P()

    def _generate_sweep_field_for_message(self, g: protogen.GeneratedFile, message: protogen.Message) -> None:
        """
        Generate the sweep field for a specific message.

        This method generates the union type for the sweep field of the given message.
        It includes the union of the message sweep, nested choice, named choice, fixed, and base model.

        Args:
            g (protogen.GeneratedFile): The generated file to write the sweep field to.
            message (protogen.Message): The message to generate the sweep field for.
        """
        base_model = f'{message.proto.name}'

        base_model = f'{PATCH_MODEL_ALIAS}.{base_model}Patch'
        g.P(f'{message.proto.name}SweepField = typing.Union[')
        g.set_indent(4)
        g.P(f'{message.proto.name}Sweep,')
        g.P(f'{PGML_ALIAS}.NestedChoice[{message.proto.name}Sweep, {base_model}],  # type: ignore')
        g.set_indent(0)
        g.P(']')
        g.P()
        g.P()

    def field_to_sweep_annotation(self, field: protogen.Field) -> str:
        """
        Convert the field to its corresponding sweep annotation.

        This method determines the appropriate sweep annotation for the given field based on its type.
        It returns the sweep annotation as a string.

        Args:
            field (protogen.Field): The field to convert to its sweep annotation.

        Returns:
            str: The sweep annotation as a string.
        """
        annotation = self.field_to_sweep_type(field)
        return f'typing.Optional[{annotation}] = None'

    def field_to_sweep_type(self, field: protogen.Field) -> str:
        """
        Convert the field to its corresponding sweep type.

        This method determines the appropriate sweep type for the given field based on its type.
        It returns the sweep type as a string.

        Args:
            field (protogen.Field): The field to convert to its sweep type.

        Returns:
            str: The sweep type as a string.
        """
        if field.kind == protogen.Kind.MESSAGE:
            return some(field.message).py_ident.py_name + 'SweepField'
        elif field.kind == protogen.Kind.ENUM:
            return some(field.enum).py_ident.py_name + 'SweepField'
        elif field.kind == protogen.Kind.DOUBLE:
            return f'{PGML_ALIAS}.FloatSweep'
        elif field.kind == protogen.Kind.FLOAT:
            return f'{PGML_ALIAS}.FloatSweep'
        elif field.kind == protogen.Kind.INT64:
            return f'{PGML_ALIAS}.IntSweep'
        elif field.kind == protogen.Kind.UINT64:
            return f'{PGML_ALIAS}.IntSweep'
        elif field.kind == protogen.Kind.INT32:
            return f'{PGML_ALIAS}.IntSweep'
        elif field.kind == protogen.Kind.FIXED64:
            return f'{PGML_ALIAS}.IntSweep'
        elif field.kind == protogen.Kind.FIXED32:
            return f'{PGML_ALIAS}.IntSweep'
        elif field.kind == protogen.Kind.BOOL:
            return f'{PGML_ALIAS}.BoolSweep'
        elif field.kind == protogen.Kind.STRING:
            return f'{PGML_ALIAS}.StrSweep'
        elif field.kind == protogen.Kind.BYTES:
            return f'{PGML_ALIAS}.BytesSweep'
        elif field.kind == protogen.Kind.UINT32:
            return f'{PGML_ALIAS}.IntSweep'
        elif field.kind == protogen.Kind.SFIXED32:
            return f'{PGML_ALIAS}.IntSweep'
        elif field.kind == protogen.Kind.SFIXED64:
            return f'{PGML_ALIAS}.IntSweep'
        elif field.kind == protogen.Kind.SINT32:
            return f'{PGML_ALIAS}.IntSweep'
        elif field.kind == protogen.Kind.SINT64:
            return f'{PGML_ALIAS}.IntSweep'
        else:
            raise ValueError(f'Unknown field kind: {field.kind}')

    def _generate_oneof_field(self, g: protogen.GeneratedFile, oneof: protogen.OneOf) -> None:
        oneof_name = oneof.proto.name
        g.P(f'{oneof_name}: {self._oneof_to_annotation(oneof)}')
        generate_docstring(g, oneof)

    def _oneof_to_annotation(self, oneof: protogen.OneOf) -> str:
        types = [f'{PGML_ALIAS}.Sweeper[{self.field_to_sweep_type(field)}]' for field in oneof.fields]
        union_type = ', '.join(types)
        return f'typing.Optional[typing.Union[{union_type}]] = None'
