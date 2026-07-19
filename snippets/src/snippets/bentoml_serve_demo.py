"""Demo BentoML service wired from generated py-gen-ml adapters.

Serve with::

    uv run bentoml serve snippets.bentoml_serve_demo:Service --port 3000
"""
from __future__ import annotations

from pgml_out.bentoml_demo_base import ClassifierServeConfig
from pgml_out.bentoml_demo_bentoml import (
    PredictRequest,
    PredictResponse,
    create_classifier_service,
)


def predict(request: PredictRequest) -> PredictResponse:
    score = sum(request.features) / max(len(request.features), 1)
    return PredictResponse(label=1 if score > 0.5 else 0, score=float(score))


Service = create_classifier_service(
    predict=predict,
    config=ClassifierServeConfig(workers=1, timeout_s=30.0),
)
