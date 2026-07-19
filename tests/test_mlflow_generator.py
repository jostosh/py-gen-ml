"""Source-level asserts for the MLflow generator fixture."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

FIXTURE = Path(__file__).parent.joinpath('pgml_out_test', 'unit_mlflow.py')


def test_unit_mlflow_fixture_emits_run_and_metric_helpers() -> None:
    source = FIXTURE.read_text()
    assert 'class RunConfigTest(BaseModel):' in source
    assert 'class MetricSetTest(BaseModel):' in source
    assert 'def start_run_config_test_run(' in source
    assert 'def log_run_config_test_params(' in source
    assert 'def log_metric_set_test(' in source
    assert "('optimizer.learning_rate', 'optimizer.learning_rate')" in source
    assert "('run_name', 'run_name')" in source


def test_unit_mlflow_fixture_emits_registry_helpers() -> None:
    source = FIXTURE.read_text()
    assert "MODEL_REGISTRY_TEST_REGISTERED_NAME = 'unit_classifier'" in source
    assert 'def model_registry_test_signature(' in source
    assert 'def register_model_registry_test(' in source
    assert 'def resolve_model_registry_test_uri(' in source
    assert "ColSpec(Array(DataType.float), 'features')" in source
    assert "ColSpec(DataType.integer, 'label')" in source
    assert "ColSpec(DataType.float, 'score')" in source


def test_unit_proto_annotates_mlflow() -> None:
    source = Path(__file__).parent.joinpath('protos', 'unit.proto').read_text()
    assert 'option (pgml.mlflow)' in source
    assert '(pgml.tracking_field)' in source
    assert 'registered_model_name' in source
    assert 'signature_input' in source


def test_registry_signature_builds(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip('mlflow')
    monkeypatch.syspath_prepend(str(Path(__file__).parent))
    from pgml_out_test.unit_mlflow import (
        MODEL_REGISTRY_TEST_REGISTERED_NAME,
        model_registry_test_signature,
        resolve_model_registry_test_uri,
    )

    signature = model_registry_test_signature()
    assert [c.name for c in signature.inputs] == ['features']
    assert [c.name for c in signature.outputs] == ['label', 'score']
    assert resolve_model_registry_test_uri(stage='Production',
                                          ) == (f'models:/{MODEL_REGISTRY_TEST_REGISTERED_NAME}/Production')
    assert resolve_model_registry_test_uri(alias='champion',
                                          ) == (f'models:/{MODEL_REGISTRY_TEST_REGISTERED_NAME}@champion')


def test_run_config_params_flatten_nested(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip('mlflow')
    monkeypatch.syspath_prepend(str(Path(__file__).parent))
    from pgml_out_test.unit_mlflow import (
        OptimizerConfigTest,
        RunConfigTest,
        run_config_test_params,
    )

    config = RunConfigTest(
        run_name='exp-1',
        epochs=3,
        optimizer=OptimizerConfigTest(learning_rate=0.01, weight_decay=1e-4),
    )
    params = run_config_test_params(config)
    assert params['epochs'] == 3
    assert params['optimizer.learning_rate'] == 0.01
    assert params['tag.run_name'] == 'exp-1'


def test_log_metrics_calls_mlflow(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip('mlflow')
    monkeypatch.syspath_prepend(str(Path(__file__).parent))
    import pgml_out_test.unit_mlflow as mod
    from pgml_out_test.unit_mlflow import MetricSetTest

    mock_log = MagicMock()
    with patch.object(mod.mlflow, 'log_metrics', mock_log):
        mod.log_metric_set_test(MetricSetTest(accuracy=0.9, loss=0.1), step=2)
    mock_log.assert_called_once()
    args, kwargs = mock_log.call_args
    assert args[0] == {'accuracy': 0.9, 'loss': 0.1}
    assert kwargs.get('step') == 2
