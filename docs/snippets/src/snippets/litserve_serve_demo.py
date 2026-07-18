"""Wire Predict into the generated LitServe factory and run the server.

From ``docs/snippets`` (after codegen)::

    uv sync --extra litserve
    uv run python -m snippets.litserve_serve_demo

Optional ``LITSERVE_PORT`` (default ``8000``).
"""
from __future__ import annotations

import os

from pgml_out.litserve_demo_base import ClassifierServeConfig
from pgml_out.litserve_demo_litserve import (
    PredictRequest,
    PredictResponse,
    create_classifier_server,
)


def predict(request: PredictRequest) -> PredictResponse:
    score = sum(request.features) / max(len(request.features), 1)
    return PredictResponse(label=1 if score > 0.5 else 0, score=float(score))


if __name__ == '__main__':
    port = int(os.environ.get('LITSERVE_PORT', '8000'))
    server = create_classifier_server(
        predict=predict,
        config=ClassifierServeConfig(
            accelerator='cpu',
            workers_per_device=1,
            timeout_s=30.0,
        ),
    )
    server.run(host='127.0.0.1', port=port, generate_client_file=False)
