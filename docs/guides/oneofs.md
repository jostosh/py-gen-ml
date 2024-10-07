## Introduction
To allow for a union of types, you can use the protobuf `oneof` keyword.

```proto linenums="1" hl_lines="37-40"
--8<-- "docs/snippets/proto/oneof_demo.proto"
```

The generated code will look like this:

```python linenums="1" hl_lines="44"
--8<-- "docs/snippets/src/pgml_out/oneof_demo_base.py"
```
