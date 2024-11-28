import io
import sys
from typing import Dict

import google.protobuf.compiler.plugin_pb2
import google.protobuf.json_format
import protogen

from py_gen_ml.logging.setup_logger import setup_logger
from py_gen_ml.plugin.base_model_generator import BaseModelGenerator
from py_gen_ml.plugin.cli_args_generator import CliArgsGenerator
from py_gen_ml.plugin.generator import GenTask, InitGenerator
from py_gen_ml.plugin.json_schema_task_generator import JsonSchemaTaskGenerator
from py_gen_ml.plugin.sweep_model_generator import SweepModelGenerator

logger = setup_logger(__name__)


class _Plugin:

    def __init__(self) -> None:
        self._gen_tasks: list[GenTask] = []

    def generate(self, plugin: protogen.Plugin) -> None:
        """
        Generate the necessary files for the plugin.

        This function generates the base model, patch model, sweep model, and CLI arguments
        for the given plugin. It uses the BaseModelGenerator, SweepModelGenerator, and
        CliArgsGenerator classes to create the respective files.
        """
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
    logger.debug('Running py-gen-ml plugin')

    input_stream = sys.stdin.buffer
    request = google.protobuf.compiler.plugin_pb2.CodeGeneratorRequest()
    request.ParseFromString(input_stream.read())

    if request.HasField('parameter') and request.parameter:
        parameter: Dict[str, str] = {}
        for param in request.parameter.split(','):
            if param == '':
                # Ignore empty parameters.
                continue
            splits = param.split('=', 1)  # maximum one split
            if len(splits) == 1:
                k, v = splits[0], ''
            else:
                k, v = splits
            parameter[k] = v
        if parameter.get('export_code_generator_request', 'false').lower() == 'true':
            with open('request.pbbin', 'wb') as f:
                f.write(request.SerializeToString())

    input_stream = io.BytesIO(request.SerializeToString())
    opts = protogen.Options(
        input=input_stream,
        supported_features=[
            google.protobuf.compiler.plugin_pb2.CodeGeneratorResponse.Feature.FEATURE_PROTO3_OPTIONAL,  # type: ignore
        ],
    )

    input_stream.seek(0)
    plugin = _Plugin()
    opts.run(plugin.generate)
