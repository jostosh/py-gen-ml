from py_gen_ml.plugin.generator import GenTask

json_schema_gen_tasks = [
    GenTask(obj_path='pgml_out_test.unit_base', obj_name='Int32Test', path='configs/base/schemas/int32_test.json'),
    GenTask(obj_path='pgml_out_test.unit_base', obj_name='Int64Test', path='configs/base/schemas/int64_test.json'),
    GenTask(obj_path='pgml_out_test.unit_base', obj_name='Uint32Test', path='configs/base/schemas/uint32_test.json'),
    GenTask(obj_path='pgml_out_test.unit_base', obj_name='Uint64Test', path='configs/base/schemas/uint64_test.json'),
    GenTask(obj_path='pgml_out_test.unit_base', obj_name='Sint32Test', path='configs/base/schemas/sint32_test.json'),
    GenTask(obj_path='pgml_out_test.unit_base', obj_name='Sint64Test', path='configs/base/schemas/sint64_test.json'),
    GenTask(obj_path='pgml_out_test.unit_base', obj_name='Fixed32Test', path='configs/base/schemas/fixed32_test.json'),
    GenTask(obj_path='pgml_out_test.unit_base', obj_name='Fixed64Test', path='configs/base/schemas/fixed64_test.json'),
    GenTask(
        obj_path='pgml_out_test.unit_base',
        obj_name='Sfixed32Test',
        path='configs/base/schemas/sfixed32_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_base',
        obj_name='Sfixed64Test',
        path='configs/base/schemas/sfixed64_test.json',
    ),
    GenTask(obj_path='pgml_out_test.unit_base', obj_name='BoolTest', path='configs/base/schemas/bool_test.json'),
    GenTask(obj_path='pgml_out_test.unit_base', obj_name='FloatTest', path='configs/base/schemas/float_test.json'),
    GenTask(obj_path='pgml_out_test.unit_base', obj_name='DoubleTest', path='configs/base/schemas/double_test.json'),
    GenTask(obj_path='pgml_out_test.unit_base', obj_name='StringTest', path='configs/base/schemas/string_test.json'),
    GenTask(obj_path='pgml_out_test.unit_base', obj_name='BytesTest', path='configs/base/schemas/bytes_test.json'),
    GenTask(obj_path='pgml_out_test.unit_base', obj_name='EnumTest', path='configs/base/schemas/enum_test.json'),
    GenTask(
        obj_path='pgml_out_test.unit_base',
        obj_name='EnumDefaultTest',
        path='configs/base/schemas/enum_default_test.json',
    ),
    GenTask(obj_path='pgml_out_test.unit_base', obj_name='OneofTest', path='configs/base/schemas/oneof_test.json'),
    GenTask(
        obj_path='pgml_out_test.unit_base',
        obj_name='RepeatedTest',
        path='configs/base/schemas/repeated_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_base',
        obj_name='OptionalTest',
        path='configs/base/schemas/optional_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_base',
        obj_name='Int32DefaultTest',
        path='configs/base/schemas/int32_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_base',
        obj_name='Int64DefaultTest',
        path='configs/base/schemas/int64_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_base',
        obj_name='Uint32DefaultTest',
        path='configs/base/schemas/uint32_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_base',
        obj_name='Uint64DefaultTest',
        path='configs/base/schemas/uint64_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_base',
        obj_name='Sint32DefaultTest',
        path='configs/base/schemas/sint32_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_base',
        obj_name='Sint64DefaultTest',
        path='configs/base/schemas/sint64_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_base',
        obj_name='Fixed32DefaultTest',
        path='configs/base/schemas/fixed32_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_base',
        obj_name='Fixed64DefaultTest',
        path='configs/base/schemas/fixed64_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_base',
        obj_name='Sfixed32DefaultTest',
        path='configs/base/schemas/sfixed32_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_base',
        obj_name='Sfixed64DefaultTest',
        path='configs/base/schemas/sfixed64_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_base',
        obj_name='BoolDefaultTest',
        path='configs/base/schemas/bool_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_base',
        obj_name='FloatDefaultTest',
        path='configs/base/schemas/float_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_base',
        obj_name='DoubleDefaultTest',
        path='configs/base/schemas/double_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_base',
        obj_name='StringDefaultTest',
        path='configs/base/schemas/string_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_base',
        obj_name='BytesDefaultTest',
        path='configs/base/schemas/bytes_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_base',
        obj_name='OneofDefaultTest',
        path='configs/base/schemas/oneof_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_base',
        obj_name='OptionalDefaultTest',
        path='configs/base/schemas/optional_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_base',
        obj_name='ExplicitCLIArgTest',
        path='configs/base/schemas/explicit_cli_arg_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_base',
        obj_name='ImplicitCLIArgTest',
        path='configs/base/schemas/implicit_cli_arg_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_base',
        obj_name='NestedFooTest',
        path='configs/base/schemas/nested_foo_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_base',
        obj_name='NestedBarTest',
        path='configs/base/schemas/nested_bar_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_base',
        obj_name='RepeatedNestedBarTest',
        path='configs/base/schemas/repeated_nested_bar_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='Int32TestSweep',
        path='configs/sweep/schemas/int32_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='Int64TestSweep',
        path='configs/sweep/schemas/int64_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='Uint32TestSweep',
        path='configs/sweep/schemas/uint32_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='Uint64TestSweep',
        path='configs/sweep/schemas/uint64_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='Sint32TestSweep',
        path='configs/sweep/schemas/sint32_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='Sint64TestSweep',
        path='configs/sweep/schemas/sint64_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='Fixed32TestSweep',
        path='configs/sweep/schemas/fixed32_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='Fixed64TestSweep',
        path='configs/sweep/schemas/fixed64_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='Sfixed32TestSweep',
        path='configs/sweep/schemas/sfixed32_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='Sfixed64TestSweep',
        path='configs/sweep/schemas/sfixed64_test.json',
    ),
    GenTask(obj_path='pgml_out_test.unit_sweep', obj_name='BoolTestSweep', path='configs/sweep/schemas/bool_test.json'),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='FloatTestSweep',
        path='configs/sweep/schemas/float_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='DoubleTestSweep',
        path='configs/sweep/schemas/double_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='StringTestSweep',
        path='configs/sweep/schemas/string_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='BytesTestSweep',
        path='configs/sweep/schemas/bytes_test.json',
    ),
    GenTask(obj_path='pgml_out_test.unit_sweep', obj_name='EnumTestSweep', path='configs/sweep/schemas/enum_test.json'),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='EnumDefaultTestSweep',
        path='configs/sweep/schemas/enum_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='OneofTestSweep',
        path='configs/sweep/schemas/oneof_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='RepeatedTestSweep',
        path='configs/sweep/schemas/repeated_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='OptionalTestSweep',
        path='configs/sweep/schemas/optional_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='Int32DefaultTestSweep',
        path='configs/sweep/schemas/int32_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='Int64DefaultTestSweep',
        path='configs/sweep/schemas/int64_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='Uint32DefaultTestSweep',
        path='configs/sweep/schemas/uint32_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='Uint64DefaultTestSweep',
        path='configs/sweep/schemas/uint64_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='Sint32DefaultTestSweep',
        path='configs/sweep/schemas/sint32_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='Sint64DefaultTestSweep',
        path='configs/sweep/schemas/sint64_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='Fixed32DefaultTestSweep',
        path='configs/sweep/schemas/fixed32_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='Fixed64DefaultTestSweep',
        path='configs/sweep/schemas/fixed64_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='Sfixed32DefaultTestSweep',
        path='configs/sweep/schemas/sfixed32_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='Sfixed64DefaultTestSweep',
        path='configs/sweep/schemas/sfixed64_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='BoolDefaultTestSweep',
        path='configs/sweep/schemas/bool_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='FloatDefaultTestSweep',
        path='configs/sweep/schemas/float_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='DoubleDefaultTestSweep',
        path='configs/sweep/schemas/double_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='StringDefaultTestSweep',
        path='configs/sweep/schemas/string_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='BytesDefaultTestSweep',
        path='configs/sweep/schemas/bytes_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='OneofDefaultTestSweep',
        path='configs/sweep/schemas/oneof_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='OptionalDefaultTestSweep',
        path='configs/sweep/schemas/optional_default_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='ExplicitCLIArgTestSweep',
        path='configs/sweep/schemas/explicit_cli_arg_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='ImplicitCLIArgTestSweep',
        path='configs/sweep/schemas/implicit_cli_arg_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='NestedFooTestSweep',
        path='configs/sweep/schemas/nested_foo_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='NestedBarTestSweep',
        path='configs/sweep/schemas/nested_bar_test.json',
    ),
    GenTask(
        obj_path='pgml_out_test.unit_sweep',
        obj_name='RepeatedNestedBarTestSweep',
        path='configs/sweep/schemas/repeated_nested_bar_test.json',
    ),
]