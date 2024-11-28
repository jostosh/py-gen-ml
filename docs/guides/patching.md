# 🧩 Patching

YAML files can be patched together to manage smaller changes without having to copy or re-write the entire configuration. This approach is particularly useful for temporary changes targeted at a single run or a small set of runs. Patches allow you to conceptualize experiments in terms of changes relative to a baseline configuration, rather than considering the full configuration each time.

## 📊 JSON Schemas

When you set up a protobuf schema and run `py-gen-ml`, it generates three types of JSON schemas:

```
<project_root>/
    configs/
        base/
            schemas/
                <message_name_a>.json
                <message_name_b>.json
                ...
        patch/
            schemas/
                <message_name_a>.json
                <message_name_b>.json
                ...
        sweep/
            schemas/
                <message_name_a>.json
                <message_name_b>.json
                ...
```

In the [previous guide](./defining_yaml_files.md), we explored how to leverage the base schemas for validation in your IDE.

## 🏗️ Pydantic Models

The patch schemas are generated from the patch Pydantic models, which contain all fields of the base model but modified to be optional. This allows you to specify only the fields you want to change in your patch.

Let's examine an example.

1. The proto
```proto
--8<-- "docs/snippets/proto/quickstart_a.proto"
```

2. The generated base model
```py { .generated-code }
--8<-- "docs/snippets/src/pgml_out/quickstart_a_base.py"
```

3. The generated patch model
```py { .generated-code }
--8<-- "docs/snippets/src/pgml_out/quickstart_a_patch.py"
```

As you can observe in (3), we can choose to omit any fields that we don't want to change, as their defaults are set to `None`.

## 🎨 Defining a Patch

Consider this baseline config:

```yaml
# configs/base/mlp.yaml
# yaml-language-server: $schema=schemas/mlp.json
num_layers: 3
num_units: 100
activation: relu
```

If you want to run an experiment where you change the number of layers to 4, you can create the following patch:

```yaml
# configs/patch/mlp_num_layers.yaml
# yaml-language-server: $schema=schemas/mlp_patch.json
num_layers: 4
```

## 🔧 Loading a Patch

In your script, you can load the base config and the patch config and merge them together:

```py
from pgml_out.proto_intro_base import MLP

config = MLP.from_yaml_files([
    "configs/base/mlp.yaml",
    "configs/patch/mlp_num_layers.yaml",
])
```

The `from_yaml_files` function will merge the patch into the base config using [`jsonmerge`](https://pypi.org/project/jsonmerge/).

### 🔍 Loading a Patch Separately

If you need to load the patch separately from the base config, you can use the `from_yaml_file` method with the patch Pydantic model:

```py
patch = MLPPatch.from_yaml_file("configs/patch/mlp_num_layers.yaml")
```

You can then merge the patch with the base config in your script:

```py
config = MLP.from_yaml_file("configs/base/mlp.yaml")
patched_config = config.merge(patch)
```

The `merge` method also patches the config using `jsonmerge`.

By utilizing these patching techniques, you can efficiently manage and experiment with your configurations.