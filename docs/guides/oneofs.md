# 🧅 Unions

To allow for a union of types, you can use the protobuf `oneof` keyword.

```proto hl_lines="34-37"
--8<-- "docs/snippets/proto/oneof_demo.proto"
```

The generated code will look like this:

```python { hl_lines="42" .generated-code }
--8<-- "docs/snippets/src/pgml_out/oneof_demo_base.py"
```
