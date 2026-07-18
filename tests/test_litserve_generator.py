"""Source-level asserts for the LitServe generator fixture."""
from __future__ import annotations

from pathlib import Path


def test_unit_litserve_fixture_emits_models_factory_and_clients() -> None:
    source = Path(__file__).parent.joinpath('pgml_out_test', 'unit_litserve.py').read_text()
    assert 'class PredictRequestTest(BaseModel):' in source
    assert 'class PredictResponseTest(BaseModel):' in source
    assert 'def classifier_test_server_kwargs(' in source
    assert 'class ClassifierTestPredictAPI(ls.LitAPI):' in source
    assert 'def create_classifier_test_predict_api(' in source
    assert 'def create_classifier_test_server(' in source
    assert 'return ls.LitServer(apis if len(apis) > 1 else apis[0], **kwargs)' in source
    assert 'import litserve as ls' in source
    assert 'import httpx' in source
    assert 'def call_classifier_test_predict_sync(' in source
    assert 'async def call_classifier_test_predict_async(' in source
    assert "api_path='/predict'" in source or 'api_path="/predict"' in source


def test_unit_proto_annotates_litserve_service() -> None:
    source = Path(__file__).parent.joinpath('protos', 'unit.proto').read_text()
    assert 'option (pgml.litserve)' in source
    assert 'option (pgml.litserve_method)' in source
    assert 'option (pgml.litserve_config)' in source


def test_docs_litserve_demo_fixture_exists() -> None:
    path = (
        Path(__file__).resolve().parents[1]
        / 'docs'
        / 'snippets'
        / 'src'
        / 'pgml_out'
        / 'litserve_demo_litserve.py'
    )
    assert path.is_file()
    source = path.read_text()
    assert 'def create_classifier_server(' in source
    assert 'def create_classifier_predict_api(' in source
