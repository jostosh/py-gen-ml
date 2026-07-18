# Weights & Biases tracking

Opt a protobuf message into W&B codegen with `(pgml.wandb).enable = true`.
`py-gen-ml` emits:

- Pydantic models (with `Field(description=...)` from proto comments)
- For **`RUN_CONFIG`**: `init_*_run` → `wandb.init(config=..., tags=...)`
- For **`METRIC_SET`**: `log_*` → `wandb.log`

Mark messages with [message kinds](message_kinds.md) (`RUN_CONFIG` / `METRIC_SET`).
Kind does **not** replace the `(pgml.wandb).enable` opt-in.

Shared field roles use `(pgml.tracking_field).slot` (`PARAM` / `METRIC` / `TAG`),
same rules as [MLflow](mlflow.md): kind defaults + optional overrides; nested
scalars flatten to dotted keys.

## Install

```console
pip install 'py-gen-ml[wandb]'
```

```console
uv add 'py-gen-ml[wandb]'
```

```console
py-gen-ml path/to/schema.proto --generators=base,patch,sweep,cli_args,wandb
```

## Annotate

```protobuf
message TrainingConfig {
  option (pgml.kind) = RUN_CONFIG;
  option (pgml.wandb) = {
    enable: true;
    project: "sentiment";
    run_name_field: "run_name";
  };
  string run_name = 1 [(pgml.tracking_field) = { slot: TAG }];
  float learning_rate = 2;
  int32 epochs = 3;
}

message TrainMetrics {
  option (pgml.kind) = METRIC_SET;
  option (pgml.wandb) = { enable: true };
  float accuracy = 1;
  float loss = 2;
}
```

| Option | Where | Meaning |
|--------|-------|---------|
| `(pgml.wandb).enable` | message | Required to emit helpers. |
| `(pgml.wandb).project` | message | Default W&B project for `init_*_run`. |
| `(pgml.wandb).run_name_field` | message | Field on RUN_CONFIG used as run name. |
| `(pgml.tracking_field).*` | field | Same shared slots as MLflow. |

## Generated usage

```python
from pgml_out.schema_wandb import (
    TrainingConfig,
    TrainMetrics,
    init_training_config_run,
    log_train_metrics,
)

config = TrainingConfig(run_name="exp-1", learning_rate=1e-3, epochs=10)
run = init_training_config_run(config)
try:
    # ... train ...
    log_train_metrics(TrainMetrics(accuracy=0.91, loss=0.2), step=1)
finally:
    run.finish()
```

`init_*_run` passes PARAM fields as `config=` and TAG values as W&B `tags=`.

## See also

- [MLflow tracking](mlflow.md)
- [Message kinds](message_kinds.md)
- [Sweeps](sweep.md)
- [Sentiment flywheel](../example_projects/sentiment_flywheel.md) — end-to-end train + MLflow (W&B generators work the same way)
