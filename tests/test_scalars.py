import pathlib

from .pgml_out_test import unit_base


def test_int32() -> None:
    assert unit_base.Int32Test(value=1).value == 1


def test_int64() -> None:
    assert unit_base.Int64Test(value=1).value == 1


def test_uint32() -> None:
    assert unit_base.Uint32Test(value=1).value == 1


def test_uint64() -> None:
    assert unit_base.Uint64Test(value=1).value == 1


def test_sint32() -> None:
    assert unit_base.Sint32Test(value=1).value == 1


def test_sint64() -> None:
    assert unit_base.Sint64Test(value=1).value == 1


def test_fixed32() -> None:
    assert unit_base.Fixed32Test(value=1).value == 1


def test_fixed64() -> None:
    assert unit_base.Fixed64Test(value=1).value == 1


def test_sfixed32() -> None:
    assert unit_base.Sfixed32Test(value=1).value == 1


def test_sfixed64() -> None:
    assert unit_base.Sfixed64Test(value=1).value == 1


def test_float() -> None:
    assert unit_base.FloatTest(value=1).value == 1


def test_double() -> None:
    assert unit_base.DoubleTest(value=1).value == 1


def test_bool() -> None:
    assert unit_base.BoolTest(value=True).value == True


def test_string() -> None:
    assert unit_base.StringTest(value='test').value == 'test'


def test_bytes() -> None:
    assert unit_base.BytesTest(value=b'test').value == b'test'


def test_enum() -> None:
    assert unit_base.EnumTest(value=unit_base.Enum.VALUE_1).value == unit_base.Enum.VALUE_1


def test_int32_default() -> None:
    assert unit_base.Int32DefaultTest().value == 1


def test_int64_default() -> None:
    assert unit_base.Int64DefaultTest().value == 1


def test_uint32_default() -> None:
    assert unit_base.Uint32DefaultTest().value == 1


def test_uint64_default() -> None:
    assert unit_base.Uint64DefaultTest().value == 1


def test_sint32_default() -> None:
    assert unit_base.Sint32DefaultTest().value == 1


def test_sint64_default() -> None:
    assert unit_base.Sint64DefaultTest().value == 1


def test_fixed32_default() -> None:
    assert unit_base.Fixed32DefaultTest().value == 1


def test_fixed64_default() -> None:
    assert unit_base.Fixed64DefaultTest().value == 1


def test_sfixed32_default() -> None:
    assert unit_base.Sfixed32DefaultTest().value == 1


def test_sfixed64_default() -> None:
    assert unit_base.Sfixed64DefaultTest().value == 1


def test_float_default() -> None:
    assert unit_base.FloatDefaultTest().value == 1


def test_double_default() -> None:
    assert unit_base.DoubleDefaultTest().value == 1


def test_bool_default() -> None:
    assert unit_base.BoolDefaultTest().value == True


def test_string_default() -> None:
    assert unit_base.StringDefaultTest().value == 'test'


def test_bytes_default() -> None:
    assert unit_base.BytesDefaultTest().value == b'test'


def test_enum_default() -> None:
    assert unit_base.EnumDefaultTest().value == unit_base.Enum.VALUE_1


def test_int32_yaml(tmp_path: pathlib.Path) -> None:
    test_file = tmp_path / 'test.yaml'
    test_file.write_text('value: 1')
    assert unit_base.Int32Test.from_yaml_file(str(test_file)) == unit_base.Int32Test(value=1)


def test_int64_yaml(tmp_path: pathlib.Path) -> None:
    test_file = tmp_path / 'test.yaml'
    test_file.write_text('value: 1')
    assert unit_base.Int64Test.from_yaml_file(str(test_file)) == unit_base.Int64Test(value=1)


def test_uint32_yaml(tmp_path: pathlib.Path) -> None:
    test_file = tmp_path / 'test.yaml'
    test_file.write_text('value: 1')
    assert unit_base.Uint32Test.from_yaml_file(str(test_file)) == unit_base.Uint32Test(value=1)


def test_uint64_yaml(tmp_path: pathlib.Path) -> None:
    test_file = tmp_path / 'test.yaml'
    test_file.write_text('value: 1')
    assert unit_base.Uint64Test.from_yaml_file(str(test_file)) == unit_base.Uint64Test(value=1)


def test_sint32_yaml(tmp_path: pathlib.Path) -> None:
    test_file = tmp_path / 'test.yaml'
    test_file.write_text('value: 1')
    assert unit_base.Sint32Test.from_yaml_file(str(test_file)) == unit_base.Sint32Test(value=1)


def test_sint64_yaml(tmp_path: pathlib.Path) -> None:
    test_file = tmp_path / 'test.yaml'
    test_file.write_text('value: 1')
    assert unit_base.Sint64Test.from_yaml_file(str(test_file)) == unit_base.Sint64Test(value=1)


def test_fixed32_yaml(tmp_path: pathlib.Path) -> None:
    test_file = tmp_path / 'test.yaml'
    test_file.write_text('value: 1')
    assert unit_base.Fixed32Test.from_yaml_file(str(test_file)) == unit_base.Fixed32Test(value=1)


def test_fixed64_yaml(tmp_path: pathlib.Path) -> None:
    test_file = tmp_path / 'test.yaml'
    test_file.write_text('value: 1')
    assert unit_base.Fixed64Test.from_yaml_file(str(test_file)) == unit_base.Fixed64Test(value=1)


def test_sfixed32_yaml(tmp_path: pathlib.Path) -> None:
    test_file = tmp_path / 'test.yaml'
    test_file.write_text('value: 1')
    assert unit_base.Sfixed32Test.from_yaml_file(str(test_file)) == unit_base.Sfixed32Test(value=1)


def test_sfixed64_yaml(tmp_path: pathlib.Path) -> None:
    test_file = tmp_path / 'test.yaml'
    test_file.write_text('value: 1')
    assert unit_base.Sfixed64Test.from_yaml_file(str(test_file)) == unit_base.Sfixed64Test(value=1)


def test_float_yaml(tmp_path: pathlib.Path) -> None:
    test_file = tmp_path / 'test.yaml'
    test_file.write_text('value: 1')
    assert unit_base.FloatTest.from_yaml_file(str(test_file)) == unit_base.FloatTest(value=1)


def test_double_yaml(tmp_path: pathlib.Path) -> None:
    test_file = tmp_path / 'test.yaml'
    test_file.write_text('value: 1')
    assert unit_base.DoubleTest.from_yaml_file(str(test_file)) == unit_base.DoubleTest(value=1)


def test_bool_yaml(tmp_path: pathlib.Path) -> None:
    test_file = tmp_path / 'test.yaml'
    test_file.write_text('value: true')
    assert unit_base.BoolTest.from_yaml_file(str(test_file)) == unit_base.BoolTest(value=True)


def test_string_yaml(tmp_path: pathlib.Path) -> None:
    test_file = tmp_path / 'test.yaml'
    test_file.write_text('value: test')
    assert unit_base.StringTest.from_yaml_file(str(test_file)) == unit_base.StringTest(value='test')


def test_bytes_yaml(tmp_path: pathlib.Path) -> None:
    test_file = tmp_path / 'test.yaml'
    test_file.write_text('value: test')
    assert unit_base.BytesTest.from_yaml_file(str(test_file)) == unit_base.BytesTest(value=b'test')


def test_enum_yaml(tmp_path: pathlib.Path) -> None:
    test_file = tmp_path / 'test.yaml'
    test_file.write_text('value: VALUE_1')
    assert unit_base.EnumTest.from_yaml_file(str(test_file)) == unit_base.EnumTest(value=unit_base.Enum.VALUE_1)
