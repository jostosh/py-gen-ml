import io
import sys
from typing import Dict, List, Optional

import google.protobuf.compiler.plugin_pb2
import google.protobuf.json_format
import protogen

from py_gen_ml.logging.setup_logger import setup_logger
from py_gen_ml.plugin.generator import GenTask, InitGenerator
from py_gen_ml.plugin.json_schema_task_generator import JsonSchemaTaskGenerator
from py_gen_ml.plugin.registry import GeneratorRegistry, default_registry

logger = setup_logger(__name__)

# Plugin parameters from protoc are comma-separated; use ';' to delimit names
# inside ``enabled_generators`` to avoid that clash.
ENABLED_GENERATORS_SEPARATOR = ';'


def _parse_enabled_generators(raw: Optional[str]) -> Optional[List[str]]:
    if raw is None or raw == '':
        return None
    return [name.strip() for name in raw.split(ENABLED_GENERATORS_SEPARATOR) if name.strip()]


class _Plugin:

    def __init__(self, registry: Optional[GeneratorRegistry] = None) -> None:
        self._gen_tasks: list[GenTask] = []
        self._registry = registry if registry is not None else default_registry()

    def generate(self, plugin: protogen.Plugin) -> None:
        """Run every active generator and emit the post-processing helpers.

        The active set is derived from the registry: when
        ``enabled_generators=<;-separated names>`` is passed as a plugin
        parameter, only those generators run; otherwise every spec with
        ``enabled_by_default=True`` runs.
        """
        enabled = _parse_enabled_generators(plugin.parameter.get('enabled_generators'))
        for generator in self._registry.build_active(plugin, enabled=enabled):
            generator.generate_code()
            self._gen_tasks.extend(generator.json_schema_gen_tasks)

        InitGenerator(plugin).generate_code()
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
