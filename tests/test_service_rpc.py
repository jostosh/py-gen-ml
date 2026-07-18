"""Tests for protobuf service/rpc helpers."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from py_gen_ml.plugin.service_rpc import (
    assert_unary_methods,
    method_api_name,
    method_http_route,
    rpc_root_messages,
    services_with_extension,
)


def test_services_with_extension_filters_enable() -> None:
    enabled = MagicMock()
    disabled = MagicMock()
    missing = MagicMock()
    file = MagicMock()
    file.services = [enabled, disabled, missing]

    def fake_get(element: object, name: str, ext_type: type) -> object | None:
        if element is enabled:
            return SimpleNamespace(enable=True)
        if element is disabled:
            return SimpleNamespace(enable=False)
        return None

    with patch('py_gen_ml.plugin.service_rpc.get_extension_value', side_effect=fake_get):
        assert services_with_extension(file, 'bentoml', object) == [enabled]


def test_rpc_root_messages_dedupes_inputs_and_outputs() -> None:
    req = MagicMock()
    resp = MagicMock()
    method_a = MagicMock()
    method_a.input = req
    method_a.output = resp
    method_b = MagicMock()
    method_b.input = req
    method_b.output = resp
    service = MagicMock()
    service.methods = [method_a, method_b]

    assert rpc_root_messages([service]) == [req, resp]


def test_assert_unary_methods_rejects_streaming() -> None:
    method = MagicMock()
    method.full_name = 'demo.Svc.Stream'
    method.proto.client_streaming = False
    method.proto.server_streaming = True
    service = MagicMock()
    service.methods = [method]

    with pytest.raises(ValueError, match='unary RPCs only'):
        assert_unary_methods([service], generator_name='bentoml')


def test_assert_unary_methods_allows_unary() -> None:
    method = MagicMock()
    method.proto.client_streaming = False
    method.proto.server_streaming = False
    service = MagicMock()
    service.methods = [method]
    assert_unary_methods([service], generator_name='bentoml')


def test_method_http_route_and_api_name_defaults() -> None:
    method = MagicMock()
    method.py_name = 'predict'
    assert method_http_route(method) == '/predict'
    assert method_http_route(method, '/v1/predict') == '/v1/predict'
    assert method_api_name(method) == 'predict'
    assert method_api_name(method, 'classify') == 'classify'
