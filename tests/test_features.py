import sys
from pathlib import Path

import pytest
from pydantic import BaseModel

sys.path.append(str(Path(__file__).parent.absolute()))

from unittest.mock import Mock, patch

from typer.testing import CliRunner

from .pgml_out_test import (
    explicit_cli_arg_test_entrypoint,
    implicit_cli_arg_test_entrypoint,
    unit_base,
)
from .pgml_out_test.explicit_cli_arg_test_entrypoint import \
    app as explicit_cli_arg_test_app
from .pgml_out_test.implicit_cli_arg_test_entrypoint import \
    app as implicit_cli_arg_test_app

cli_runner = CliRunner()


def test_oneof() -> None:
    assert unit_base.OneofTest(value=1).value == 1
    assert unit_base.OneofTest(value='test').value == 'test'


def test_repeated() -> None:
    assert unit_base.RepeatedTest(values=[1, 2, 3]).values == [1, 2, 3]


def test_optional() -> None:
    assert unit_base.OptionalTest(value=1).value == 1
    assert unit_base.OptionalTest().value is None


def test_default() -> None:
    assert unit_base.Int32DefaultTest().value == 1
    assert unit_base.Int64DefaultTest().value == 1
    assert unit_base.Uint32DefaultTest().value == 1
    assert unit_base.Uint64DefaultTest().value == 1
    assert unit_base.Sint32DefaultTest().value == 1
    assert unit_base.Sint64DefaultTest().value == 1
    assert unit_base.Fixed32DefaultTest().value == 1
    assert unit_base.Fixed64DefaultTest().value == 1
    assert unit_base.Sfixed32DefaultTest().value == 1
    assert unit_base.Sfixed64DefaultTest().value == 1
    assert unit_base.FloatDefaultTest().value == 1
    assert unit_base.DoubleDefaultTest().value == 1
    assert unit_base.BoolDefaultTest().value == True
    assert unit_base.StringDefaultTest().value == 'test'
    assert unit_base.BytesDefaultTest().value == b'test'
    assert unit_base.EnumDefaultTest().value == unit_base.Enum.VALUE_1


def assert_base_model_eq(a: BaseModel, b: BaseModel) -> None:
    assert a.model_dump() == b.model_dump()


@pytest.fixture
def mocked_explicit_cli_arg_run_trial() -> Mock:
    with patch.object(explicit_cli_arg_test_entrypoint, 'run_trial') as mock_run_trial:
        yield mock_run_trial


def test_cli_arg_explicit_no_override(tmp_path: Path, mocked_explicit_cli_arg_run_trial: Mock) -> None:
    config_path = tmp_path.joinpath('config.yaml')
    config_path.write_text('bar: test')
    result = cli_runner.invoke(explicit_cli_arg_test_app, ['--config-paths', str(config_path)])
    assert result.exit_code == 0
    mocked_explicit_cli_arg_run_trial.assert_called_once()
    assert_base_model_eq(mocked_explicit_cli_arg_run_trial.call_args[0][0], unit_base.ExplicitCLIArgTest(bar='test'))


def test_cli_arg_explicit_override(tmp_path: Path, mocked_explicit_cli_arg_run_trial: Mock) -> None:
    config_path = tmp_path.joinpath('config.yaml')
    config_path.write_text('bar: test')
    result = cli_runner.invoke(explicit_cli_arg_test_app, ['--config-paths', str(config_path), '--foo', 'test2'])
    assert result.exit_code == 0
    mocked_explicit_cli_arg_run_trial.assert_called_once()
    assert_base_model_eq(mocked_explicit_cli_arg_run_trial.call_args[0][0], unit_base.ExplicitCLIArgTest(bar='test2'))


@pytest.fixture
def mocked_implicit_cli_arg_run_trial() -> Mock:
    with patch.object(implicit_cli_arg_test_entrypoint, 'run_trial') as mock_run_trial:
        yield mock_run_trial


def test_cli_arg_implicit_no_override(tmp_path: Path, mocked_implicit_cli_arg_run_trial: Mock) -> None:
    config_path = tmp_path.joinpath('config.yaml')
    config_path.write_text('bar: test')
    result = cli_runner.invoke(implicit_cli_arg_test_app, ['--config-paths', str(config_path)])
    assert result.exit_code == 0
    mocked_implicit_cli_arg_run_trial.assert_called_once()
    assert_base_model_eq(mocked_implicit_cli_arg_run_trial.call_args[0][0], unit_base.ImplicitCLIArgTest(bar='test'))


def test_cli_arg_implicit_override(tmp_path: Path, mocked_implicit_cli_arg_run_trial: Mock) -> None:
    config_path = tmp_path.joinpath('config.yaml')
    config_path.write_text('bar: test')
    result = cli_runner.invoke(implicit_cli_arg_test_app, ['--config-paths', str(config_path), '--bar', 'test2'])
    assert result.exit_code == 0
    mocked_implicit_cli_arg_run_trial.assert_called_once()
    assert_base_model_eq(mocked_implicit_cli_arg_run_trial.call_args[0][0], unit_base.ImplicitCLIArgTest(bar='test2'))
