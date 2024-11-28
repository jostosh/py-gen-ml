from __future__ import annotations

import re
from dataclasses import dataclass, field, replace
from typing import Any, Dict, Final, Optional, TypeVar

from pydantic import BaseModel
from pydantic.json_schema import GenerateJsonSchema, JsonSchemaMode
from pydantic_core.core_schema import CoreSchema

INTERNAL_OBJECT_PATH_PATTERN: Final[
    str] = r'^#\/?(?:[\$a-zA-Z0-9_]+(?:\[\d+\])?|\.\.)(?:\/([a-zA-Z0-9_]+(?:\[\d+\])?|\.\.))*$'  # noqa: E501
INTERNAL_OBJECT_PATH_REGEX: Final = re.compile(INTERNAL_OBJECT_PATH_PATTERN)
EXTERNAL_OBJECT_PATH_PATTERN: Final[
    str
] = r'^\!(\/?(?:[\w\.]+|\.\.)+(?:/(?:[\w\.]+|\.\.))*)' + f'({INTERNAL_OBJECT_PATH_PATTERN[1:-1]})?$'  # noqa: E501
EXTERNAL_OBJECT_PATH_REGEX: Final = re.compile(EXTERNAL_OBJECT_PATH_PATTERN)

TBaseModel = TypeVar('TBaseModel', bound=BaseModel)


@dataclass
class ObjectStep:
    """A step in an object path."""

    name: str
    """The name of the step."""

    index: Optional[int] = None
    """The index of the step."""


@dataclass
class ObjectPath:
    """A path to an object."""

    steps: list[ObjectStep] = field(default_factory=list)
    """The steps to the object."""

    is_absolute: bool = False
    """Whether the path is absolute."""

    def add_step(self, name: str) -> ObjectPath:
        """
        Add a step to the object path.

        Args:
            name (str): The name of the step to add.

        Returns:
            ObjectPath: The object path with the added step.
        """
        return replace(self, steps=self.steps.copy() + [ObjectStep(name=name)])

    def add_index_step(self, index: int) -> ObjectPath:
        """
        Add an index step to the object path.

        Args:
            index (int): The index to add.

        Returns:
            ObjectPath: The object path with the added index step.
        """
        if len(self.steps) == 0:
            raise ValueError('Cannot add an index step to an empty path')
        steps = self.steps.copy()
        steps[-1].index = index
        return replace(self, steps=steps)

    @classmethod
    def from_string(cls, path: str) -> ObjectPath:
        """
        Create an object path from a string.

        Args:
            path (str): The path to create.

        Returns:
            ObjectPath: The created object path.
        """
        steps: list[ObjectStep] = []

        path = path.removeprefix('#')
        if path.startswith('/'):
            is_absolute = True
        else:
            is_absolute = False
        for part in path.removeprefix('/').split('/'):
            key = None

            int_key_regex = re.compile(r'^(\w+)\[(\d+)\]$')  # matches "key[0]"
            if (match := int_key_regex.match(part)) is not None:
                part, key = match.groups()
                key = int(key)
            steps.append(ObjectStep(name=part, index=key))
        return cls(steps=steps, is_absolute=is_absolute)

    def concat(self, other: ObjectPath) -> ObjectPath:
        """
        Concatenate two object paths.

        Args:
            other (ObjectPath): The other object path to concatenate.

        Returns:
            ObjectPath: The concatenated object path.
        """
        if other.is_absolute:
            return other
        return ObjectPath(steps=self.steps.copy() + other.steps.copy())


def resolve_inner_ref(root: Dict[str, Any], path_to_ref: ObjectPath, path_at_ref: ObjectPath) -> Any:
    """
    Resolve a reference in a nested structure that is rooted at `root`.

    Args:
        root (Dict[str, Any]): The root of the nested structure.
        path_to_ref (ObjectPath): The path to the reference.
        path_at_ref (ObjectPath): The path at the reference.

    Returns:
        Any: The resolved value.
    """
    path_to_ref = ObjectPath(path_to_ref.steps.copy()[:-1])  # remove the last step, as it is the reference to itself
    while len(path_at_ref.steps) > 0 and len(path_to_ref.steps) > 0 and path_at_ref.steps[0].name == '..':
        path_at_ref = ObjectPath(steps=path_at_ref.steps.copy()[1:])
        path_to_ref = ObjectPath(steps=path_to_ref.steps.copy()[:-1])

    path = path_to_ref.concat(path_at_ref)

    current = root
    for step in path.steps:
        try:
            current = current[step.name]
        except KeyError:
            raise ValueError(f'Key {step.name} not found in {current}')
        if step.index is not None:
            current = current[step.index]
    return current


class InsertAnyOfWithObjectPath(GenerateJsonSchema):
    """
    A class that inserts anyOf with object path schemas into a JSON schema.

    With the injected schema, one can add references to objects within a YAML file. The references
    can be internal and external.
    """

    def generate(
        self,
        schema: CoreSchema,
        mode: JsonSchemaMode = 'validation',
    ) -> Dict[str, Any]:
        """
        Generate a JSON schema with anyOf with object path schemas.

        Args:
            schema (Dict[str, Any]): The schema to generate the anyOf with object path schemas for.
            mode (str): The mode to generate the schema for.

        Returns:
            Dict[str, Any]: The generated schema.
        """
        json_schema = super().generate(schema, mode)
        self._traverse_properties(json_schema['properties'], mode)
        for definition in json_schema.get('$defs', {}).values():
            if 'properties' not in definition:
                continue
            self._traverse_properties(definition['properties'], mode)

        json_schema['properties']['_defs_'] = {}
        return json_schema

    def _get_external_object_path_schema(self) -> Dict[str, Any]:
        return {
            'type': 'string',
            'description': 'An object path to an external object',
            'minLength': 2,
            'pattern': EXTERNAL_OBJECT_PATH_PATTERN,
        }

    def _get_internal_object_path_schema(self) -> Dict[str, Any]:
        return {
            'type': 'string',
            'description': 'An object path to an internal object',
            'minLength': 2,
            'pattern': INTERNAL_OBJECT_PATH_PATTERN,
        }

    def _traverse_properties(self, properties: Dict[str, Any], mode: str) -> None:
        # Traverse the schema and insert the object path schema
        for property in properties.values():
            if 'anyOf' in property:
                property['anyOf'].append(self._get_external_object_path_schema())
                property['anyOf'].append(self._get_internal_object_path_schema())
            else:
                inner_values = property.copy()
                if inner_values.get('type') == 'array':
                    property['items'] = {
                        'anyOf': [
                            inner_values['items'].copy(),
                            self._get_external_object_path_schema(),
                            self._get_internal_object_path_schema(),
                        ],
                    }
                else:
                    property.clear()
                    property['anyOf'] = [
                        inner_values,
                        self._get_external_object_path_schema(),
                        self._get_internal_object_path_schema(),
                    ]
