# Argilla datasets

Opt a protobuf message into Argilla codegen with `(pgml.argilla).enable = true`.
`py-gen-ml` emits:

- Pydantic models with `Field(description=...)` from proto comments
- `build_*_settings()` for Argilla `Settings` (UI fields + questions)
- `to_*_record` / `from_*_record` mappers
- Optional alias helpers when `(pgml.mapper_config).enable` is set

Use [message kinds](message_kinds.md) (`FEATURE_ROW`, `LABEL`, `FEEDBACK`, …) to
document the contract. Kind does **not** replace the Argilla opt-in.

## Field vs Question vs Metadata

Every field on an Argilla-enabled message **must** set
`(pgml.argilla_field).slot`. Missing slots fail at codegen.

| Slot | Argilla artifact | Record mapping |
|------|------------------|----------------|
| `FIELD` | `TextField` / `ChatField` / `ImageField` / … | `record.fields[name]` |
| `QUESTION` | `LabelQuestion` / `MultiLabelQuestion` / `RatingQuestion` / `TextQuestion` / … | suggestions / responses |
| `METADATA` | *(none in Settings)* | `record.metadata[name]` |

Typical pattern for classification HITL:

- **FIELD** — the text (or multimodal content) annotators read
- **QUESTION** — the label they assign (`positive` / `negative`, …)
- **METADATA** — ids, provenance (`imdb` vs `synthetic`), timestamps

```protobuf
string id = 1 [(pgml.argilla_field) = { slot: METADATA }];
string text = 2 [(pgml.argilla_field) = {
  slot: FIELD; field_type: "text"; required: true
}];
string sentiment = 3 [(pgml.argilla_field) = {
  slot: QUESTION; question_type: "label";
  labels: ["negative", "positive"]; required: true
}];
```

### `ArgillaField` knobs

| Field | Applies to | Meaning |
|-------|------------|---------|
| `slot` | all | `FIELD` / `QUESTION` / `METADATA` (required) |
| `name` | all | Optional UI/API name (default: proto field name) |
| `field_type` | FIELD | `text` (default), `chat`, `image`, … |
| `question_type` | QUESTION | `label`, `multi_label`, `rating`, `text`, … |
| `labels` | label questions | Allowed class names |
| `required` | FIELD / QUESTION | Passed through to Argilla |

## Install the extra

```console
pip install 'py-gen-ml[argilla]'
```

```console
uv add 'py-gen-ml[argilla]'
```

The Argilla extra also pins `datasets>=3` so imports work with modern `pyarrow`
(versions that removed `PyExtensionType`, commonly pulled in with LanceDB).

```console
py-gen-ml path/to/schema.proto --generators=base,patch,sweep,cli_args,argilla
```

## Annotate

Instruction–response style demo:

```protobuf
--8<-- "docs/snippets/proto/flywheel_demo.proto"
```

Sentiment / IMDB flywheel contract:

```protobuf
--8<-- "docs/snippets/proto/sentiment_demo.proto"
```

| Option | Where | Meaning |
|--------|-------|---------|
| `(pgml.argilla).enable` | message | Required to emit Argilla helpers. |
| `(pgml.argilla).dataset_name` | message | Hint returned by `*_dataset_name()` (default: snake_case message name). |
| `(pgml.argilla_field).*` | field | Slot + type/labels (see above). |
| `(pgml.mapper_config).enable` | message | Emit `*_ALIASES` / `*_to_row_dict` / `*_from_row_dict`. |

## Generated module

For `SentimentExample`, enabling the generator writes `*_argilla.py` with:

- `SentimentExample` Pydantic model
- `sentiment_example_dataset_name()` — e.g. `"imdb_sentiment"`
- `build_sentiment_example_settings(*, client=None)`
- `to_sentiment_example_record` / `from_sentiment_example_record`
- Optional mapper aliases when configured

### Offline Settings construction

Argilla 2.x field/question constructors may try to resolve a default client.
Pass an explicit client (or a test double) to avoid requiring API credentials
at Settings build time:

```python
from unittest.mock import MagicMock
from pgml_out.sentiment_demo_argilla import build_sentiment_example_settings

settings = build_sentiment_example_settings(client=MagicMock())
assert {f.name for f in settings.fields} == {"text"}
assert {q.name for q in settings.questions} == {"sentiment"}
```

### Records and suggestions

`to_*_record` places FIELD values in `record.fields`, METADATA in
`record.metadata`, and non-null QUESTION values as `Suggestion`s (model or
weak labels for annotators to confirm). After humans respond in the Argilla UI,
map responses back with `from_*_record` (best-effort for suggestions) or your
own response parsing before training.

Suggested flow for classification:

1. Synthesize or load seeds → full models
2. `to_*_record` → log to Argilla (labels as suggestions)
3. Humans submit responses
4. Export / fetch records → prefer **responses** over suggestions for train labels
5. Validate back into the same Pydantic / Lance models

## Pushing to a live Argilla server

```python
import argilla as rg
from pgml_out.sentiment_demo_argilla import (
    build_sentiment_example_settings,
    sentiment_example_dataset_name,
    to_sentiment_example_record,
)

client = rg.Argilla()  # uses ARGILLA_API_URL / ARGILLA_API_KEY
settings = build_sentiment_example_settings(client=client)
dataset = rg.Dataset(
    name=sentiment_example_dataset_name(),
    settings=settings,
    client=client,
)
dataset.create()
dataset.records.log([to_sentiment_example_record(row) for row in rows])
```

Or via the bridge:

```python
from py_gen_ml.bridges import synthetic_rows_to_argilla_records

records = synthetic_rows_to_argilla_records(rows, to_record=to_sentiment_example_record)
dataset.records.log(records)
```

Keep dataset create/log in *your* module. Do not edit the generated `*_argilla.py`.

## HITL tips

- Put free-text the annotator must read in `FIELD`, never only in metadata.
- Keep class names in `labels:` stable—changing them mid-project breaks the UI.
- Use `METADATA` for provenance (`source=imdb|synthetic`) so you can filter
  training sets later.
- For end-to-end sentiment + training wiring, see the
  [Sentiment flywheel](../example_projects/sentiment_flywheel.md) example.

## See also

- [Sentiment flywheel](../example_projects/sentiment_flywheel.md)
- [PydanticAI synthesis](pydantic_ai.md)
- [Cross-tool bridges](bridges.md)
- [Message kinds](message_kinds.md)
