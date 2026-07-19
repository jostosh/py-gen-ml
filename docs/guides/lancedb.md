# LanceDB schemas

Opt a protobuf message into LanceDB codegen with `(pgml.lancedb).enable = true`.
`py-gen-ml` then emits `lancedb.pydantic.LanceModel` classes for that message
and every nested message type reachable from it, plus small helpers to create
a table with the generated schema.

Feature-row messages should also set `(pgml.kind) = FEATURE_ROW` so other
generators can discover the same contract. See [Message kinds](message_kinds.md).
Kind does **not** replace the LanceDB opt-in.

## Install the extra

The generator itself ships with `py-gen-ml`. Generated modules import `lancedb`,
so install the optional extra in projects that use them:

```console
pip install 'py-gen-ml[lancedb]'
```

Or with uv:

```console
uv add 'py-gen-ml[lancedb]'
```

The torch DataLoader example below also needs PyTorch (`pip install torch`).

Enable the generator when you run codegen (it is **off by default**):

```console
py-gen-ml path/to/schema.proto --generators=base,patch,sweep,cli_args,lancedb
```

## Concepts

### Message opt-in

Annotate the **root** row type with `(pgml.lancedb)` (and preferably
`(pgml.kind) = FEATURE_ROW`):

| Option | Meaning |
|--------|---------|
| `enable` | Required. When `true`, emit LanceModels for this message and its nested types. |
| `table_name` | Optional default table name. Falls back to the message name in snake_case. |

Nested messages do **not** need their own `(pgml.lancedb)` option. Walking field
types from each enabled root builds the set of models to emit.

### Vector columns

LanceDB fixed-size vectors use `lancedb.pydantic.Vector(dim)`. Mark a field with
`(pgml.lancedb_field).vector_dim = N` (typically on `repeated float`):

```protobuf
repeated float embedding = 2 [(pgml.lancedb_field).vector_dim = 8];
```

That field is generated as `embedding: Vector(8)` instead of `List[float]`.

### Merge keys

Mark join columns for LanceDB ``merge_insert`` with
``(pgml.lancedb_field).merge_key = true``:

```protobuf
string id = 1 [(pgml.lancedb_field) = { merge_key: true }];
```

Codegen emits ``*_merge_on() -> list[str]`` listing those fields. Pass that to
``py_gen_ml.bridges.merge_rows(table, rows, on=...)`` for upserts. When no field
is marked, use ``py_gen_ml.bridges.append_rows(table, rows)`` instead.

### What gets generated

For a proto `lancedb_demo.proto`, enabling the generator writes
`lancedb_demo_lancedb.py` containing:

- One `LanceModel` subclass per message in the nested closure
- `*_table_name()` returning the configured (or default) table name
- `*_merge_on()` returning fields marked ``merge_key``
- `create_*_table(db, ...)` calling `db.create_table(..., schema=<RootModel>, exist_ok=True)`

Enums are stored as `str`. Scalar / list / nested-message fields follow the usual
Python mapping that LanceDB converts to Arrow types.

Torch Dataset wrappers are **not** generated. LanceDB tables already implement
PyTorch's Dataset contract, so you pass the table to
`torch.utils.data.DataLoader` directly (see
[LanceDB's PyTorch integration](https://docs.lancedb.com/training/torch)).

## Annotate a schema

```protobuf
--8<-- "docs/snippets/proto/lancedb_demo.proto"
```

## Generated models

```python { .generated-code }
--8<-- "docs/snippets/src/pgml_out/lancedb_demo_lancedb.py"
```

## End-to-end: insert rows and load with PyTorch

LanceDB's [`Table`](https://docs.lancedb.com/training/torch) can be handed to
`torch.utils.data.DataLoader` without a custom `Dataset` class. Batches arrive
as Arrow tables; use a `collate_fn` to turn them into tensors.

For purely numeric scalar columns, LanceDB's
`lancedb.util.tbl_to_tensor` is enough. Our demo schema also has strings,
fixed-size vectors, and a nested struct, so the snippet uses a small collate
helper that keeps those columns usable in training.

```python linenums="1"
--8<-- "docs/snippets/src/snippets/lancedb_torch_demo.py"
```

Run it from the docs snippets project (after codegen):

```console
cd docs/snippets
uv sync --extra lancedb
uv run python -m snippets.lancedb_torch_demo
```

You should see three batches of two row ids each, with embedding tensors of
shape `(2, 8)`.

### Going further

LanceDB's [Permutation API](https://docs.lancedb.com/training/torch) is useful
when you want column projection, splits, or shuffle without materializing a
copy. For example, selecting only the embedding column reduces I/O before the
DataLoader:

```python
from lancedb.permutation import Permutation

permutation = Permutation.identity(table).select_columns(["embedding"])
```

See the LanceDB docs for `tbl_to_tensor`, `torch_col` format, and multi-worker
loaders (`num_workers`, `multiprocessing_context="forkserver"`).

## Overview

This feature bridges **your protobuf row schema** to **LanceDB table schemas**
without hand-maintaining parallel Pydantic models:

1. You declare the row shape (and nested structs / vector dims) in `.proto`.
2. `py-gen-ml --generators=...,lancedb` emits `LanceModel` classes and
   `create_*_table` helpers.
3. You insert validated rows (model instances or compatible dicts) into LanceDB.
4. For training, pass the table to `torch.utils.data.DataLoader` using LanceDB's
   PyTorch integration (with a collate suited to your column types).

Install `py-gen-ml[lancedb]` for the runtime import; keep `lancedb` in
`--generators` whenever you regenerate so `*_lancedb.py` stays in sync with the
proto.
