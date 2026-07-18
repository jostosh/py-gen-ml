"""Runtime integration tests for generated BentoML server and client."""
from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

bentoml = pytest.importorskip('bentoml')
pytest.importorskip('starlette')

from starlette.testclient import TestClient  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
SNIPPETS_SRC = REPO / 'docs' / 'snippets' / 'src'


def _predict(request):  # type: ignore[no-untyped-def]
    from pgml_out.bentoml_demo_bentoml import PredictResponse

    score = sum(request.features) / max(len(request.features), 1)
    return PredictResponse(label=1 if score > 0.5 else 0, score=float(score))


@pytest.fixture
def classifier_service(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.syspath_prepend(str(SNIPPETS_SRC))
    from pgml_out.bentoml_demo_base import ClassifierServeConfig
    from pgml_out.bentoml_demo_bentoml import create_classifier_service

    return create_classifier_service(
        predict=_predict,
        config=ClassifierServeConfig(workers=1, timeout_s=30.0),
    )


def test_generated_service_asgi_roundtrip(classifier_service) -> None:
    with TestClient(classifier_service.to_asgi()) as client:
        response = client.post('/predict', json={'features': [0.8, 0.9, 0.7]})
    assert response.status_code == 200
    body = response.json()
    assert body['label'] == 1
    assert body['score'] == pytest.approx((0.8 + 0.9 + 0.7) / 3)


def test_generated_client_against_live_server(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(SNIPPETS_SRC))
    port = 30998
    env = {**os.environ, 'PYTHONPATH': str(SNIPPETS_SRC)}
    proc = subprocess.Popen(
        [
            sys.executable,
            '-m',
            'bentoml',
            'serve',
            'snippets.bentoml_serve_demo:Service',
            '-p',
            str(port),
        ],
        cwd=str(REPO),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    url = f'http://127.0.0.1:{port}'
    try:
        deadline = time.time() + 30
        while time.time() < deadline:
            try:
                if bentoml.SyncHTTPClient(url, server_ready_timeout=1).is_ready():
                    break
            except Exception:
                time.sleep(0.5)
        else:
            out = proc.stdout.read().decode() if proc.stdout else ''
            raise AssertionError(f'server not ready:\n{out}')

        from pgml_out.bentoml_demo_bentoml import (
            PredictRequest,
            PredictResponse,
            call_classifier_predict_sync,
        )

        high = call_classifier_predict_sync(
            PredictRequest(features=[0.8, 0.9, 0.7]),
            url=url,
        )
        assert isinstance(high, PredictResponse)
        assert high.label == 1
        assert high.score == pytest.approx((0.8 + 0.9 + 0.7) / 3)

        low = call_classifier_predict_sync(
            PredictRequest(features=[0.1, 0.0, 0.2]),
            url=url,
        )
        assert low.label == 0
    finally:
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
