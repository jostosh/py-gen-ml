# 🚀 Quick Start Guide

## 🌟 Introduction

`py-gen-ml` leverages [protobufs](https://developers.google.com/protocol-buffers) to define the schema for your configuration. `py-gen-ml` uses the language agnostic schema to generate code and JSON schemas from the protobuf definitions, creating a robust and versatile configuration system for machine learning projects.

!!! note
    While `py-gen-ml` currently doesn't fully utilize the language-neutral or platform-neutral features of protobuf, these capabilities are available for future expansion. If you're new to protobufs, you can learn more about them [here](https://developers.google.com/protocol-buffers).

## 📝 Defining Your Protobuf

To create a protobuf schema, you'll need to write a `.proto` file. This file contains the definition of the data structure you want to use in your configuration. The protobuf counterpart of a data object is called a `message`. Most generated files we'll see later on will contain one class per message in the protobuf file.

Here's a simple example of a protobuf definition:

```proto
--8<-- "docs/snippets/proto/quickstart_a.proto"
```

## 🛠️ Generating Configuration Utilities

With your protobuf defined, you can now **✨ generate ✨** configuration objects using this command:

```console
py-gen-ml quickstart_a.proto
```

By default, the generated code will be written to `src/pgml_out`. To customize this and explore other options, check out the [py-gen-ml command](py-gen-ml-command.md) documentation. The command will generate the following files:

- `quickstart_a_base.py`
- `quickstart_a_patch.py`
- `quickstart_a_sweep.py`

Let's dive into the details of each file.

## 🧩 Generated Code

### 📊 Generated Base Model
One of the files generated is a Pydantic model for your main configuration. 
```python { .generated-code }
--8<-- "docs/snippets/src/pgml_out/quickstart_a_base.py"
```

 Use this file to load and validate configuration files written in YAML format. As you can see, it inherits from `pgml.YamlBaseModel` which is a convenience base class that provides methods for loading configurations from YAML files.

For instance, the following YAML file will be validated according to the schema defined in `quickstart_a_base.py`:

```yaml
# example.yaml
num_layers: 2
num_units: 100
activation: relu
```

You can load the configuration like so:

```python
# example.py
from pgml_out.quickstart_a_base import MLPQuickstart

config = MLPQuickstart.from_yaml_file("example.yaml")
```


### 🔧 Generated Patch

```python { .generated-code }
--8<-- "docs/snippets/src/pgml_out/quickstart_a_patch.py"
```

This file defines a Pydantic model for your patch configuration. All fields are optional. This allows you to express experiments in terms of changes with respect to a base configuration. 

Consequently:

- Changes are small and additive
- You can easily compose multiple patches together

You can load a base configuration and apply patches using the `.from_yaml_files` method. This method is automatically inherited from `pgml.YamlBaseModel`:

```python
# example.py
from pgml_out.quickstart_a_base import MLPQuickstart
from pgml_out.quickstart_a_patch import MLPQuickstartPatch

config_with_patches = MLPQuickstart.from_yaml_files(["example.yaml", "example_patch.yaml"])
```

### 🔍 Generated Sweep Configuration

Upon running the command, you'll also get a `quickstart_a_sweep.py` file:

```python { .generated-code }
--8<-- "docs/snippets/src/pgml_out/quickstart_a_sweep.py"
```

This file defines a `pgml.Sweeper` for your configuration, enabling you to sweep over the values of your configuration. `py_gen_ml` comes with tooling to traverse the config and construct a search space for your trials. Currently, it supports [Optuna](https://optuna.org/) but we'll add more frameworks in the future.

Here's an example YAML file that will be validated according to the schema in `quickstart_a_sweep.py`:

```yaml
# example_sweep.yaml
num_layers:
  low: 1
  high: 5
```

To run a hyperparameter sweep, you can use the OptunaSampler:

```python
# example.py
from pgml_out.quickstart_base import MLP
from pgml_out.quickstart_sweep import MLPSweep

def train_model(config: MLP) -> float:
    """Train a model and return the accuracy"""

if __name__ == "__main__":
    config = MLP.from_yaml_file("example.yaml")
    sweep = MLPSweep.from_yaml_file("example_sweep.yaml")

    def objective(trial: optuna.Trial) -> float:
        sampler = pgml.OptunaSampler(trial=trial)
        patch = sampler.sample(sweep)
        accuracy = train_model(config.merge(patch))
        return accuracy

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=100)
```

## 🪄 Generating a Command Line Interface

To generate a command line interface, you'll need to add the following option to your protobuf:

```proto
option (pgml.cli).enable = true;
```

Like so:

```proto hl_lines="6 10"
--8<-- "docs/snippets/proto/quickstart_b.proto"
```

When running `py-gen-ml`, you'll now get a `quickstart_b_cli_args.py` file:

```console
py-gen-ml quickstart_b.proto
```

### 💻 Generated CLI

```python { .generated-code }
--8<-- "docs/snippets/src/pgml_out/quickstart_b_cli_args.py"
```

This file defines a Pydantic model for your command line arguments. We've chosen to use [typer](https://typer.tiangolo.com/) to handle command line arguments, and we've added a convenience function to simplify the use of this class.

The easiest way to use the CLI is to copy the generated entrypoint script. The entrypoint name is the snake case version of the name of the message with the `pgml.cli` option with `_entrypoint.py` appended.

### 🚀 Generated Entrypoint

```python { .generated-code }
--8<-- "docs/snippets/src/pgml_out/mlp_quickstart_entrypoint.py"
```

The magic happens in the `pgml.pgml_cmd` decorator. This decorator is used to wrap the `main` function and add the necessary arguments and options to the CLI.

Now you can run your script with command line arguments and configuration files:

```console
python mlp_quickstart_entrypoint.py --help
```

You can set parameters via both command line arguments and configuration files:

```console
python mlp_quickstart_entrypoint.py --config-paths example.yaml --num-layers 3
```

With these tools at your disposal, you're now ready to create flexible and powerful configurations for your machine learning projects using `py-gen-ml`! If you're looking for a more complex example, check out the [CIFAR 10 example project](example_projects/cifar10.md).
