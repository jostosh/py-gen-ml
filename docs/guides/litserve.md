# LitServe services

Opt a protobuf **service** into LitServe codegen with `(pgml.litserve).enable = true`.
`py-gen-ml` then emits Pydantic request/response models, per-RPC `LitAPI` factories,
a `create_*_server` that wraps them in `litserve.LitServer`, typed sync/async
client helpers, and optional serve-config kwargs.

Mark request/response/config messages with [message kinds](message_kinds.md)
(`FEATURE_ROW`, `PREDICTION`, `RUN_CONFIG`) so other generators can share the
same contracts. Kind does **not** replace the LitServe service opt-in.

## Install the extra

```console
pip install 'py-gen-ml[litserve]'
```

Or with uv:

```console
uv add 'py-gen-ml[litserve]'
```

Enable the generator when you run codegen (it is **off by default**):

```console
py-gen-ml path/to/schema.proto --generators=base,patch,sweep,cli_args,litserve
```

## Annotate a contract

```protobuf
--8<-- "docs/snippets/proto/litserve_demo.proto"
```

| Option | Where | Meaning |
|--------|-------|---------|
| `(pgml.litserve).enable` | `service` | Required to emit LitServe adapters for this service. |
| `(pgml.litserve).name` | `service` | Optional LitAPI class-name prefix (default: service name). |
| `(pgml.litserve_method).api_path` | `rpc` | HTTP path (default: `/{method_snake}`). |
| `(pgml.litserve_config).enable` | message | Link a config message to a service. |
| `(pgml.litserve_config).service` | message | Proto service name this config configures. |

Config field conventions used by the kwargs mapper:

- `accelerator` → `LitServer(accelerator=...)`
- `devices` → `LitServer(devices=...)`
- `workers_per_device` → `LitServer(workers_per_device=...)`
- `timeout_s` → `LitServer(timeout=...)`
- `url` → default URL for generated client helpers (not passed to `LitServer`)

Unary RPCs only; streaming methods raise at codegen time.

LitServe mounts **one endpoint per `LitAPI`**. Multi-RPC services get one API
class per method (distinct `api_path`) and a single `LitServer` holding all of them.

## Generated module

For `litserve_demo.proto`, enabling the generator writes `litserve_demo_litserve.py`
containing:

- `PredictRequest` / `PredictResponse` as `pydantic.BaseModel`
- `classifier_server_kwargs(config)` mapping serve settings
- `create_classifier_predict_api(predict=..., setup=...)` returning a `LitAPI` instance
- `create_classifier_server(predict=..., config=..., **server_kwargs)` returning `LitServer`
- `call_classifier_predict_sync` / `call_classifier_predict_async` (via `httpx`)

## Serve

### 1. Write a serve module

Wire your model logic into the generated factory:

```python linenums="1"
--8<-- "docs/snippets/src/snippets/litserve_serve_demo.py"
```

Keep handlers in *your* code. Do not edit the generated `*_litserve.py` module.

### 2. Start the server

From the docs snippets project (after codegen), with the `litserve` extra
installed:

```console
cd docs/snippets
uv sync --extra litserve
uv run python -m snippets.litserve_serve_demo
```

When the process is ready:

```console
curl -s http://127.0.0.1:8000/predict \
  -H 'content-type: application/json' \
  -d '{"features": [0.8, 0.9, 0.7]}'
```

### 3. Call with the generated client

```python
from pgml_out.litserve_demo_litserve import PredictRequest, call_classifier_predict_sync

result = call_classifier_predict_sync(
    PredictRequest(features=[0.8, 0.9, 0.7]),
    url="http://127.0.0.1:8000",
)
print(result.label, result.score)
```

Pass an existing `httpx.Client` / `AsyncClient` via `client=` when you want to
reuse connections.
