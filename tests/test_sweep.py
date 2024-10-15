from pathlib import Path

import optuna
import pytest

import py_gen_ml as pgml
from py_gen_ml.sweep.sweep import FloatUniform, IntUniform

from .pgml_out_test import unit_base, unit_sweep


@pytest.mark.parametrize(
    'class_name',
    [
        'Int32Test',
        'Int64Test',
        'Uint32Test',
        'Uint64Test',
        'FloatTest',
        'DoubleTest',
        'Fixed32Test',
        'Fixed64Test',
        'Sfixed32Test',
        'Sfixed64Test',
    ],
)
def test_numeric_sweep(class_name: str) -> None:
    config = getattr(unit_base, class_name)(value=10)
    if class_name in ['FloatTest', 'DoubleTest']:
        sweep = getattr(unit_sweep, f'{class_name}Sweep')(value=FloatUniform(low=1, high=5, step=1))
    else:
        sweep = getattr(unit_sweep, f'{class_name}Sweep')(value=IntUniform(low=1, high=5, step=1))

    def trial_fn(trial: optuna.Trial) -> float:
        patch = pgml.OptunaSampler(trial).sample(sweep)
        patched_config = config.merge(patch)
        return patched_config.value

    study = optuna.create_study(direction='maximize',)
    study.optimize(trial_fn, n_trials=50)

    for trial in study.get_trials():
        assert trial.value is not None
        assert trial.value <= 5
        assert trial.value > 0


def test_bool_any_sweep(tmp_path: Path) -> None:
    config_path = tmp_path / 'config.yaml'
    config_path.write_text('value: true')
    sweep_path = tmp_path / 'sweep.yaml'
    sweep_path.write_text('value: any')

    config = unit_base.BoolTest.from_yaml_file(str(config_path))
    sweep = unit_sweep.BoolTestSweep.from_yaml_file(str(sweep_path))

    def trial_fn(trial: optuna.Trial) -> float:
        patch = pgml.OptunaSampler(trial).sample(sweep)
        patched_config = config.merge(patch)
        return 1.0 if patched_config.value else 0.0

    study = optuna.create_study(direction='maximize',)
    study.optimize(trial_fn, n_trials=50)

    for trial in study.get_trials():
        assert trial.value is not None
        assert trial.value == 1.0 or trial.value == 0.0


@pytest.mark.parametrize('class_name', [
    'StringTest',
    'BytesTest',
])
def test_string_bytes_sweep(class_name: str, tmp_path: Path) -> None:
    config_path = tmp_path / 'config.yaml'
    config_path.write_text(f'value: "hello"')
    sweep_path = tmp_path / 'sweep.yaml'
    sweep_path.write_text(f'value:\n  options: ["foo", "bar"]')

    config = getattr(unit_base, class_name).from_yaml_file(str(config_path))
    sweep = getattr(unit_sweep, f'{class_name}Sweep').from_yaml_file(str(sweep_path))

    def trial_fn(trial: optuna.Trial) -> float:
        patch = pgml.OptunaSampler(trial).sample(sweep)
        patched_config = config.merge(patch)
        assert patched_config.value not in ['hello', b'hello']
        return 1.0 if patched_config.value in ['foo', b'foo'] else 0.0

    study = optuna.create_study(direction='maximize',)
    study.optimize(trial_fn, n_trials=50)

    for trial in study.get_trials():
        assert trial.value is not None
        assert trial.value == 1.0 or trial.value == 0.0
