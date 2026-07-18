"""Runtime integration tests for generated LitServe server and client."""
from __future__ import annotations

import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

pytest.importorskip('litserve')
httpx = pytest.importorskip('httpx')

REPO = Path(__file__).resolve().parents[1]
SNIPPETS = REPO / 'docs' / 'snippets'
SNIPPETS_SRC = SNIPPETS / 'src'


def _predict(request):  # type: ignore[no-untyped-def]
    from pgml_out.litserve_demo_litserve import PredictResponse

    score = sum(request.features) / max(len(request.features), 1)
    return PredictResponse(label=1 if score > 0.5 else 0, score=float(score))


def test_generated_api_roundtrip(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(SNIPPETS_SRC))
    from pgml_out.litserve_demo_litserve import (
        PredictRequest,
        create_classifier_predict_api,
    )

    api = create_classifier_predict_api(predict=_predict)
    request = api.decode_request({'features': [0.8, 0.9, 0.7]})
    assert isinstance(request, PredictRequest)
    output = api.predict(request)
    body = api.encode_response(output)
    assert body['label'] == 1
    assert body['score'] == pytest.approx((0.8 + 0.9 + 0.7) / 3)


def test_generated_client_against_live_server(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(SNIPPETS_SRC))
    # Bind an ephemeral port first so we never collide with a stale process.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    env = {
        **os.environ,
        'PYTHONPATH': str(SNIPPETS_SRC),
        'LITSERVE_PORT': str(port),
    }
    proc = subprocess.Popen(
        [sys.executable, '-m', 'snippets.litserve_serve_demo'],
        cwd=str(SNIPPETS),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    url = f'http://127.0.0.1:{port}'
    try:
        deadline = time.time() + 45
        while time.time() < deadline:
            try:
                response = httpx.get(f'{url}/health', timeout=1.0)
                if response.status_code == 200:
                    break
            except Exception:
                time.sleep(0.5)
        else:
            out = proc.stdout.read().decode() if proc.stdout else ''
            raise AssertionError(f'server not ready:\n{out}')

        from pgml_out.litserve_demo_litserve import (
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
