"""Generator that emits BentoML I/O models, service factories, and client helpers."""
from __future__ import annotations

from typing import ClassVar, Optional

import protogen

from py_gen_ml.extensions_pb2 import BentoML, BentoMLConfig, BentoMLMethod
from py_gen_ml.logging.setup_logger import setup_logger
from py_gen_ml.plugin.common import (
    get_extension_value,
    py_import_for_source_file_derived_file,
    snake_case,
)
from py_gen_ml.plugin.constants import BASE_MODEL_ALIAS, BENTOML_SUFFIX
from py_gen_ml.plugin.generator import Generator
from py_gen_ml.plugin.message_kind import (
    collect_message_closure,
    ordered_messages,
)
from py_gen_ml.plugin.registry import GeneratorSpec
from py_gen_ml.plugin.schema_emit import emit_pydantic_model
from py_gen_ml.plugin.service_rpc import (
    assert_unary_methods,
    configs_by_service,
    method_api_name,
    method_http_route,
    rpc_root_messages,
    services_with_extension,
)
from py_gen_ml.plugin.type_mapping import PythonTypeMapper, TypeMapper
from py_gen_ml.typing.some import some

logger = setup_logger(__name__)


class BentoMLGenerator(Generator):
    """Emit BentoML adapters for services opted in via ``(pgml.bentoml)``.

    Generates Pydantic I/O models for RPC request/response closures, a
    ``create_*_service`` factory, typed sync/async client helpers, and optional
    serve-config kwargs mappers linked via ``(pgml.bentoml_config)``.
    """

    name: ClassVar[str] = 'bentoml'
    output_suffix: ClassVar[Optional[str]] = BENTOML_SUFFIX

    def __init__(
        self,
        gen: protogen.Plugin,
        suffix: Optional[str] = None,
        *,
        type_mapper: Optional[TypeMapper] = None,
    ) -> None:
        super().__init__(gen, type_mapper=type_mapper or PythonTypeMapper())
        self._suffix = suffix or BENTOML_SUFFIX

    def _generate_code_for_file(self, file: protogen.File) -> None:
        services = services_with_extension(file, 'bentoml', BentoML)
        if not services:
            return

        assert_unary_methods(services, generator_name='bentoml')

        roots = rpc_root_messages(services)
        messages = collect_message_closure(roots, file)
        configs = configs_by_service(file, 'bentoml_config', BentoMLConfig)

        g = self._new_python_file(
            file,
            self._suffix,
            emit_typing_import=True,
            emit_pgml_import=False,
        )
        g.P('import bentoml')
        g.P('from pydantic import BaseModel')
        if configs:
            base_py_import = py_import_for_source_file_derived_file(g, '_base')
            base_py_import = self._prepend_python_import(base_py_import)
            g.P(f'import {base_py_import} as {BASE_MODEL_ALIAS}')
        g.P()
        g.P()

        for message in ordered_messages(file, messages):
            emit_pydantic_model(
                g,
                message,
                base_class='BaseModel',
                field_annotation=self._field_annotation,
                field_type=self._field_type,
            )

        for service in sorted(services, key=lambda s: s.proto.name):
            config_msg = configs.get(service.proto.name)
            self._generate_service_kwargs(g, service, config_msg)
            self._generate_create_service(g, service, config_msg)
            self._generate_client_helpers(g, service, config_msg)

        self._run_yapf(g)

    def _generate_service_kwargs(
        self,
        g: protogen.GeneratedFile,
        service: protogen.Service,
        config_msg: Optional[protogen.Message],
    ) -> None:
        if config_msg is None:
            return

        helper = snake_case(service.proto.name)
        config_cls = f'{BASE_MODEL_ALIAS}.{config_msg.proto.name}'
        g.P(
            f'def {helper}_service_kwargs('
            f'config: {config_cls}'
            f') -> typing.Dict[str, typing.Any]:',
        )
        g.set_indent(4)
        g.P(f'"""Map :class:`{config_msg.proto.name}` fields to ``@bentoml.service`` kwargs."""')
        g.P('kwargs: typing.Dict[str, typing.Any] = {}')
        field_names = {field.py_name for field in config_msg.fields}
        if 'workers' in field_names:
            g.P('if getattr(config, "workers", None) is not None:')
            g.set_indent(8)
            g.P('kwargs["workers"] = config.workers')
            g.set_indent(4)
        if 'timeout_s' in field_names:
            g.P('if getattr(config, "timeout_s", None) is not None:')
            g.set_indent(8)
            g.P('kwargs["traffic"] = {"timeout": config.timeout_s}')
            g.set_indent(4)
        g.P('return kwargs')
        g.set_indent(0)
        g.P()
        g.P()

    def _generate_create_service(
        self,
        g: protogen.GeneratedFile,
        service: protogen.Service,
        config_msg: Optional[protogen.Message],
    ) -> None:
        bentoml_opts = some(get_extension_value(service, 'bentoml', BentoML))
        class_name = bentoml_opts.name or service.proto.name
        helper = snake_case(service.proto.name)

        params: list[str] = []
        for method in service.methods:
            in_name = some(method.input).proto.name
            out_name = some(method.output).proto.name
            params.append(
                f'{method.py_name}: typing.Callable[[{in_name}], {out_name}]',
            )
        if config_msg is not None:
            config_cls = f'{BASE_MODEL_ALIAS}.{config_msg.proto.name}'
            params.append(f'config: typing.Optional[{config_cls}] = None')

        g.P(f'def create_{helper}_service(*, {", ".join(params)}) -> typing.Any:')
        g.set_indent(4)
        g.P(f'"""Build a ``@bentoml.service`` class for ``{service.proto.name}``.')
        g.P()
        g.P('Pass one callable per RPC; callables receive the request model and')
        g.P('must return the response model. Do not edit the generated module—')
        g.P('inject your model logic via these handlers.')
        g.P('"""')
        if config_msg is not None:
            g.P(f'cfg = config or {BASE_MODEL_ALIAS}.{config_msg.proto.name}()')
            g.P(f'service_kwargs = {helper}_service_kwargs(cfg)')
        else:
            g.P('service_kwargs: typing.Dict[str, typing.Any] = {}')
        g.P()
        g.P('@bentoml.service(**service_kwargs)')
        g.P(f'class {class_name}:')
        g.set_indent(8)
        for method in service.methods:
            self._emit_api_method(g, method)
        g.set_indent(4)
        g.P(f'return {class_name}')
        g.set_indent(0)
        g.P()
        g.P()

    def _emit_api_method(
        self,
        g: protogen.GeneratedFile,
        method: protogen.Method,
    ) -> None:
        opts = get_extension_value(method, 'bentoml_method', BentoMLMethod)
        api_name = method_api_name(method, opts.name if opts and opts.name else None)
        route = method_http_route(method, opts.route if opts and opts.route else None)
        batchable = bool(opts.batchable) if opts is not None else False
        in_name = some(method.input).proto.name
        out_name = some(method.output).proto.name

        api_args = [
            f'route={route!r}',
            f'name={api_name!r}',
            f'input_spec={in_name}',
            f'output_spec={out_name}',
        ]
        if batchable:
            api_args.append('batchable=True')
        g.P(f'@bentoml.api({", ".join(api_args)})')
        g.P(f'def {method.py_name}(self, **kwargs: typing.Any) -> {out_name}:')
        g.set_indent(12)
        g.P(f'return {method.py_name}({in_name}.model_validate(kwargs))')
        g.set_indent(8)
        g.P()

    def _generate_client_helpers(
        self,
        g: protogen.GeneratedFile,
        service: protogen.Service,
        config_msg: Optional[protogen.Message],
    ) -> None:
        helper = snake_case(service.proto.name)
        config_model = config_msg
        has_url = (config_model is not None and any(f.py_name == 'url' for f in config_model.fields))

        for method in service.methods:
            opts = get_extension_value(method, 'bentoml_method', BentoMLMethod)
            api_name = method_api_name(method, opts.name if opts and opts.name else None)
            in_name = some(method.input).proto.name
            out_name = some(method.output).proto.name
            sync_name = f'call_{helper}_{method.py_name}_sync'
            async_name = f'call_{helper}_{method.py_name}_async'

            g.P(
                f'def {sync_name}('
                f'request: {in_name}, *, '
                f'url: typing.Optional[str] = None, '
                f'client: typing.Optional[bentoml.SyncHTTPClient] = None'
                f') -> {out_name}:',
            )
            g.set_indent(4)
            g.P(f'"""Call ``{service.proto.name}.{method.proto.name}`` synchronously."""')
            g.P('owns_client = client is None')
            if config_model is not None and has_url:
                g.P(
                    f'resolved_url = url or {BASE_MODEL_ALIAS}.{config_model.proto.name}().url',
                )
            else:
                g.P('resolved_url = url')
            g.P('if client is None:')
            g.set_indent(8)
            g.P('if not resolved_url:')
            g.set_indent(12)
            g.P('raise ValueError("url is required when client is not provided")')
            g.set_indent(8)
            g.P('client = bentoml.SyncHTTPClient(resolved_url)')
            g.set_indent(4)
            g.P('try:')
            g.set_indent(8)
            g.P(f'raw = client.call({api_name!r}, **request.model_dump())')
            g.P(f'return {out_name}.model_validate(raw)')
            g.set_indent(4)
            g.P('finally:')
            g.set_indent(8)
            g.P('if owns_client:')
            g.set_indent(12)
            g.P('client.close()')
            g.set_indent(0)
            g.P()
            g.P()

            g.P(
                f'async def {async_name}('
                f'request: {in_name}, *, '
                f'url: typing.Optional[str] = None, '
                f'client: typing.Optional[bentoml.AsyncHTTPClient] = None'
                f') -> {out_name}:',
            )
            g.set_indent(4)
            g.P(f'"""Call ``{service.proto.name}.{method.proto.name}`` asynchronously."""')
            g.P('owns_client = client is None')
            if config_model is not None and has_url:
                g.P(
                    f'resolved_url = url or {BASE_MODEL_ALIAS}.{config_model.proto.name}().url',
                )
            else:
                g.P('resolved_url = url')
            g.P('if client is None:')
            g.set_indent(8)
            g.P('if not resolved_url:')
            g.set_indent(12)
            g.P('raise ValueError("url is required when client is not provided")')
            g.set_indent(8)
            g.P('client = bentoml.AsyncHTTPClient(resolved_url)')
            g.set_indent(4)
            g.P('try:')
            g.set_indent(8)
            g.P(f'raw = await client.call({api_name!r}, **request.model_dump())')
            g.P(f'return {out_name}.model_validate(raw)')
            g.set_indent(4)
            g.P('finally:')
            g.set_indent(8)
            g.P('if owns_client:')
            g.set_indent(12)
            g.P('await client.close()')
            g.set_indent(0)
            g.P()
            g.P()

    def _field_annotation(self, field: protogen.Field) -> str:
        annotation = self._field_type(field)
        if field.is_list():
            annotation = f'typing.List[{annotation}]'
        if field.proto.proto3_optional:
            annotation = f'typing.Optional[{annotation}]'
        return annotation

    def _field_type(self, field: protogen.Field) -> str:
        if field.kind == protogen.Kind.ENUM:
            return 'str'
        assert self._type_mapper is not None
        return self._type_mapper.field_to_type(field)


bentoml_spec = GeneratorSpec(
    name='bentoml',
    factory=lambda plugin: BentoMLGenerator(plugin),
    enabled_by_default=False,
    description='BentoML I/O models, service factories, and clients for (pgml.bentoml) services.',
)
