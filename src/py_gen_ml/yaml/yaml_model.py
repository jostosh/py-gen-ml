import pathlib
import warnings
from typing import Any, Dict, List

with warnings.catch_warnings():
    warnings.filterwarnings('ignore', category=DeprecationWarning, module='jsonmerge')
    import jsonmerge

from pydantic import BaseModel
from ruamel.yaml import YAML
from typing_extensions import Self

from py_gen_ml.cli_args.arg_refs import apply_args
from py_gen_ml.yaml.object_path import (
    EXTERNAL_OBJECT_PATH_REGEX,
    INTERNAL_OBJECT_PATH_REGEX,
    ObjectPath,
    resolve_inner_ref,
)

yaml = YAML()


class YamlBaseModel(BaseModel):
    """
    A base model that can be used to create instances of models from yaml files.

    This class augments the Pydantic base model with the ability to load data from yaml files. Moreover,
    it offers the ability to merge multiple yaml files into a single model. It also internally
    resolves references to other objects in the yaml files. Lastly, it offers the ability to
    apply cli arguments to the model.

    !!! info
        All Pydantic models that are generated using `py-gen-ml` will inherit from this class. So make sure to
        read the documentation on this class to fully leverage all the features of `py-gen-ml`.
    """

    @classmethod
    def from_yaml_file(cls, path: str) -> Self:
        """
        Create a new instance of the model from a yaml file.

        Args:
            path (str): The path to the yaml file.

        Returns:
            The new instance of the model.
        """
        return cls.from_yaml_files([path])

    @classmethod
    def load_data_with_references(cls, path: str) -> Dict[str, Any]:
        """
        Load data from a yaml file and resolve references.

        Args:
            path (str): The path to the yaml file.

        Returns:
            Dict[str, Any]: The loaded data.
        """
        with open(path) as f:
            data = yaml.load(f)
            _resolve_object_paths_recursively(path, data, ObjectPath(), data)
        return data

    @classmethod
    def from_yaml_files(cls, paths: List[str]) -> Self:
        """
        Create a new instance of the model by merging the data from multiple yaml files.

        The data from the files must be either the base model type that follows the schema
        defined in the protobufs, or it must be an overlay that can be merged with the same
        base model type.

        Args:
            paths: The paths to the yaml files.

        Returns:
            The new instance of the model.
        """
        data: Dict[str, Any] = {}
        for path in paths:
            new_data = cls.load_data_with_references(path)

            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=DeprecationWarning, module='jsonmerge')
                data = jsonmerge.merge(data, new_data)
        return cls.model_validate(data)

    def merge(self, other: BaseModel) -> Self:
        """
        Merge this model with another model.

        Args:
            other: The other model to merge with.

        Returns:
            The merged model.
        """
        return self.merge_json(other.model_dump(mode='json', exclude_none=True, exclude_defaults=True))

    def merge_json(self, other: Dict[str, Any]) -> Self:
        """
        Merges a json representation.

        Args:
            other: The other model to merge with as a jsonified dict

        Returns:
            The merged model.
        """
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=DeprecationWarning, module='jsonmerge')
            data = jsonmerge.merge(self.model_dump(mode='json'), other)
        return self.model_validate(data)

    def apply_cli_args(self, other: BaseModel) -> Self:
        """
        Merge CLI args base model.

        Args:
            other: The other model to merge with.

        Returns:
            The merged model.
        """
        return apply_args(self, other)


def _resolve_object_paths_recursively(root_path: str, root: Dict[str, Any], path_to_ref: ObjectPath, data: Any) -> None:
    """
    Recursively resolves object paths in the data.

    This function traverses the data structure, looking for string values that represent
    object paths. When it finds such a value, it resolves the path and updates the data
    structure accordingly. This process continues recursively for nested structures.

    Args:
        root_path: The path to the root of the data structure.
        root: The root of the data structure.
        path_to_ref: The path to the reference object.
        data: The data to resolve.
    """
    if isinstance(data, dict):
        for field_name, value in data.items():
            _resolve_object_paths_recursively(root_path, root, path_to_ref.add_step(field_name), value)
        return
    elif isinstance(data, list):
        for index, item in enumerate(data):  # type: ignore
            _resolve_object_paths_recursively(root_path, root, path_to_ref.add_index_step(index=index), item)
        return
    elif isinstance(data, str) and EXTERNAL_OBJECT_PATH_REGEX.match(data):
        resolved_value = _resolve_external_ref(root_path, data)
    elif isinstance(data, str) and INTERNAL_OBJECT_PATH_REGEX.match(data):
        path_at_ref = ObjectPath.from_string(data)
        resolved_value = resolve_inner_ref(root, path_to_ref, path_at_ref)
    else:
        return

    steps = path_to_ref.steps.copy()
    container = root
    while len(steps) > 1:
        step = steps.pop(0)
        container = container[step.name]
        if step.index is not None:
            container = container[step.index]

    if steps[0].index is not None:
        container[steps[0].name][steps[0].index] = resolved_value
    else:
        container[steps[0].name] = resolved_value

    _resolve_object_paths_recursively(root_path, root, path_to_ref, resolved_value)


def _resolve_external_ref(root_path: str, path: str) -> Any:
    """
    Resolves an external reference.

    Args:
        path: The path to the external reference.

    Returns:
        The external reference.
    """
    re_match = EXTERNAL_OBJECT_PATH_REGEX.match(path)
    if re_match is None:
        raise ValueError('Expected a path that matches external reference regex')
    file_path = re_match.group(1)

    if not file_path.startswith('/'):
        file_path = str(pathlib.Path(root_path).parent / file_path)

    data = YamlBaseModel.load_data_with_references(file_path)

    if re_match.group(2) is None:
        return data

    path_at_ref = ObjectPath.from_string(re_match.group(2))
    return resolve_inner_ref(data, ObjectPath(), path_at_ref)
