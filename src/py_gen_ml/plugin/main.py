import google.protobuf.compiler.plugin_pb2
import google.protobuf.json_format
import protogen

from py_gen_ml.plugin.base_model_generator import BaseModelGenerator
from py_gen_ml.plugin.cli_args_generator import CliArgsGenerator
from py_gen_ml.plugin.generator import GenTask, InitGenerator
from py_gen_ml.plugin.json_schema_task_generator import JsonSchemaTaskGenerator
from py_gen_ml.plugin.sweep_model_generator import SweepModelGenerator


class _Plugin:

    def __init__(self) -> None:
        self._gen_tasks = list[GenTask]()

    def generate(self, plugin: protogen.Plugin) -> None:
        """
        Generate the necessary files for the plugin.

        This function generates the base model, patch model, sweep model, and CLI arguments
        for the given plugin. It uses the BaseModelGenerator, SweepModelGenerator, and
        CliArgsGenerator classes to create the respective files.
        """
        plugin.parameter
        for generator in [
            BaseModelGenerator(plugin, is_patch=False, suffix='_base.py'),
            BaseModelGenerator(plugin, is_patch=True, suffix='_patch.py'),
            SweepModelGenerator(plugin, suffix='_sweep.py'),
            CliArgsGenerator(plugin, suffix='_cli_args.py'),
            InitGenerator(plugin),
        ]:
            generator.generate_code()
            self._gen_tasks.extend(generator.json_schema_gen_tasks)

        JsonSchemaTaskGenerator(plugin, self._gen_tasks).generate_code()

    @property
    def json_schema_gen_tasks(self) -> list[GenTask]:
        return self._gen_tasks


def run() -> None:
    """
    Run the plugin to generate the necessary files.

    This function sets up the plugin options and runs the generate function to create
    the required files. It uses the protogen.Options class to configure the supported
    features and then executes the generate function.
    """
    opts = protogen.Options(
        supported_features=[
            google.protobuf.compiler.plugin_pb2.CodeGeneratorResponse.Feature.FEATURE_PROTO3_OPTIONAL,  # type: ignore
        ],
    )
    plugin = _Plugin()
    opts.run(plugin.generate)
