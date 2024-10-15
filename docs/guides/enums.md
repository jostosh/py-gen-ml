# 🔠 Enums
Enums can be used to represent a set of named values that can be assigned to a field.

Protobuf provides a dedicated syntax for defining enums.
```proto
--8<-- "docs/snippets/proto/enum_demo.proto"
```

The generated code will look like this:

```python { .generated-code }
--8<-- "docs/snippets/src/pgml_out/enum_demo_base.py"
```
