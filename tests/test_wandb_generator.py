"""Source-level asserts for the W&B generator fixture."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

FIXTURE = Path(__file__).parent.joinpath('pgml_out_test', 'unit_wandb.py')


def test_unit_wandb_fixture_emits_init_and_log_helpers() -> None:
    source = FIXTURE.read_text()
    assert 'class RunConfigTest(BaseModel):' in source
    assert 'class MetricSetTest(BaseModel):' in source
    assert 'def init_run_config_test_run(' in source
    assert 'def log_metric_set_test(' in source
    assert "('optimizer.learning_rate', 'optimizer.learning_rate')" in source
    assert 'wandb.init(' in source


def test_unit_proto_annotates_wandb() -> None:
    source = Path(__file__).parent.joinpath('protos', 'unit.proto').read_text()
    assert 'option (pgml.wandb)' in source


def test_run_config_config_flatten(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip('wandb')
    monkeypatch.syspath_prepend(str(Path(__file__).parent))
    from pgml_out_test.unit_wandb import (
        OptimizerConfigTest,
        RunConfigTest,
        run_config_test_config,
    )

    config = RunConfigTest(
        run_name='exp-1',
        epochs=3,
        optimizer=OptimizerConfigTest(learning_rate=0.01, weight_decay=1e-4),
    )
    cfg = run_config_test_config(config)
    assert cfg['epochs'] == 3
    assert cfg['optimizer.learning_rate'] == 0.01
    assert 'run_name' not in cfg  # TAG, not PARAM


def test_log_metrics_calls_wandb(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip('wandb')
    monkeypatch.syspath_prepend(str(Path(__file__).parent))
    import pgml_out_test.unit_wandb as mod
    from pgml_out_test.unit_wandb import MetricSetTest

    mock_log = MagicMock()
    with patch.object(mod.wandb, 'log', mock_log):
        mod.log_metric_set_test(MetricSetTest(accuracy=0.9, loss=0.1), step=2)
    mock_log.assert_called_once_with({'accuracy': 0.9, 'loss': 0.1}, step=2)
