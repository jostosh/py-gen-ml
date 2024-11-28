import abc
import importlib
import json
import pathlib
from dataclasses import dataclass

import protogen
from yapf.yapflib.yapf_api import FormatCode

from py_gen_ml.logging.setup_logger import setup_logger
from py_gen_ml.plugin.common import field_requires_typing_import
from py_gen_ml.yaml.object_path import InsertAnyOfWithObjectPath

logger = setup_logger(__name__)


@dataclass
class GenTask:
    """
    Data class representing a generation task.

    Attributes:
        obj_path (str): The path to the object module.
        obj_name (str): The name of the object.
        path (str): The path to write the JSON schema.
    """
    obj_path: str
    obj_name: str
    path: str

    def generate(self) -> None:
        """
        Generate the JSON schema for the object.

        This method imports the object module, retrieves the object, and writes the JSON schema to the specified path.
        """
        obj_module = importlib.import_module(self.obj_path)
        obj = getattr(obj_module, self.obj_name)
        pathlib.Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(self.path).write_text(
            json.dumps(
                obj.model_json_schema(schema_generator=InsertAnyOfWithObjectPath,),
                indent=2,
            ),
        )


class Generator(abc.ABC):
    """
    Abstract base class for all generators.

    This class defines the interface for all generators used in the plugin.

    Args:
        gen (protogen.Plugin): The protogen plugin instance.
    """

    def __init__(self, gen: protogen.Plugin) -> None:
        """
        Initialize the Generator.

        Args:
            gen (protogen.Plugin): The protogen plugin instance.
        """
        self._gen = gen
        self._json_schema_gen_tasks: list[GenTask] = []
        self._source_root = self._gen.parameter['source_root']
        self._output_dir = self._gen.parameter['output_dir']
        self._configs_dir = self._gen.parameter['configs_dir']

    def generate_code(self) -> None:
        """
        Generate code for all relevant files.

        This method iterates through the files to generate, checks if the
        extension is enabled, and then generates the corresponding code.
        """
        for file in self._gen.files_to_generate:
            self._generate_code_for_file(file)

    def _requires_typing_import(self, file: protogen.File) -> bool:
        for message in file.messages:
            for field in message.fields:
                if field_requires_typing_import(field):
                    return True
        return False

    @abc.abstractmethod
    def _generate_code_for_file(self, file: protogen.File) -> None:
        """
        Generate code for a specific file.

        Args:
            file (protogen.File): The file to generate code for.
        """

    def _prepend_python_import(self, obj_path: str) -> str:
        prefix = str(pathlib.Path(self._output_dir).relative_to(self._source_root)).replace('/', '.')
        return f'{prefix}.{obj_path}'

    def _add_json_schema_gen_task(self, obj_path: str, obj_name: str, path: str) -> None:
        self._json_schema_gen_tasks.append(GenTask(self._prepend_python_import(obj_path), obj_name, path))

    @property
    def json_schema_gen_tasks(self) -> list[GenTask]:
        """
        Get the list of JSON schema generation tasks.

        Returns:
            List[GenTask]: The list of JSON schema generation tasks.
        """
        return self._json_schema_gen_tasks

    def _run_yapf(self, file: protogen.GeneratedFile) -> None:
        """
        Run yapf on the given file.

        Args:
            file (protogen.File): The file to run yapf on.
        """
        lines = file._buf
        yapf_toml_path = pathlib.Path(__file__).parent / 'yapf_style.toml'
        formatted_content, changed = FormatCode('\n'.join(lines), style_config=str(yapf_toml_path.absolute()))
        if changed:
            file._buf = formatted_content.split('\n')  # type: ignore


class InitGenerator(Generator):
    """
    Generator for the __init__.py file.

    This class is responsible for generating the __init__.py file,
    which is used to initialize the package.
    """

    def generate_code(self) -> None:
        """
        Generate the __init__.py file.

        This method creates a new generated file for the __init__.py file.
        It imports necessary modules and defines the __init__ module.
        """
        self._gen.new_generated_file('__init__.py', protogen.PyImportPath('__init__'))

    def _generate_code_for_file(self, file: protogen.File) -> None:
        pass
