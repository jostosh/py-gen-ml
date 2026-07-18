# PydanticAI synthesis

Opt a protobuf message into PydanticAI codegen with `(pgml.pydantic_ai).enable = true`.
`py-gen-ml` then emits:

- **Full** Pydantic models (strict synthesis outputs)
- **Partial** models (every field `Optional[...] = None` for few-shot / incomplete rows)
- An agent factory using PydanticAI **`NativeOutput`** (native structured outputs /
  JSON Schema response format when the provider supports it)
- A single `synthesize_*` / `synthesize_*_sync` entrypoint

Mark the same message with [message kinds](message_kinds.md) (usually
`FEATURE_ROW`) so LanceDB, Argilla, and serving generators can share the contract.
Kind does **not** replace the `(pgml.pydantic_ai).enable` opt-in.

## Why NativeOutput

By default PydanticAI can expose structured results as tools. For synthesis we
want the provider’s **native structured-output** path whenever possible, so the
JSON Schema derived from your Pydantic model is what the model must satisfy.
Generated agents wrap the output type in `NativeOutput(...)` (passing the
protobuf **message** comment as `description=` when present) and do **not**
register extra tools in v1 (some providers cannot mix tools + native schema).

If your provider lacks native structured outputs, PydanticAI falls back according
to its own rules—prefer models that advertise JSON Schema / response_format
support for best results.

## Proto field comments → JSON Schema (do this well)

Codegen turns protobuf **leading comments** into
`pydantic.Field(description=...)`. Those descriptions appear in
`model_json_schema()` and are forwarded to the LLM under native structured
outputs.

```protobuf
// Full movie-review text in the style of IMDB user reviews.
string text = 3;
```

becomes roughly:

```python
text: str = Field(
    description="Full movie-review text in the style of IMDB user reviews.",
)
```

Vague or missing comments produce weak schemas and weaker synthetic data.
Treat field comments as part of the product contract for synthesis—especially
for labels (`"negative" or "positive"`), free text style, and provenance fields.

## Install the extra

```console
pip install 'py-gen-ml[pydantic-ai]'
```

Or with uv:

```console
uv add 'py-gen-ml[pydantic-ai]'
```

Enable the generator (it is **off by default**):

```console
py-gen-ml path/to/schema.proto --generators=base,patch,sweep,cli_args,pydantic_ai
```

Combine with other opt-ins when the same message is also an Argilla / LanceDB
row, e.g. `--generators=base,pydantic_ai,argilla,lancedb`.

## Annotate a contract

Minimal options:

| Option | Where | Meaning |
|--------|-------|---------|
| `(pgml.pydantic_ai).enable` | message | Required to emit synthesis helpers. |
| `(pgml.pydantic_ai).agent_name` | message | Optional `NativeOutput` name (default: message name). |
| `(pgml.pydantic_ai).response_message` | message | If the enabled message is a seed wrapper, name of the output message type. |

Example (instruction–response style):

```protobuf
--8<-- "docs/snippets/proto/flywheel_demo.proto"
```

For a full **sentiment classification** flywheel (IMDB seeds → synthesize →
Argilla → train), see the [Sentiment flywheel](../example_projects/sentiment_flywheel.md)
example project and `sentiment_demo.proto`.

## Generated module

For a message `ReviewExample`, enabling the generator writes
`*_pydantic_ai.py` containing:

- `ReviewExample` — full model
- `ReviewExamplePartial` — all-optional twin for `examples` / `incomplete`
- `create_review_example_agent(model, *, system_prompt, output_type)`
- `synthesize_review_example(...)` / `synthesize_review_example_sync(...)`
- Internal helpers: gap `create_model` for Path B completion

Do not edit the generated module. Inject `model` and prompts from your
application code.

## Single `synthesize_*` API

```python
async def synthesize_review_example(
    *,
    model: str | Model,
    system_prompt: str,
    count: int = 1,
    examples: Sequence[ReviewExamplePartial] | None = None,
    incomplete: Sequence[ReviewExamplePartial] | None = None,
    diversify_rounds: int = 0,
) -> list[ReviewExample]:
```

Return values are always **full** models.

### Path A — generate full instances (`incomplete` is omitted)

| Intent | How |
|--------|-----|
| From scratch | `count=n` |
| Few-shot | pass `examples=[Partial(...), ...]` (`None` allowed on unused fields) |
| Diversify | `diversify_rounds=k`: after the first batch, prior full outputs are fed back as examples for subsequent rounds |

Rough total rows for Path A with diversify:
`count * (diversify_rounds + 1)` (first batch + one batch per diversify round).

### Path B — complete missing fields (`incomplete` is set)

Treated as a **separate** code path:

1. For each partial, fields that are `None` are collected.
2. `pydantic.create_model` builds a **gap** schema with only those fields (descriptions preserved).
3. The agent runs with `NativeOutput(Gap)`.
4. Gap values are merged onto the partial → full model.

When `incomplete` is non-empty, `count` is ignored. Combining `incomplete` with
`diversify_rounds > 0` raises `ValueError` (chain calls yourself if you need both).

### Choosing a path

| Situation | API |
|-----------|-----|
| Expand a labeled seed set | Path A + `examples` (+ optional `diversify_rounds`) |
| Label unlabeled text | Path B with `sentiment=None` (or similar) |
| Fill missing metadata only | Path B with only those fields `None` |

## Examples

From scratch:

```python
from pgml_out.flywheel_demo_pydantic_ai import synthesize_review_example_sync

rows = synthesize_review_example_sync(
    model="openai:gpt-4o",
    system_prompt="You write concise instruction–response pairs.",
    count=2,
)
```

Few-shot + diversify (typical for expanding a seed set):

```python
from pgml_out.flywheel_demo_pydantic_ai import (
    ReviewExamplePartial,
    synthesize_review_example_sync,
)

seeds = [
    ReviewExamplePartial(
        id="s1",
        instruction="Explain gravity to a child.",
        generation="Gravity is the pull that keeps us on the ground.",
        quality="good",
    ),
]
rows = synthesize_review_example_sync(
    model="openai:gpt-4o",
    system_prompt="Write new diverse instruction–response pairs.",
    count=4,
    examples=seeds,
    diversify_rounds=1,
)
```

Complete gaps only:

```python
filled = synthesize_review_example_sync(
    model="openai:gpt-4o",
    system_prompt="Fill missing fields only; keep provided values.",
    incomplete=[
        ReviewExamplePartial(
            id="1",
            instruction="Explain gravity",
            generation=None,
            quality=None,
        ),
    ],
)
```

Pass any PydanticAI-compatible `model` string (e.g. `openai:gpt-4o`,
`anthropic:claude-sonnet-4-0`) or a `Model` instance.

## Testing JSON Schema locally

```python
from pgml_out.flywheel_demo_pydantic_ai import ReviewExample

print(ReviewExample.model_json_schema()["properties"]["instruction"]["description"])
```

You should see the protobuf comment text. The sentiment demo asserts this for
`text` / `sentiment` in `tests/test_sentiment_flywheel_demo.py`.

## Limitations (v1)

- No tools on the synthesis agent (NativeOutput-only).
- No `incomplete` + `diversify_rounds > 0` in one call.
- Quality depends heavily on field comments and your system prompt.
- Provider support for native structured outputs varies—validate schemas early.

## See also

- [Sentiment flywheel](../example_projects/sentiment_flywheel.md) — IMDB → synthesize → Argilla → train
- [Argilla datasets](argilla.md)
- [Cross-tool bridges](bridges.md)
- [Message kinds](message_kinds.md)
