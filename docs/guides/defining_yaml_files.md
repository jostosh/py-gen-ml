# 📝 Defining YAML Files

YAML files are the backbone of your project's configuration in `py-gen-ml`. To make working with these files a breeze, `py-gen-ml` automatically generates JSON schemas for each protobuf model. These schemas are your secret weapon for validating YAML files with ease!

## 🏗️ Default Project Structure

When you use `py-gen-ml`, it sets up a neat and organized structure for your schemas:

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

## 🛠️ Putting Schemas to Work

Want to leverage these schemas in Visual Studio Code? It's simple! Just install the [YAML plugin](https://marketplace.cursorapi.com/items?itemName=redhat.vscode-yaml) and add this line to the top of your YAML file:

```yaml
# yaml-language-server: $schema=schemas/<message_name>.json
```

(We're assuming your file is located under `<project_root>/configs/base/`.)

Let's take the following proto as an example:

```proto
--8<-- "docs/snippets/proto/mlp.proto"
``` 

Here's a quick example of what your YAML file might look like:

```yaml linenums="1" hl_lines="1"
--8<-- "docs/snippets/configs/base/mlp.yaml"
```

Now, if you accidentally misconfigure your YAML file, Visual Studio Code will give you a friendly heads-up with a validation error.

The video below shows how the editor leverages the schema to know exactly which fields can be added and when the field is invalid:

![type:video](../assets/video/parsing.webm)

You can see that:

1. The leading comment we have added to the message in the proto shows at the top of the file.
2. By pressing ++cmd+space++ (or ++ctrl+space++ on Linux) with an empty file, we see the list of possible fields.
3. By pressing ++cmd+space++ (or ++ctrl+space++ on Linux) after typing `activation:`, we get a list of possible values for the field.
4. By entering an invalid value for `num_units`, we get a validation error.

## 🧩 Handling Nested Messages

Let's kick things up a notch with a more complex protobuf that includes some nesting:

```proto
--8<-- "docs/snippets/proto/advanced.proto"
```

You can define a YAML file for this structure like so:

```yaml
# configs/base/default.yaml
# yaml-language-server: $schema=schemas/training.json
mlp:
  layers:
    - num_units: 100
      activation: relu
    - num_units: 200
      activation: relu
    - num_units: 100
      activation: relu
optimizer:
  type: sgd
  learning_rate: 0.01
```

As you can see, the nesting in the YAML file mirrors the nesting in the protobuf.

Now, let's put this config to work by creating a model and an optimizer:

```python
from pgml_out.advanced_base import Training

def create_model(config: Training) -> torch.nn.Module:
    layers = []
    for layer in config.mlp.layers:
        layers.append(torch.nn.Linear(layer.num_units, layer.num_units))
        layers.append(torch.nn.ReLU() if layer.activation == "relu" else torch.nn.Tanh())
    return torch.nn.Sequential(*layers)

def create_optimizer(model: torch.nn.Module, config: Training) -> torch.optim.Optimizer:
    return torch.optim.SGD(model.parameters(), lr=config.optimizer.learning_rate)

if __name__ == "__main__":
    config = Training.from_yaml_file("configs/base/default.yaml")
    model = create_model(config)
    optimizer = create_optimizer(model, config)
```

## 🔗 Internal References with `#`

Want to reuse values in your YAML file? `py-gen-ml` has got you covered! You can replace a value with a reference to another value using the `#<path_to_value>` syntax. Here's how it works:

```yaml linenums="1" hl_lines="7-10"
# configs/base/default.yaml
# yaml-language-server: $schema=schemas/training.json
mlp:
  layers:
    - num_units: 100
      activation: relu
    - num_units: "#/mlp/layers[0]/num_units"
      activation: "#/mlp/layers[0]/activation"
    - num_units: "#/mlp/layers[0]/num_units"
      activation: "#/mlp/layers[0]/activation"
optimizer:
  type: sgd
  learning_rate: 0.01
```

In this example, the second and third layers will mirror the number of units and activation function of the first layer. 

### 🎯 Using the `_defs_` Field

For even more flexibility, you can use the `_defs_` field. It's perfect for reusing values with shorter paths and a more centralized definition:

```yaml linenums="1" hl_lines="5-7 11-14"
# configs/base/default.yaml
# yaml-language-server: $schema=schemas/training.json
mlp:
  layers:
    - '#/_defs_/layer'
    - '#/_defs_/layer'
    - '#/_defs_/layer'
optimizer:
  type: sgd
  learning_rate: 0.01
_defs_:
  layer:
    num_units: 100
    activation: relu
```

### 📊 Using Indices in Lists

Need to reference specific elements in a list? No problem! You can use indices like this:

```yaml linenums="1" hl_lines="7"
# configs/base/default.yaml
# yaml-language-server: $schema=schemas/training.json
mlp:
  layers:
    - num_units: 100
      activation: relu
    - '#/mlp/layers[2]'
    - num_units: 200
      activation: relu
optimizer:
  type: sgd
  learning_rate: 0.01
```

### 👪 Relative Internal References

You can also use relative internal references. This is useful if you want to reuse values in a nested structure and the reference
is close to the reused value.

```yaml linenums="1" hl_lines="11"
# configs/base/default.yaml
# yaml-language-server: $schema=schemas/training.json
foo:
  bar:
    data:
      train_dataset:
        path: train.csv
        batch_size: 32
      test_dataset:
        path: test.csv
        batch_size: '#../train_dataset/batch_size'
optimizer:
  type: sgd
  learning_rate: 0.01
```

This allows you to skip the `/foo/bar` prefix to get to the `data` field. It also makes this part of the YAML
file more self-contained: you can safely copy this part to a different YAML that follows a different schema
yet the same relative structure for the `data` field.

## 🌐 External References with `!`

Want to reuse values across multiple YAML files? External references by prefixing the path with `!` is the way to go:

```yaml linenums="1" hl_lines="5-8"
# configs/base/default.yaml
# yaml-language-server: $schema=schemas/training.json
mlp:
  layers:
    - '!layer.yaml'
    - '!layer.yaml'
    - '!layer.yaml'
optimizer: '!optimizer.yaml'
```

The referenced files might look like this:

```yaml
# configs/base/layer.yaml
num_units: 100
activation: relu
```

```yaml
# configs/base/optimizer.yaml
type: sgd
learning_rate: 0.01
```

## 🔀 Combining External and Internal References

For the ultimate flexibility, you can mix and match external and internal references:

```yaml linenums="1" hl_lines="5-7"
# configs/base/default.yaml
# yaml-language-server: $schema=schemas/training.json
mlp:
  layers:
    - '!layer.yaml#/layer0'
    - '!layer.yaml#/layer1'
    - '!layer.yaml#/layer2'
optimizer:
  type: sgd
  learning_rate: 0.01
```

With the corresponding `layer.yaml`:

```yaml
# configs/base/layer.yaml
layer0:
    num_units: 100
    activation: relu
layer1:
    num_units: 200
    activation: relu
layer2:
    num_units: 100
    activation: relu
```

And there you have it! With these powerful YAML configuration techniques at your fingertips, you're all set to create flexible and maintainable machine learning projects using `py-gen-ml`. Happy coding! 🚀