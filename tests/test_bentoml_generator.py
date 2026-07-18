"""Tests for the BentoML generator fixtures."""
from __future__ import annotations

from pathlib import Path


def test_unit_bentoml_fixture_emits_models_factory_and_clients() -> None:
    source = Path(__file__).parent.joinpath('pgml_out_test', 'unit_bentoml.py').read_text()
    assert 'class PredictRequestTest(BaseModel):' in source
    assert 'class PredictResponseTest(BaseModel):' in source
    assert 'def classifier_test_service_kwargs(' in source
    assert 'kwargs["workers"] = config.workers' in source
    assert 'kwargs["traffic"] = {"timeout": config.timeout_s}' in source
    assert 'def create_classifier_test_service(' in source
    assert '@bentoml.service(**service_kwargs)' in source
    assert "route='/predict'" in source
    assert 'input_spec=PredictRequestTest' in source
    assert 'output_spec=PredictResponseTest' in source
    assert 'def predict(self, **kwargs: typing.Any) -> PredictResponseTest:' in source
    assert 'PredictRequestTest.model_validate(kwargs)' in source
    assert 'def call_classifier_test_predict_sync(' in source
    assert 'async def call_classifier_test_predict_async(' in source
    assert 'import bentoml' in source
    assert 'from pydantic import BaseModel' in source


def test_unit_proto_annotates_bentoml_service() -> None:
    source = Path(__file__).parent.joinpath('protos', 'unit.proto').read_text()
    assert 'service ClassifierTest' in source
    assert 'option (pgml.bentoml)' in source
    assert 'option (pgml.bentoml_method)' in source
    assert 'option (pgml.bentoml_config)' in source


def test_docs_bentoml_demo_fixture_exists() -> None:
    path = (Path(__file__).resolve().parents[1] / 'docs' / 'snippets' / 'src' / 'pgml_out' / 'bentoml_demo_bentoml.py')
    source = path.read_text()
    assert 'def create_classifier_service(' in source
    assert 'def call_classifier_predict_sync(' in source
