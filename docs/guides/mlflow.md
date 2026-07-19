# MLflow tracking

Opt a protobuf message into MLflow codegen with `(pgml.mlflow).enable = true`.
`py-gen-ml` emits:

- Pydantic models (with `Field(description=...)` from proto comments)
- For **`RUN_CONFIG`**: `start_*_run` (context manager), `log_*_params`, flatten helpers
- For **`METRIC_SET`**: `log_*` → `mlflow.log_metrics`
- When **`registered_model_name`** is set: Model Registry helpers
  (`*_signature`, `register_*`, `resolve_*_uri`)

Mark tracking messages with [message kinds](message_kinds.md) (`RUN_CONFIG` / `METRIC_SET`).
Kind does **not** replace the `(pgml.mlflow).enable` opt-in. Registry helpers can
live on a dedicated message that only sets `registered_model_name` + signature
message names (no kind required).

Shared field roles use `(pgml.tracking_field).slot` (`PARAM` / `METRIC` / `TAG`).
When unset: `RUN_CONFIG` fields default to **PARAM**, `METRIC_SET` fields to **METRIC**.
Nested message scalars flatten to dotted keys (`optimizer.learning_rate`).

## Install

```console
pip install 'py-gen-ml[mlflow]'
```

```console
uv add 'py-gen-ml[mlflow]'
```

```console
py-gen-ml path/to/schema.proto --generators=base,patch,sweep,cli_args,mlflow
```

## Annotate

```protobuf
message TrainingConfig {
  option (pgml.kind) = RUN_CONFIG;
  option (pgml.mlflow) = {
    enable: true;
    experiment_name: "sentiment";
    run_name_field: "run_name";
  };
  string run_name = 1 [(pgml.tracking_field) = { slot: TAG }];
  float learning_rate = 2;  // PARAM by default
  int32 epochs = 3;
}

message TrainMetrics {
  option (pgml.kind) = METRIC_SET;
  option (pgml.mlflow) = { enable: true };
  float accuracy = 1;
  float loss = 2;
}
```

| Option | Where | Meaning |
|--------|-------|---------|
| `(pgml.mlflow).enable` | message | Required to emit helpers. |
| `(pgml.mlflow).experiment_name` | message | Default experiment for `start_*_run`. |
| `(pgml.mlflow).run_name_field` | message | Field on RUN_CONFIG used as MLflow run name. |
| `(pgml.mlflow).registered_model_name` | message | Emit Model Registry helpers for this name. |
| `(pgml.mlflow).signature_input` | message | Protobuf message name → signature inputs. |
| `(pgml.mlflow).signature_output` | message | Protobuf message name → signature outputs. |
| `(pgml.tracking_field).slot` | field | `PARAM` / `METRIC` / `TAG` (optional; kind default applies). |
| `(pgml.tracking_field).name` | field | Optional log key override. |

## Generated usage

```python
from pgml_out.schema_mlflow import (
    TrainingConfig,
    TrainMetrics,
    start_training_config_run,
    log_train_metrics,
)

config = TrainingConfig(run_name="exp-1", learning_rate=1e-3, epochs=10)
with start_training_config_run(config):
    # ... train ...
    log_train_metrics(TrainMetrics(accuracy=0.91, loss=0.2), step=1)
```

On enter, `start_*_run` calls `mlflow.set_experiment` (when configured),
`mlflow.start_run`, logs PARAM fields (and `tag.*` params for TAG slots), and
`mlflow.set_tag` for TAG values.

## Model Registry

```protobuf
message PredictRequest { string prompt = 1; }
message Prediction { string generation = 1; }

message MyModel {
  option (pgml.mlflow) = {
    enable: true;
    registered_model_name: "my_model";
    signature_input: "PredictRequest";
    signature_output: "Prediction";
  };
}
```

```python
from pgml_out.schema_mlflow import (
    my_model_signature,
    register_my_model,
    resolve_my_model_uri,
)

# After logging an artifact in the active run:
mlflow.transformers.log_model(..., signature=my_model_signature())
register_my_model(f"runs:/{run.info.run_id}/model")

# At serve time:
uri = resolve_my_model_uri(alias="champion")  # models:/my_model@champion
```

Signature schemas cover scalar and repeated-scalar fields only; nested message
fields are skipped with a warning.

## See also

- [Weights & Biases tracking](wandb.md)
- [Message kinds](message_kinds.md)
- [Sweeps](sweep.md) — pairs well with Optuna + MLflow runs
- [Sentiment flywheel](../example_projects/sentiment_flywheel.md) — end-to-end train + MLflow
