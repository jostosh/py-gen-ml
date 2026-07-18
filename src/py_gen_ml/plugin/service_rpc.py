"""Helpers for protobuf ``service`` / ``rpc`` roots used by serving generators."""
from __future__ import annotations

from typing import Optional, TypeVar

import protogen

from py_gen_ml.plugin.common import get_extension_value
from py_gen_ml.typing.some import some

T = TypeVar('T')


def services_with_extension(
    file: protogen.File,
    extension_name: str,
    extension_type: type[T],
) -> list[protogen.Service]:
    """Return services in ``file`` whose named extension has ``.enable`` true."""
    enabled: list[protogen.Service] = []
    for service in file.services:
        opts = get_extension_value(service, extension_name, extension_type)
        if opts is not None and getattr(opts, 'enable', False):
            enabled.append(service)
    return enabled


def rpc_root_messages(services: list[protogen.Service]) -> list[protogen.Message]:
    """Deduped input/output messages for all methods on ``services``."""
    roots: list[protogen.Message] = []
    seen: set[protogen.Message] = set()
    for service in services:
        for method in service.methods:
            for message in (some(method.input), some(method.output)):
                if message not in seen:
                    seen.add(message)
                    roots.append(message)
    return roots


def assert_unary_methods(
    services: list[protogen.Service],
    *,
    generator_name: str,
) -> None:
    """Raise ``ValueError`` if any RPC is client- or server-streaming."""
    for service in services:
        for method in service.methods:
            if method.proto.client_streaming or method.proto.server_streaming:
                raise ValueError(
                    f'{generator_name} generator supports unary RPCs only; '
                    f'{method.full_name} is streaming',
                )


def method_http_route(method: protogen.Method, route: Optional[str] = None) -> str:
    """HTTP route for ``method``; default ``/{method.py_name}`` when ``route`` empty."""
    if route:
        return route
    return f'/{method.py_name}'


def method_api_name(method: protogen.Method, name: Optional[str] = None) -> str:
    """Client/API endpoint name; default ``method.py_name`` when ``name`` empty."""
    if name:
        return name
    return method.py_name


def configs_by_service(
    file: protogen.File,
    extension_name: str,
    extension_type: type[T],
) -> dict[str, protogen.Message]:
    """Map proto service name → config message for enabled ``*_config`` extensions.

    Expects the extension message to expose ``.enable`` and ``.service`` (service
    declaration name). Used by BentoML / LitServe serve-config linkage.
    """
    mapping: dict[str, protogen.Message] = {}
    for message in file.messages:
        opts = get_extension_value(message, extension_name, extension_type)
        if opts is None or not getattr(opts, 'enable', False):
            continue
        service = getattr(opts, 'service', '') or ''
        if not service:
            continue
        mapping[service] = message
    return mapping
