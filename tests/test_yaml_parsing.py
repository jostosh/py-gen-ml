from pathlib import Path

from pydantic import BaseModel

from .pgml_out_test import unit_base


def assert_base_model_eq(a: BaseModel, b: BaseModel) -> None:
    assert a.model_dump() == b.model_dump()


def test_nested_yaml_parsing(tmp_path: Path) -> None:
    config_path = tmp_path.joinpath('config.yaml')
    config_path.write_text('foo_0:\n  foo: test_0\nfoo_1:\n  foo: test_1')
    parsed = unit_base.NestedBarTest.from_yaml_file(str(config_path))
    assert_base_model_eq(
        parsed,
        unit_base.NestedBarTest(
            foo_0=unit_base.NestedFooTest(foo='test_0'),
            foo_1=unit_base.NestedFooTest(foo='test_1'),
        ),
    )


def test_nested_yaml_parsing_with_internal_references(tmp_path: Path) -> None:
    config_path = tmp_path.joinpath('config.yaml')
    config_path.write_text("foo_0:\n  foo: test_0\nfoo_1:\n  foo: '#/foo_0/foo'")
    parsed = unit_base.NestedBarTest.from_yaml_file(str(config_path))
    assert_base_model_eq(
        parsed,
        unit_base.NestedBarTest(
            foo_0=unit_base.NestedFooTest(foo='test_0'),
            foo_1=unit_base.NestedFooTest(foo='test_0'),
        ),
    )


def test_nested_yaml_parsing_with_relative_internal_references(tmp_path: Path) -> None:
    config_path = tmp_path.joinpath('config.yaml')
    config_path.write_text("foo_0:\n  foo: test_0\nfoo_1:\n  foo: '#../foo_0/foo'")
    parsed = unit_base.NestedBarTest.from_yaml_file(str(config_path))
    assert_base_model_eq(
        parsed,
        unit_base.NestedBarTest(
            foo_0=unit_base.NestedFooTest(foo='test_0'),
            foo_1=unit_base.NestedFooTest(foo='test_0'),
        ),
    )


def test_nested_yaml_parsing_with_def_internal_references(tmp_path: Path) -> None:
    config_path = tmp_path.joinpath('config.yaml')
    config_path.write_text("foo_0:\n  foo: test_0\nfoo_1:\n  foo: '#/_defs_/foo'\n_defs_:\n  foo: test_1")
    parsed = unit_base.NestedBarTest.from_yaml_file(str(config_path))
    assert_base_model_eq(
        parsed,
        unit_base.NestedBarTest(
            foo_0=unit_base.NestedFooTest(foo='test_0'),
            foo_1=unit_base.NestedFooTest(foo='test_1'),
        ),
    )


def test_nested_yaml_external_references(tmp_path: Path) -> None:
    config_path = tmp_path.joinpath('config.yaml')
    config_path.write_text("foo_0:\n  foo: test_0\nfoo_1:\n  foo: '!external.yaml#/foo_0/foo'")
    external_path = tmp_path.joinpath('external.yaml')
    external_path.write_text('foo_0:\n  foo: test_1')
    parsed = unit_base.NestedBarTest.from_yaml_file(str(config_path))
    assert_base_model_eq(
        parsed,
        unit_base.NestedBarTest(
            foo_0=unit_base.NestedFooTest(foo='test_0'),
            foo_1=unit_base.NestedFooTest(foo='test_1'),
        ),
    )


def test_repeated_nested_yaml_parsing(tmp_path: Path) -> None:
    config_path = tmp_path.joinpath('config.yaml')
    config_path.write_text(
        """
bar:
  - foo_0:
      foo: test_0
    foo_1:
      foo: test_1
  - foo_0:
      foo: test_2
    foo_1:
      foo: test_3
""",
    )
    parsed = unit_base.RepeatedNestedBarTest.from_yaml_file(str(config_path))
    assert_base_model_eq(
        parsed,
        unit_base.RepeatedNestedBarTest(
            bar=[
                unit_base.NestedBarTest(
                    foo_0=unit_base.NestedFooTest(foo='test_0'),
                    foo_1=unit_base.NestedFooTest(foo='test_1'),
                ),
                unit_base.NestedBarTest(
                    foo_0=unit_base.NestedFooTest(foo='test_2'),
                    foo_1=unit_base.NestedFooTest(foo='test_3'),
                ),
            ],
        ),
    )


def test_repeated_nested_yaml_parsing_with_internal_references(tmp_path: Path) -> None:
    config_path = tmp_path.joinpath('config.yaml')
    config_path.write_text("""
bar:
  - foo_0:
      foo: test_0
    foo_1:
      foo: '#/bar[0]/foo_0/foo'
""")
    parsed = unit_base.RepeatedNestedBarTest.from_yaml_file(str(config_path))
    assert_base_model_eq(
        parsed,
        unit_base.RepeatedNestedBarTest(
            bar=[
                unit_base.NestedBarTest(
                    foo_0=unit_base.NestedFooTest(foo='test_0'),
                    foo_1=unit_base.NestedFooTest(foo='test_0'),
                ),
            ],
        ),
    )


def test_repeated_nested_yaml_parsing_with_relative_internal_references(tmp_path: Path) -> None:
    config_path = tmp_path.joinpath('config.yaml')
    config_path.write_text("""
bar:
  - foo_0:
      foo: test_0
    foo_1:
      foo: '#../../bar[0]/foo_0/foo'
""")
    parsed = unit_base.RepeatedNestedBarTest.from_yaml_file(str(config_path))
    assert_base_model_eq(
        parsed,
        unit_base.RepeatedNestedBarTest(
            bar=[
                unit_base.NestedBarTest(
                    foo_0=unit_base.NestedFooTest(foo='test_0'),
                    foo_1=unit_base.NestedFooTest(foo='test_0'),
                ),
            ],
        ),
    )


def test_repeated_nested_yaml_parsing_with_def_internal_references(tmp_path: Path) -> None:
    config_path = tmp_path.joinpath('config.yaml')
    config_path.write_text(
        """
bar:
  - foo_0:
      foo: test_0
    foo_1:
      foo: '#/_defs_/foo'
_defs_:
  foo: test_1
""",
    )
    parsed = unit_base.RepeatedNestedBarTest.from_yaml_file(str(config_path))
    assert_base_model_eq(
        parsed,
        unit_base.RepeatedNestedBarTest(
            bar=[
                unit_base.NestedBarTest(
                    foo_0=unit_base.NestedFooTest(foo='test_0'),
                    foo_1=unit_base.NestedFooTest(foo='test_1'),
                ),
            ],
        ),
    )


def test_repeated_nested_yaml_external_references(tmp_path: Path) -> None:
    config_path = tmp_path.joinpath('config.yaml')
    config_path.write_text("""
bar:
  - foo_0:
      foo: test_0
    foo_1:
      foo: '!external.yaml#/foo_0/foo'
""")
    external_path = tmp_path.joinpath('external.yaml')
    external_path.write_text('foo_0:\n  foo: test_1')
    parsed = unit_base.RepeatedNestedBarTest.from_yaml_file(str(config_path))
    assert_base_model_eq(
        parsed,
        unit_base.RepeatedNestedBarTest(
            bar=[
                unit_base.NestedBarTest(
                    foo_0=unit_base.NestedFooTest(foo='test_0'),
                    foo_1=unit_base.NestedFooTest(foo='test_1'),
                ),
            ],
        ),
    )


def test_repeated_external_whole_file_references(tmp_path: Path) -> None:
    config_path = tmp_path.joinpath('config.yaml')
    config_path.write_text("""
bar:
  - foo_0:
      foo: test_0
    foo_1: '!external.yaml'
""")
    external_path = tmp_path.joinpath('external.yaml')
    external_path.write_text('foo: test_1')
    parsed = unit_base.RepeatedNestedBarTest.from_yaml_file(str(config_path))
    assert_base_model_eq(
        parsed,
        unit_base.RepeatedNestedBarTest(
            bar=[
                unit_base.NestedBarTest(
                    foo_0=unit_base.NestedFooTest(foo='test_0'),
                    foo_1=unit_base.NestedFooTest(foo='test_1'),
                ),
            ],
        ),
    )
