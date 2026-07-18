<p align="center">
   <a href="https://jostosh.github.io/py-gen-ml"><img src="docs/assets/images/logo.svg" alt="py-gen-ml" width="200"></a>
</p>
<p align="center">
    <em>Typed ML contracts from Protocol Buffers—across the whole lifecycle.</em>
</p>
<p align="center">

---

**Documentation**: <a href="https://jostosh.github.io/py-gen-ml" target="_blank">https://jostosh.github.io/py-gen-ml</a>

---

# Project introduction

`py-gen-ml` turns **your** protobuf schemas into typed adapters for the ML
lifecycle: feature rows, labels, predictions, feedback, run configs, and metrics.
A deterministic `protoc` plugin emits Pydantic models and optional tool adapters
(LanceDB, Argilla, PydanticAI, LitServe, BentoML, MLflow, W&B, …). One schema is
the source of truth; generators and small runtime bridges hang off the same
messages.

Experiment **configuration** (base / patch / sweep / CLI / YAML) is how you
drive training runs from the same schemas—load YAML, overlay patches, sample
sweeps, and override fields from the command line.

## What this is (and isn't)

**What this is:**

- You author `.proto` files that describe ML **contracts** (rows, predictions,
  feedback, run configs, metrics—and training hyperparameters).
- You mark roles with `(pgml.kind)` and opt into tools with `(pgml.<tool>).enable`.
- You run `py-gen-ml` / `protoc-gen-py-ml` and get typed models plus adapters.
- You keep training loops, servers, and HITL workflows in your code; generated
  code owns schemas and glue.

**What this isn't:**

- Not an LLM that invents schemas or training code from a prompt.
- Not “AI generates your protobufs.” Direction is **protobuf → typed ML tooling**.
- Not a replacement for Argilla, LitServe, MLflow, etc.—only the contract layer
  and thin helpers around them.

## How it fits together

```text
You write .proto + (pgml.kind) + tool opt-ins
                 │
                 ▼
           py-gen-ml (protoc plugin)
                 │
     ┌───────────┼──────────────────────┐
     ▼           ▼                      ▼
  Base/patch   Opt-in adapters      JSON Schema
  sweep/CLI    (LanceDB, Argilla,   (YAML IDE)
               PydanticAI, LitServe,
               BentoML, MLflow, W&B)
                 │
                 ▼
        Your training / serving / HITL code
                 │
                 ▼
           py_gen_ml.bridges
```

| Idea | Role |
|------|------|
| `(pgml.kind)` | Shared ML-contract role (`FEATURE_ROW`, `PREDICTION`, `FEEDBACK`, `RUN_CONFIG`, …) |
| `(pgml.<tool>).enable` | Emit that tool’s adapter |
| Base / patch / sweep / CLI | Experiment configs: YAML, patches, sweeps, and CLI overrides |
| Bridges | Runtime helpers that compose **already generated** adapters |

## Flagship path: sentiment flywheel

The [Sentiment flywheel](https://jostosh.github.io/py-gen-ml/example_projects/sentiment_flywheel/)
shows one proto driving offline synthesize → HITL → train → track and online
serve → prediction → feedback → store. Prefer
[CIFAR-10](https://jostosh.github.io/py-gen-ml/example_projects/cifar10/) when
you care mainly about config → train → sweep.

## Experiment configuration

The same plugin emits base / patch / sweep / CLI / factories / JSON Schema for
experiment configs. Load YAML, overlay patches, sample Optuna sweeps, and override
nested fields from the command line—without hand-maintaining parallel types.

## Getting started

```console
pip install py-gen-ml
```

Optional extras match the tools you enable (`lancedb`, `argilla`, `pydantic-ai`,
`litserve`, `bentoml`, `mlflow`, `wandb`, `bridges`, …).

- New to the library → [Quickstart](https://jostosh.github.io/py-gen-ml/quickstart/)
- Lifecycle story → [Sentiment flywheel](https://jostosh.github.io/py-gen-ml/example_projects/sentiment_flywheel/)
- Schema roles → [Message kinds](https://jostosh.github.io/py-gen-ml/guides/message_kinds/)

## When to use it

- You want one schema for **feature / prediction / feedback / run / metric**
  messages across tools
- You run HITL, synthesis, serving, or tracking and hate duplicating types
- You also need robust **experiment config** (patch, sweep, CLI, JSON Schema)

## Where to go from here

- [Documentation home](https://jostosh.github.io/py-gen-ml/)
- [Message kinds](https://jostosh.github.io/py-gen-ml/guides/message_kinds/)
- [Sentiment flywheel](https://jostosh.github.io/py-gen-ml/example_projects/sentiment_flywheel/)
- [Quickstart (config)](https://jostosh.github.io/py-gen-ml/quickstart/)
- [CIFAR-10](https://jostosh.github.io/py-gen-ml/example_projects/cifar10/)
