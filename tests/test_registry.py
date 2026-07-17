"""Tests for the generator registry and type mapping."""
from __future__ import annotations

from typing import Any
from unittest import mock

import pytest

import py_gen_ml as pgml
from py_gen_ml.plugin import main as plugin_main
from py_gen_ml.plugin.base_model_generator import (
    BaseModelGenerator,
    base_spec,
    patch_spec,
)
from py_gen_ml.plugin.cli_args_generator import CliArgsGenerator, cli_args_spec
from py_gen_ml.plugin.registry import (
    ENTRY_POINT_GROUP,
    GeneratorRegistry,
    GeneratorSpec,
    default_registry,
)
from py_gen_ml.plugin.sweep_model_generator import (
    SweepModelGenerator,
    sweep_spec,
)


class _FakePlugin:
    """Minimal stand-in for protogen.Plugin used to construct generators."""

    def __init__(self) -> None:
        self.parameter = {
            'source_root': 'src',
            'output_dir': 'src/pgml_out',
            'configs_dir': 'configs',
        }
        self.files_to_generate: list[Any] = []


def test_default_registry_lists_builtins() -> None:
    registry = default_registry(include_entry_points=False)
    assert registry.names() == ['base', 'patch', 'sweep', 'cli_args']


def test_class_attributes_match_specs() -> None:
    assert BaseModelGenerator.name == 'base'
    assert BaseModelGenerator.output_suffix == pgml.BASE_SUFFIX
    assert SweepModelGenerator.name == 'sweep'
    assert SweepModelGenerator.output_suffix == pgml.SWEEP_SUFFIX
    assert CliArgsGenerator.name == 'cli_args'
    assert CliArgsGenerator.output_suffix == pgml.CLI_ARGS_SUFFIX

    # Specs match the class attributes.
    assert base_spec.name == BaseModelGenerator.name
    assert sweep_spec.name == SweepModelGenerator.name
    assert cli_args_spec.name == CliArgsGenerator.name
    assert patch_spec.name == 'patch'


def test_build_active_default_runs_all_builtins() -> None:
    registry = default_registry(include_entry_points=False)
    generators = registry.build_active(_FakePlugin(), enabled=None)
    assert [type(g).__name__ for g in generators] == [
        'BaseModelGenerator',
        'BaseModelGenerator',
        'SweepModelGenerator',
        'CliArgsGenerator',
    ]
    # The first BaseModelGenerator emits the base model, the second the patch.
    assert generators[0]._is_patch is False
    assert generators[1]._is_patch is True


def test_build_active_filters_to_enabled_set() -> None:
    registry = default_registry(include_entry_points=False)
    generators = registry.build_active(_FakePlugin(), enabled=['base', 'sweep'])
    assert [type(g).__name__ for g in generators] == ['BaseModelGenerator', 'SweepModelGenerator']
    assert generators[0]._is_patch is False


def test_build_active_preserves_enabled_order() -> None:
    registry = default_registry(include_entry_points=False)
    generators = registry.build_active(_FakePlugin(), enabled=['sweep', 'base'])
    assert [type(g).__name__ for g in generators] == ['SweepModelGenerator', 'BaseModelGenerator']


def test_unknown_generator_raises() -> None:
    registry = default_registry(include_entry_points=False)
    with pytest.raises(KeyError, match='Unknown generator'):
        registry.build_active(_FakePlugin(), enabled=['nonexistent'])


def test_register_overrides_existing() -> None:
    registry = GeneratorRegistry()
    registry.register(GeneratorSpec(name='foo', factory=lambda p: object()))  # type: ignore[arg-type]
    sentinel = object()
    registry.register(GeneratorSpec(name='foo', factory=lambda p: sentinel))  # type: ignore[arg-type]
    [built] = registry.build_active(_FakePlugin(), enabled=['foo'])
    assert built is sentinel


def test_disabled_by_default_skipped_unless_explicit() -> None:
    registry = GeneratorRegistry()
    sentinel = object()
    registry.register(
        GeneratorSpec(
            name='opt_in',
            factory=lambda p: sentinel,  # type: ignore[arg-type]
            enabled_by_default=False,
        ),
    )
    assert registry.build_active(_FakePlugin(), enabled=None) == []
    assert registry.build_active(_FakePlugin(), enabled=['opt_in']) == [sentinel]


def test_register_rejects_empty_name() -> None:
    registry = GeneratorRegistry()
    with pytest.raises(ValueError):
        registry.register(GeneratorSpec(name='', factory=lambda p: object()))  # type: ignore[arg-type]


def test_entry_point_loading_picks_up_third_party_specs() -> None:
    sentinel = object()
    third_party_spec = GeneratorSpec(
        name='lancedb_schema',
        factory=lambda plugin: sentinel,  # type: ignore[arg-type]
        description='Fake third-party generator',
    )
    fake_ep = mock.MagicMock()
    fake_ep.name = 'lancedb_schema'
    fake_ep.load.return_value = third_party_spec

    with mock.patch(
        'py_gen_ml.plugin.registry.importlib.metadata.entry_points',
        return_value=[fake_ep],
    ):
        registry = default_registry(include_entry_points=True)

    assert 'lancedb_schema' in registry.names()
    [built] = registry.build_active(_FakePlugin(), enabled=['lancedb_schema'])
    assert built is sentinel


def test_entry_point_callable_is_invoked() -> None:
    sentinel = object()
    spec = GeneratorSpec(name='callable_ep', factory=lambda p: sentinel)  # type: ignore[arg-type]

    fake_ep = mock.MagicMock()
    fake_ep.name = 'callable_ep'
    fake_ep.load.return_value = lambda: spec  # zero-arg callable returning a spec

    with mock.patch(
        'py_gen_ml.plugin.registry.importlib.metadata.entry_points',
        return_value=[fake_ep],
    ):
        registry = default_registry(include_entry_points=True)

    assert 'callable_ep' in registry.names()


def test_broken_entry_point_is_skipped_not_fatal() -> None:
    fake_ep = mock.MagicMock()
    fake_ep.name = 'broken'
    fake_ep.load.side_effect = RuntimeError('boom')

    with mock.patch(
        'py_gen_ml.plugin.registry.importlib.metadata.entry_points',
        return_value=[fake_ep],
    ):
        registry = default_registry(include_entry_points=True)

    # Built-ins are still present despite the broken entry point.
    assert 'base' in registry.names()
    assert 'broken' not in registry.names()


def test_non_spec_entry_point_is_skipped() -> None:
    fake_ep = mock.MagicMock()
    fake_ep.name = 'wrong_type'
    fake_ep.load.return_value = 'not a spec'

    with mock.patch(
        'py_gen_ml.plugin.registry.importlib.metadata.entry_points',
        return_value=[fake_ep],
    ):
        registry = default_registry(include_entry_points=True)

    assert 'wrong_type' not in registry.names()


def test_parse_enabled_generators_handles_separator() -> None:
    parse = plugin_main._parse_enabled_generators
    assert parse(None) is None
    assert parse('') is None
    assert parse('base') == ['base']
    assert parse('base;patch') == ['base', 'patch']
    assert parse(' base ; patch ') == ['base', 'patch']
    assert parse('base;;patch') == ['base', 'patch']


def test_entry_point_group_is_exposed_publicly() -> None:
    assert pgml.GENERATORS_ENTRY_POINT_GROUP == ENTRY_POINT_GROUP
    assert ENTRY_POINT_GROUP == 'py_gen_ml.generators'


def test_python_type_mapper_scalars() -> None:
    mapper = pgml.PythonTypeMapper()
    field = mock.MagicMock()
    field.kind = __import__('protogen').Kind.INT32
    assert mapper.field_to_type(field) == 'int'
    field.kind = __import__('protogen').Kind.STRING
    assert mapper.field_to_type(field) == 'str'
    field.kind = __import__('protogen').Kind.BOOL
    assert mapper.field_to_type(field) == 'bool'


def test_python_type_mapper_message_and_enum_modes() -> None:
    import protogen

    field = mock.MagicMock()
    field.kind = protogen.Kind.MESSAGE
    field.message.py_ident.py_name = 'Foo'

    assert pgml.PythonTypeMapper().field_to_type(field) == 'Foo'
    assert pgml.PythonTypeMapper(is_patch=True).field_to_type(field) == 'FooPatch'
    assert pgml.PythonTypeMapper(message_suffix='Args').field_to_type(field) == 'FooArgs'

    enum_field = mock.MagicMock()
    enum_field.kind = protogen.Kind.ENUM
    enum_field.enum.py_ident.py_name = 'Color'

    assert pgml.PythonTypeMapper().field_to_type(enum_field) == 'Color'
    assert pgml.PythonTypeMapper(is_patch=True).field_to_type(enum_field) == 'base.Color'
    assert pgml.PythonTypeMapper(enum_alias_prefix='base').field_to_type(enum_field) == 'base.Color'


def test_typemapper_protocol_runtime_check() -> None:
    assert isinstance(pgml.PythonTypeMapper(), pgml.TypeMapper)


def test_public_api_surface() -> None:
    # Sanity: every name listed in __all__ exists on the package.
    for name in pgml.__all__:
        assert hasattr(pgml, name), f'pgml.{name} missing'
