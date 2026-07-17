# 💯 Default Values

## 👉 Setting default values

Some config fields almost never change for a given project. Think of a standard epsilon, a default activation, or a fixed bias flag. Putting those defaults in the protobuf schema keeps YAML files focused on what actually varies. The generated Pydantic models pick up the same defaults so Python construction stays consistent.

The default needs to be propagated to the generated code. Hence, we'll add the default to the protobuf schema using `(pgml.default)`.

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

## 🔌 How defaults interact with the rest of the stack

- **YAML**: omit a field and the generated model fills in the proto default when the object is constructed.
- **Patches**: a patch can still override a defaulted field. Leaving it unset on the patch keeps the base (or default) value.
- **CLI**: command-line overrides win over whatever was loaded from YAML / defaults, same as other fields.

Putting defaults in the schema keeps the single source of truth story intact. That beats scattering the same values across YAML and Python.

## 🚧 Limitations
It is currently only possible to specify defaults for built-ins such as `string`, `float`, `int`, etc. For message
fields, you cannot specify a default value. We leave this feature for future work.
