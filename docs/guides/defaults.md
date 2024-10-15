# 💯 Default Values

## 👉 Setting default values
Some configs are unlikely to ever change. In such cases, a default value can be specified.

The default needs to be propagated to the generated code. Hence, we'll add the default to the protobuf schema.

```protobuf linenums="1" hl_lines="11 13"
--8<-- "docs/snippets/proto/default.proto"
```

The default value will be added to the generated code.

```python { linenums="1" hl_lines="8 11" .generated-code }
--8<-- "docs/snippets/src/pgml_out/default_base.py"
```

In this case, all values have a default, so it is possible to instantiate the class without specifying any values.

```python
from pgml_out.default_base import Optimizer

optimizer = Optimizer()
```

### 🔠 Enums
Enum values can be specified using the name of the enum value.

```proto hl_lines="23"
--8<-- "docs/snippets/proto/default_enum.proto"
```

```python { hl_lines="26" .generated-code }
--8<-- "docs/snippets/src/pgml_out/default_enum_base.py"
```

## 🚧 Limitations
It is currently only possible to specify defaults for built-ins such as `string`, `float`, `int`, etc. For message
fields, you cannot specify a default value. We leave this feature for future work.
