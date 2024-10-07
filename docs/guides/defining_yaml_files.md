YAML files are used to define the configuration of your project. To make it easier to work with YAML files, `py-gen-ml` generates JSON schemas for each protobuf model. You can use these schemas to validate your YAML files.

## Default project structure

By default, `py-gen-ml` generates the schemas under the following directories:

```
<project_root>/
    configs/
        base/
            schemas/
                <message_name_a>.json
                <message_name_b>.json
                ...
        sweep/
            schemas/
                <message_name_a>.json
                <message_name_b>.json
                ...
        cli_args/
            schemas/
                <message_name_a>.json
                <message_name_b>.json
                ...
```

## Using the schemas
To use this schema in Visual Studio Code, you can install the [YAML plugin](https://marketplace.cursorapi.com/items?itemName=redhat.vscode-yaml) and add a the following line to the top of your YAML file:

```yaml
# yaml-language-server: $schema=schemas/<message_name>.json
```
Here we assume that the file is located under `<project_root>/configs/base/`.

Here's an example of what the YAML file should look like:

```yaml linenums="1" hl_lines="1"
# yaml-language-server: $schema=schemas/mlp.json
num_layers: 3
num_units: 100
activation: relu
```

Should you misconfigure the YAML file, you'll see a validation error in Visual Studio Code.


### Nested messages
Let's say we have the following protobuf with some nesting:

```proto
--8<-- "docs/snippets/proto/advanced.proto"
```

We can define the following YAML file:

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

As you can see, we can nest the messages as we see fit.

We could then use this config to construct a model and an optimizer.

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

## Internal references with `#`

You can reuse values in your YAML file by replacing a value with a reference to another value.

The reference syntax is `#<path_to_value>`. Where path to value is a '/' separated path to the value.

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

In this case the second layer and third layer will have the same number of units and activation function as the first layer.

### Using the `_defs_` field

You can also use the `_defs_` field to reuse values. This is useful if you want to reuse values with a shorter path and a definition that is more 'centralized'.

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

### Using indices in lists

You can use indices in lists to reference specific elements in the list.

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

## External references with `!`

You can also reference values in other YAML files. This is useful if you want to reuse values across multiple YAML files.

```yaml linenums="1" hl_lines="5-8"
# configs/base/default.yaml
# yaml-language-server: $schema=schemas/training.json
mlp:
  layers:
    - '!../layer.yaml'
    - '!../layer.yaml'
    - '!../layer.yaml'
optimizer: '!../optimizer.yaml'
```
The two files referenced are:
```yaml
# configs/base/layer.yaml
num_units: 100
activation: relu
```
And the optimizer file:
```yaml
# configs/base/optimizer.yaml
type: sgd
learning_rate: 0.01
```

## Combining external and internal references
You can also combine external references with internal references by appending the internal reference to the external reference.

```yaml linenums="1" hl_lines="5-7"
# configs/base/default.yaml
# yaml-language-server: $schema=schemas/training.json
mlp:
  layers:
    - '!../layer.yaml#/layer0'
    - '!../layer.yaml#/layer1'
    - '!../layer.yaml#/layer2'
optimizer:
  type: sgd
  learning_rate: 0.01
```

The other file can then look like this:
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
