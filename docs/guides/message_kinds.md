# Message kinds

Mark a protobuf message with `(pgml.kind)` to declare its role in the ML
lifecycle. Kinds are shared vocabulary: many generators can select the same
roots (feature rows, predictions, run configs, …) without inventing parallel
schemas.

Tool-specific options stay separate. For example, LanceDB still requires
`(pgml.lancedb).enable = true` to emit code; setting `kind = FEATURE_ROW`
documents the contract and lets future generators find the same message.

## Values

| Kind | Meaning |
|------|---------|
| `MESSAGE_KIND_UNSPECIFIED` | Default when unset. No shared role. |
| `FEATURE_ROW` | A dataset / feature-store row (inputs, embeddings, metadata). |
| `LABEL` | Human or ground-truth annotation attached to a sample. |
| `PREDICTION` | Model output for a sample. |
| `FEEDBACK` | Downstream feedback (clicks, corrections, ratings). |
| `RUN_CONFIG` | Experiment / training run configuration. |
| `METRIC_SET` | Named metrics logged for a run or evaluation. |

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
an optional third-party package.

See also [LanceDB schemas](lancedb.md) for a `FEATURE_ROW` example.
