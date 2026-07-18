# Message kinds

Mark a protobuf message with `(pgml.kind)` to declare its role in the ML
lifecycle. Kinds are shared vocabulary: many generators can select the same
roots (feature rows, predictions, run configs, …) without inventing parallel
schemas.

Tool-specific options stay separate. For example, LanceDB still requires
`(pgml.lancedb).enable = true` to emit code; setting `kind = FEATURE_ROW`
documents the contract and lets future generators find the same message.

**Rule of thumb:** `(pgml.kind)` = ML-contract role; `(pgml.<tool>).enable` =
emit that tool’s adapter. Keep kinds small; put library-specific knobs on tool
options, not on new parallel taxonomies.

## Values

| Kind | Meaning |
|------|---------|
| `MESSAGE_KIND_UNSPECIFIED` | Default when unset. No shared role. |
| `FEATURE_ROW` | A dataset / feature-store row (inputs, embeddings, metadata). |
| `LABEL` | Human or ground-truth annotation attached to a sample. |
| `PREDICTION` | Model output for a sample. |
| `FEEDBACK` | Downstream feedback (clicks, corrections, ratings). |
| `RUN_CONFIG` | Experiment / training run configuration (params for MLflow / W&B). |
| `METRIC_SET` | Named metrics logged for a run or evaluation. |

The [Sentiment flywheel](../example_projects/sentiment_flywheel.md) example uses
`FEATURE_ROW` for labeled training rows and serve requests, `PREDICTION` for
immutable model outputs, and `FEEDBACK` for human re-labels—each as a **separate
message** with its own tool opt-ins.

## Annotate a message

```protobuf
import "py_gen_ml/extensions.proto";

message EmbeddingSample {
    option (pgml.kind) = FEATURE_ROW;
    // Tool opt-in remains separate:
    option (pgml.lancedb) = {
        enable: true;
        table_name: "embedding_samples";
    };

    string id = 1;
    repeated float embedding = 2 [(pgml.lancedb_field).vector_dim = 8];
}
```

Nested messages usually omit `kind`. Generators that need nested types walk
fields from kind-tagged (or tool-enabled) roots via a shared message closure.

## How generators use kinds

Plugin helpers live in `py_gen_ml.plugin.message_kind`:

- `get_message_kind(message)` — read `(pgml.kind)`, or unspecified if absent
- `messages_with_kind(file, kind)` — roots with an exact kind
- `collect_message_closure(roots, file)` — same-file nested message set
- `ordered_messages(file, messages)` — topological emit order

Prefer filtering roots with `messages_with_kind` when the generator targets a
lifecycle role, and keep a tool-specific `(pgml.*).enable` when codegen imports
an optional third-party package. Serving generators should use
`py_gen_ml.plugin.service_rpc` for service/rpc roots; Pydantic-style class
bodies should go through `emit_pydantic_model` in `schema_emit`.

See also [LanceDB schemas](lancedb.md), [BentoML services](bentoml.md),
[LitServe services](litserve.md), [PydanticAI synthesis](pydantic_ai.md),
[Argilla](argilla.md), [MLflow tracking](mlflow.md),
[Weights & Biases](wandb.md), [bridges](bridges.md), and the
[Sentiment flywheel](../example_projects/sentiment_flywheel.md) example.
