## Introduction
Some configs are unlikely to ever change. In such cases, a default value can be specified.

The default needs to be propagated to the generated code. Hence, we'll add the default to the protobuf schema.

```protobuf linenums="1" hl_lines="13 15"
--8<-- "docs/snippets/proto/default.proto"
```

The default value will be added to the generated code.

```python linenums="1" hl_lines="12 15"
--8<-- "docs/snippets/src/pgml_out/default_base.py"
```

In this case, all values have a default, so it is possible to instantiate the class without specifying any values.

```python
from pgml_out.default_base import Optimizer

optimizer = Optimizer()
```

## Limitations
It is currently only possible to specify defaults for built-ins such as `string`, `float`, `int`, etc. For message
fields, you cannot specify a default value. We leave this feature for future work.
