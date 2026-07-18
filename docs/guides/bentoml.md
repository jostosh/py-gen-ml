# BentoML services

Opt a protobuf **service** into BentoML codegen with `(pgml.bentoml).enable = true`.
`py-gen-ml` then emits Pydantic request/response models, a `create_*_service`
factory, typed sync/async client helpers, and optional serve-config kwargs.

Mark request/response/config messages with [message kinds](message_kinds.md)
(`FEATURE_ROW`, `PREDICTION`, `RUN_CONFIG`) so other generators can share the
same contracts. Kind does **not** replace the BentoML service opt-in.

## Install the extra

```console
pip install 'py-gen-ml[bentoml]'
```

Or with uv:

```console
uv add 'py-gen-ml[bentoml]'
```

Enable the generator when you run codegen (it is **off by default**):

```console
py-gen-ml path/to/schema.proto --generators=base,patch,sweep,cli_args,bentoml
```

## Annotate a contract

```protobuf
--8<-- "docs/snippets/proto/bentoml_demo.proto"
```

| Option | Where | Meaning |
|--------|-------|---------|
| `(pgml.bentoml).enable` | `service` | Required to emit BentoML adapters for this service. |
| `(pgml.bentoml).name` | `service` | Optional Python class name (default: service name). |
| `(pgml.bentoml_method).route` | `rpc` | HTTP route (default: `/{method_snake}`). |
| `(pgml.bentoml_method).name` | `rpc` | Client API name (default: method snake_case). |
| `(pgml.bentoml_method).batchable` | `rpc` | When true, mark the API batchable. |
| `(pgml.bentoml_config).enable` | message | Link a config message to a service. |
| `(pgml.bentoml_config).service` | message | Proto service name this config configures. |

Config field conventions used by the kwargs mapper:

- `workers` → `@bentoml.service(workers=...)`
- `timeout_s` → `@bentoml.service(traffic={"timeout": ...})`
- `url` → default URL for generated client helpers (not passed to `@bentoml.service`)

Unary RPCs only; streaming methods raise at codegen time.

## Generated module

For `bentoml_demo.proto`, enabling the generator writes `bentoml_demo_bentoml.py`
containing:

- `PredictRequest` / `PredictResponse` as `pydantic.BaseModel`
- `classifier_service_kwargs(config)` mapping serve settings
- `create_classifier_service(predict=..., config=...)` returning a `@bentoml.service` class
- `call_classifier_predict_sync` / `call_classifier_predict_async`

## Serve with `bentoml serve`

HTTP request bodies use flat request-model fields (e.g. `{"features": [...]}`).
The generated API method accepts BentoML's unpacked kwargs and rebuilds the
request model before calling your handler.

### 1. Write a service module

Wire your model logic into the generated factory and assign the result to a
module-level name (BentoML looks this up as `module:Service`):

```python linenums="1"
--8<-- "docs/snippets/src/snippets/bentoml_serve_demo.py"
```

Keep handlers in *your* code. Do not edit the generated `*_bentoml.py` module.

### 2. Start the server

From the docs snippets project (after codegen), with the `bentoml` extra
installed:

```console
cd docs/snippets
uv sync --extra bentoml
uv run bentoml serve snippets.bentoml_serve_demo:Service --port 3000
```

In your own project the pattern is the same: put the service module on
`PYTHONPATH` (or install the package), then pass `package.module:Service`.

Useful flags:

| Flag | Meaning |
|------|---------|
| `--port 3000` | Listen port (default is often `3000`). |
| `--reload` | Restart on code changes while developing. |
| `--host 0.0.0.0` | Bind all interfaces (needed in containers). |

When the process is ready, check health and hit the RPC route:

```console
curl -s http://127.0.0.1:3000/readyz
curl -s http://127.0.0.1:3000/predict \
  -H 'content-type: application/json' \
  -d '{"features": [0.8, 0.9, 0.7]}'
```

You should get JSON like `{"label": 1, "score": 0.8}`. OpenAPI / interactive
docs are also served by BentoML on the same host (see the BentoML UI link printed
at startup).

### 3. Call with the generated client

While the server is running:

```python
from pgml_out.bentoml_demo_bentoml import PredictRequest, call_classifier_predict_sync

response = call_classifier_predict_sync(
    PredictRequest(features=[0.8, 0.9, 0.7]),
    url="http://127.0.0.1:3000",
)
print(response.label, response.score)
```

If you omit `url`, the helper falls back to `ClassifierServeConfig().url`
(default `http://localhost:3000` in the demo proto). Pass an existing
`bentoml.SyncHTTPClient` / `AsyncHTTPClient` via `client=` when you want to reuse
a connection.

```python
import bentoml
from pgml_out.bentoml_demo_bentoml import PredictRequest, call_classifier_predict_sync

with bentoml.SyncHTTPClient("http://127.0.0.1:3000") as client:
    response = call_classifier_predict_sync(
        PredictRequest(features=[0.1, 0.2]),
        client=client,
    )
```

Use `call_classifier_predict_async` the same way with
`bentoml.AsyncHTTPClient` in async code.
