# 🔠 Enums

Enums represent a fixed set of named values you can assign to a field. In ML configs they're a natural fit for things like activation functions, optimizers, or schedule kinds. Anywhere a free-form string would invite typos and drift, an enum is safer.

You define the enum in your protobuf schema. `py-gen-ml` then generates a Python `Enum` and wires it into the base, patch, and sweep models.

## 📝 Defining an enum

Protobuf provides a dedicated syntax for defining enums:

```proto
--8<-- "docs/snippets/proto/enum_demo.proto"
```

The generated code will look like this:

```python { .generated-code }
--8<-- "docs/snippets/src/pgml_out/enum_demo_base.py"
```

## 📄 Using enums in YAML

In YAML, write the enum member name as a string (matching the proto identifier):

```yaml
activation: RELU
num_layers: 3
```

The generated JSON Schema for the base model will constrain the field to the allowed values, so your editor can flag invalid names as you type.

## 🔧 Patches and sweeps

- **Patches**: the enum field is optional on the patch model, so you can override just the activation (or leave it unset).
- **Sweeps**: you can list allowed enum values in a sweep YAML and let the sampler pick among them. That is the same idea as sweeping other categorical fields.

## 💡 Naming tip

Prefer clear, uppercase proto enum values (`RELU`, `GELU`) and keep the set small. If two concepts share a name across messages, consider nested enums or a shared package-level enum so the schema stays readable.
