# 🧅 Unions

ML configs often need mutually exclusive shapes: a backbone that is either a transformer or a conv net, an optimizer that is Adam or SGD, a schedule that is cosine or step. Protobuf's `oneof` encodes that exclusivity in the schema. `py-gen-ml` turns it into a typed `Union` on the generated Pydantic models.

## 📝 Defining a oneof

```proto hl_lines="34-37"
--8<-- "docs/snippets/proto/oneof_demo.proto"
```

The generated code will look like this:

```python { hl_lines="42" .generated-code }
--8<-- "docs/snippets/src/pgml_out/oneof_demo_base.py"
```

Notice `backbone: typing.Union[Transformer, ConvNet]`. Exactly one of the alternatives is expected at runtime.

## 📄 YAML shape

In YAML, nest the chosen variant under its field name. For a transformer backbone:

```yaml
backbone:
  transformer:
    num_layers: 6
    num_heads: 8
    activation: gelu
```

Or for a conv net:

```yaml
backbone:
  conv_net:
    layers:
      - out_channels: 64
        kernel_size: 3
        activation: relu
```

The generated JSON Schema validates that the payload matches one of the allowed variants.

## 🔧 Patches, sweeps, and typing

- **Patches**: each alternative can be patched independently. Unset fields on the patch leave the base alone.
- **Sweeps**: you can sweep fields inside the active variant the same way you sweep nested messages.
- **Typing**: your training code can branch with `isinstance` (or pattern matching) on the union members and stay type-checker friendly.

## ⚠️ Caveats

- A `oneof` is exclusive: don't set more than one alternative in the same config.
- Prefer `oneof` when the alternatives have different fields. If they share the same shape and only a label differs, an [enum](enums.md) is usually simpler.
