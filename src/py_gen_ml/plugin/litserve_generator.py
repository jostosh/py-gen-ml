"""Generator that emits LitServe I/O models, LitAPI/LitServer factories, and clients."""
from __future__ import annotations

from typing import ClassVar, Optional

import protogen

from py_gen_ml.extensions_pb2 import LitServe, LitServeConfig, LitServeMethod
from py_gen_ml.logging.setup_logger import setup_logger
from py_gen_ml.plugin.common import (
    get_extension_value,
    py_import_for_source_file_derived_file,
    snake_case,
)
from py_gen_ml.plugin.constants import BASE_MODEL_ALIAS, LITSERVE_SUFFIX
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
    method_http_route,
    rpc_root_messages,
    services_with_extension,
)
from py_gen_ml.plugin.type_mapping import PythonTypeMapper, TypeMapper
from py_gen_ml.typing.some import some

logger = setup_logger(__name__)


class LitServeGenerator(Generator):
    """Emit LitServe adapters for services opted in via ``(pgml.litserve)``.

    Generates Pydantic I/O models for RPC request/response closures, per-RPC
    module-level ``LitAPI`` classes plus ``create_*_*_api`` factories, a
    ``create_*_server`` that wraps them in ``litserve.LitServer``, typed
    sync/async client helpers, and optional serve-config kwargs mappers linked
    via ``(pgml.litserve_config)``.
    """

    name: ClassVar[str] = 'litserve'
    output_suffix: ClassVar[Optional[str]] = LITSERVE_SUFFIX

    def __init__(
        self,
        gen: protogen.Plugin,
        suffix: Optional[str] = None,
        *,
        type_mapper: Optional[TypeMapper] = None,
    ) -> None:
        super().__init__(gen, type_mapper=type_mapper or PythonTypeMapper())
        self._suffix = suffix or LITSERVE_SUFFIX

    def _generate_code_for_file(self, file: protogen.File) -> None:
        services = services_with_extension(file, 'litserve', LitServe)
        if not services:
            return

        assert_unary_methods(services, generator_name='litserve')

        roots = rpc_root_messages(services)
        messages = collect_message_closure(roots, file)
        configs = configs_by_service(file, 'litserve_config', LitServeConfig)

        g = self._new_python_file(
            file,
            self._suffix,
            emit_typing_import=True,
            emit_pgml_import=False,
        )
        g.P('import httpx')
        g.P('import litserve as ls')
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
            self._generate_server_kwargs(g, service, config_msg)
            for method in service.methods:
                self._generate_api_class(g, service, method)
                self._generate_create_api(g, service, method)
            self._generate_create_server(g, service, config_msg)
            self._generate_client_helpers(g, service, config_msg)

        self._run_yapf(g)

    def _generate_server_kwargs(
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
            f'def {helper}_server_kwargs('
            f'config: {config_cls}'
            f') -> typing.Dict[str, typing.Any]:',
        )
        g.set_indent(4)
        g.P(
            f'"""Map :class:`{config_msg.proto.name}` fields to ``ls.LitServer`` kwargs."""',
        )
        g.P('kwargs: typing.Dict[str, typing.Any] = {}')
        field_names = {field.py_name for field in config_msg.fields}
        if 'accelerator' in field_names:
            g.P('if getattr(config, "accelerator", None) is not None:')
            g.set_indent(8)
            g.P('kwargs["accelerator"] = config.accelerator')
            g.set_indent(4)
        if 'devices' in field_names:
            g.P('if getattr(config, "devices", None) is not None:')
            g.set_indent(8)
            g.P('kwargs["devices"] = config.devices')
            g.set_indent(4)
        if 'workers_per_device' in field_names:
            g.P('if getattr(config, "workers_per_device", None) is not None:')
            g.set_indent(8)
            g.P('kwargs["workers_per_device"] = config.workers_per_device')
            g.set_indent(4)
        if 'timeout_s' in field_names:
            g.P('if getattr(config, "timeout_s", None) is not None:')
            g.set_indent(8)
            g.P('kwargs["timeout"] = config.timeout_s')
            g.set_indent(4)
        g.P('return kwargs')
        g.set_indent(0)
        g.P()
        g.P()

    def _api_class_name(self, service: protogen.Service, method: protogen.Method) -> str:
        litserve_opts = some(get_extension_value(service, 'litserve', LitServe))
        prefix = litserve_opts.name or service.proto.name
        return f'{prefix}{method.proto.name}API'

    def _method_api_path(self, method: protogen.Method) -> str:
        opts = get_extension_value(method, 'litserve_method', LitServeMethod)
        return method_http_route(
            method,
            opts.api_path if opts and opts.api_path else None,
        )

    def _generate_api_class(
        self,
        g: protogen.GeneratedFile,
        service: protogen.Service,
        method: protogen.Method,
    ) -> None:
        """Emit a module-level LitAPI subclass (picklable for LitServe workers)."""
        api_path = self._method_api_path(method)
        class_name = self._api_class_name(service, method)
        in_name = some(method.input).proto.name
        out_name = some(method.output).proto.name

        g.P(f'class {class_name}(ls.LitAPI):')
        g.set_indent(4)
        g.P(f'"""LitAPI for ``{service.proto.name}.{method.proto.name}``."""')
        g.P()
        g.P(
            'def __init__('
            'self, '
            f'predict: typing.Callable[[{in_name}], {out_name}], '
            'setup: typing.Optional[typing.Callable[[typing.Any, str], None]] = None'
            ') -> None:',
        )
        g.set_indent(8)
        g.P(f'super().__init__(api_path={api_path!r})')
        g.P('self._predict = predict')
        g.P('self._setup = setup')
        g.set_indent(4)
        g.P()
        g.P('def setup(self, device: str) -> None:')
        g.set_indent(8)
        g.P('if self._setup is not None:')
        g.set_indent(12)
        g.P('self._setup(self, device)')
        g.set_indent(4)
        g.P()
        g.P(f'def decode_request(self, request: {in_name}) -> {in_name}:')
        g.set_indent(8)
        g.P(f'if isinstance(request, {in_name}):')
        g.set_indent(12)
        g.P('return request')
        g.set_indent(8)
        g.P(f'return {in_name}.model_validate(request)')
        g.set_indent(4)
        g.P()
        g.P(f'def predict(self, x: {in_name}) -> {out_name}:')
        g.set_indent(8)
        g.P('return self._predict(x)')
        g.set_indent(4)
        g.P()
        g.P(f'def encode_response(self, output: {out_name}) -> typing.Dict[str, typing.Any]:')
        g.set_indent(8)
        g.P(f'if isinstance(output, {out_name}):')
        g.set_indent(12)
        g.P('return output.model_dump()')
        g.set_indent(8)
        g.P(f'return {out_name}.model_validate(output).model_dump()')
        g.set_indent(0)
        g.P()
        g.P()

    def _generate_create_api(
        self,
        g: protogen.GeneratedFile,
        service: protogen.Service,
        method: protogen.Method,
    ) -> None:
        helper = snake_case(service.proto.name)
        class_name = self._api_class_name(service, method)
        in_name = some(method.input).proto.name
        out_name = some(method.output).proto.name
        factory = f'create_{helper}_{method.py_name}_api'

        g.P(
            f'def {factory}(*, '
            f'{method.py_name}: typing.Callable[[{in_name}], {out_name}], '
            f'setup: typing.Optional[typing.Callable[[typing.Any, str], None]] = None'
            f') -> {class_name}:',
        )
        g.set_indent(4)
        g.P(
            f'"""Build a ``{class_name}`` for ``{service.proto.name}.{method.proto.name}``.',
        )
        g.P()
        g.P(
            f'Pass the RPC handler as ``{method.py_name}``; optionally ``setup(api, device)``',
        )
        g.P('for model load. Handlers should be module-level (picklable) for LitServe workers.')
        g.P('Do not edit the generated module—inject logic via these callables.')
        g.P('"""')
        g.P(f'return {class_name}(predict={method.py_name}, setup=setup)')
        g.set_indent(0)
        g.P()
        g.P()

    def _generate_create_server(
        self,
        g: protogen.GeneratedFile,
        service: protogen.Service,
        config_msg: Optional[protogen.Message],
    ) -> None:
        helper = snake_case(service.proto.name)
        params: list[str] = []
        for method in service.methods:
            in_name = some(method.input).proto.name
            out_name = some(method.output).proto.name
            params.append(
                f'{method.py_name}: typing.Callable[[{in_name}], {out_name}]',
            )
        params.append(
            'setup: typing.Optional[typing.Callable[[typing.Any, str], None]] = None',
        )
        if config_msg is not None:
            config_cls = f'{BASE_MODEL_ALIAS}.{config_msg.proto.name}'
            params.append(f'config: typing.Optional[{config_cls}] = None')
        params.append('**server_kwargs: typing.Any')

        g.P(f'def create_{helper}_server(*, {", ".join(params)}) -> ls.LitServer:')
        g.set_indent(4)
        g.P(f'"""Build an ``ls.LitServer`` for ``{service.proto.name}``.')
        g.P()
        g.P('One ``LitAPI`` is created per RPC (distinct ``api_path``). Extra kwargs are')
        g.P('forwarded to ``ls.LitServer`` and override mapped config fields.')
        g.P('"""')
        if config_msg is not None:
            g.P(f'cfg = config or {BASE_MODEL_ALIAS}.{config_msg.proto.name}()')
            g.P(f'kwargs = {helper}_server_kwargs(cfg)')
        else:
            g.P('kwargs: typing.Dict[str, typing.Any] = {}')
        g.P('kwargs.update(server_kwargs)')
        g.P('apis = [')
        g.set_indent(8)
        for method in service.methods:
            factory = f'create_{helper}_{method.py_name}_api'
            g.P(
                f'{factory}({method.py_name}={method.py_name}, setup=setup),',
            )
        g.set_indent(4)
        g.P(']')
        g.P('return ls.LitServer(apis if len(apis) > 1 else apis[0], **kwargs)')
        g.set_indent(0)
        g.P()
        g.P()

    def _generate_client_helpers(
        self,
        g: protogen.GeneratedFile,
        service: protogen.Service,
        config_msg: Optional[protogen.Message],
    ) -> None:
        helper = snake_case(service.proto.name)
        has_url = (
            config_msg is not None
            and any(f.py_name == 'url' for f in config_msg.fields)
        )

        for method in service.methods:
            api_path = self._method_api_path(method)
            in_name = some(method.input).proto.name
            out_name = some(method.output).proto.name
            sync_name = f'call_{helper}_{method.py_name}_sync'
            async_name = f'call_{helper}_{method.py_name}_async'

            g.P(
                f'def {sync_name}('
                f'request: {in_name}, *, '
                f'url: typing.Optional[str] = None, '
                f'client: typing.Optional[httpx.Client] = None'
                f') -> {out_name}:',
            )
            g.set_indent(4)
            g.P(f'"""Call ``{service.proto.name}.{method.proto.name}`` synchronously."""')
            g.P('owns_client = client is None')
            if config_msg is not None and has_url:
                g.P(
                    f'resolved_url = url or {BASE_MODEL_ALIAS}.{config_msg.proto.name}().url',
                )
            else:
                g.P('resolved_url = url')
            g.P('if not resolved_url:')
            g.set_indent(8)
            g.P('raise ValueError("url is required")')
            g.set_indent(4)
            g.P(f'endpoint = resolved_url.rstrip("/") + {api_path!r}')
            g.P('if client is None:')
            g.set_indent(8)
            g.P('client = httpx.Client()')
            g.set_indent(4)
            g.P('try:')
            g.set_indent(8)
            g.P('response = client.post(endpoint, json=request.model_dump())')
            g.P('response.raise_for_status()')
            g.P(f'return {out_name}.model_validate(response.json())')
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
                f'client: typing.Optional[httpx.AsyncClient] = None'
                f') -> {out_name}:',
            )
            g.set_indent(4)
            g.P(f'"""Call ``{service.proto.name}.{method.proto.name}`` asynchronously."""')
            g.P('owns_client = client is None')
            if config_msg is not None and has_url:
                g.P(
                    f'resolved_url = url or {BASE_MODEL_ALIAS}.{config_msg.proto.name}().url',
                )
            else:
                g.P('resolved_url = url')
            g.P('if not resolved_url:')
            g.set_indent(8)
            g.P('raise ValueError("url is required")')
            g.set_indent(4)
            g.P(f'endpoint = resolved_url.rstrip("/") + {api_path!r}')
            g.P('if client is None:')
            g.set_indent(8)
            g.P('client = httpx.AsyncClient()')
            g.set_indent(4)
            g.P('try:')
            g.set_indent(8)
            g.P('response = await client.post(endpoint, json=request.model_dump())')
            g.P('response.raise_for_status()')
            g.P(f'return {out_name}.model_validate(response.json())')
            g.set_indent(4)
            g.P('finally:')
            g.set_indent(8)
            g.P('if owns_client:')
            g.set_indent(12)
            g.P('await client.aclose()')
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


litserve_spec = GeneratorSpec(
    name='litserve',
    factory=lambda plugin: LitServeGenerator(plugin),
    enabled_by_default=False,
    description='LitServe LitAPI/LitServer factories and clients for (pgml.litserve) services.',
)
