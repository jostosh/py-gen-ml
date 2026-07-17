## Introduction

Here we will walk through an example project for training a model to classify images from the CIFAR10 dataset. The full source lives in the repo under [`examples/cifar10/`](https://github.com/jostosh/py-gen-ml/tree/main/examples/cifar10). The flow is end-to-end `py-gen-ml`. You author a protobuf schema, generate typed config tooling, then load YAML, apply CLI overrides, and optionally sweep. The training loop stays ordinary Python. This combines most of the concepts from the guides so far. It offers a simple model, data and optimizer, and shows how to:

- Use a variety of special attributes to define the config schema
- Load a config from a yaml file
- Apply CLI arguments to the config
- Load a sweep file to sample from a set of configurations

## Schema

The schema is defined in a proto file. This is the file that we will use to train the model. It looks like this:

### The model

The model definition is a simple convolutional neural network followed by a multi-layer perceptron. In proto definition, it looks like this:

```proto
--8<-- "examples/cifar10/src/cifar10/config.proto:25:77"
```

Concepts that we've used here are:

- Nesting: we define a `Model` message that contains two nested messages: `ConvNet` and `MLP` which in turn contain blocks of linear and convolutional layers.
- `pgml.factory`: This is a special attribute that tells `py-gen-ml` that with these values we can build an instance of the given class.
- `pgml.default`: This is a special attribute that tells `py-gen-ml` to use a default value if the field is not set.
- Enums: we define an enum for the activation function.

### The data

We define a `Data` message that contains the batch size and the number of epochs to train. In proto definition, it looks like this:

```proto
--8<-- "examples/cifar10/src/cifar10/config.proto:86"
```

### The optimizer

We define an `Optimizer` message that contains the learning rate and the decay rate. In proto definition, it looks like this:

```proto
--8<-- "examples/cifar10/src/cifar10/config.proto:79:85"
```

### The project

We define a `Project` message that contains the model, the optimizer, and the data. In proto definition, it looks like this:

```proto
--8<-- "examples/cifar10/src/cifar10/config.proto:1:23"
```
As you can see, there are a couple of arg references to ensure we can propagate values via the command line for fields that have the same name and that are deeply nested.

## The entrypoint
To launch the training, we create a function that can do a range of things:

1. Load a yaml config file
2. Load multiple yaml config files and merge them
3. Load a yaml sweep file to generate patches and apply them to the config using Optuna
4. Apply CLI arguments to the config
5. Whatever the input is, train the model and return the accuracy

Even though this sounds like a lot, with `pg-gen-ml` it is actually quite easy to do. The main function now becomes:

```python title="Entrypoint" linenums="1"
--8<-- "examples/cifar10/src/cifar10/train.py:145:167"
```

Let's break this down a bit more.

- At line 7, we load the project config from one or more yaml files. This is where files will be merged before they are passed to the Pydantic model validator.
- At line 8, we apply the CLI arguments to the config.
- At line 10, we check if there are any sweep files. If there are, we load them at line 14. If there are no sweep files, we simply train the model and return the accuracy.
- At line 16-20, we define an objective function for Optuna to use. This is the function that will be called to train the model and return the accuracy. Note that we are using the exact same `train_model` function that we used in line 10 earlier.
- At line 22 and 23, we create an Optuna study and optimize the objective function.

## The configuration

The configuration is defined in a yaml file. This is the file that we will use to train the model. It looks like this:

```yaml title="Config"
--8<-- "examples/cifar10/configs/base/default.yaml"
```

## Sweep configuration

We define the following sweep configuration:

```yaml title="Sweep"
--8<-- "examples/cifar10/configs/sweep/lr_beta1.yaml"
```

This is a sweep over the learning rate and beta1 parameters. We'll use it below when launching Optuna trials.

## Example code overview

Hand-written training code lives under [`examples/cifar10/src/cifar10/`](https://github.com/jostosh/py-gen-ml/tree/main/examples/cifar10/src/cifar10). Generated config tooling lives under [`examples/cifar10/src/pgml_out/`](https://github.com/jostosh/py-gen-ml/tree/main/examples/cifar10/src/pgml_out). Rough map:

| Piece | Path | Role |
|-------|------|------|
| Schema | `config.proto` | Source of truth for the project config |
| Generated models | `pgml_out/config_{base,patch,sweep,cli_args}.py` | Load YAML, merge patches, sample sweeps, parse CLI |
| Modules | `modules.py` | Conv / MLP building blocks and `Model.from_config` |
| Data | `data.py` | CIFAR-10 transforms and DataLoaders |
| Trainer | `train.py` (`Trainer`) | Train / eval loop, optional Optuna trial reporting |
| Train function | `train.py` (`train_model`) | Wire config → model, data, optimizer, trainer |
| Entrypoint | `train.py` (`main`) | `@pgml.pgml_cmd` CLI: configs, sweeps, CLI overrides |

### Modules

```python title="Modules"
--8<-- "examples/cifar10/src/cifar10/modules.py"
```

### Data

```python title="Data"
--8<-- "examples/cifar10/src/cifar10/data.py"
```

### Trainer

```python title="Trainer"
--8<-- "examples/cifar10/src/cifar10/train.py:26:98"
```

### Train function

The train function that instantiates all the components and calls the trainer:

```python title="Train function"
--8<-- "examples/cifar10/src/cifar10/train.py:106:139"
```

## How to run

All commands below assume you are in the example project directory:

```console
cd examples/cifar10
```

Install the example (pulls in `py-gen-ml` from the workspace plus Torch):

```console
uv sync
```

### Inspect the CLI

```console
uv run python src/cifar10/train.py --help
```

This prints the generated options, including nested field overrides:

```
 Usage: train.py [OPTIONS]

╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --config-paths              TEXT         Path to config file [default: None] [required]                                             │
│    --sweep-paths               TEXT         Type of config to use [default: <class 'list'>]                                            │
│    --out-channels              INTEGER      Number of output channels. Maps to 'net.conv_net.block.out_channels' [default: None]       │
│    --kernel-size               INTEGER      Square kernel size. Maps to 'net.conv_net.block.kernel_size' [default: None]               │
│    --pool-size                 INTEGER      Square pool size. Maps to 'net.conv_net.block.pool_size' [default: None]                   │
│    --out-features              INTEGER      Number of output features. Maps to 'net.head.block.out_features' [default: None]           │
│    --batch-size                INTEGER      Batch size for a single GPU. Maps to 'data.batch_size' [default: None]                     │
│    --num-epochs                INTEGER      Number of epochs to train. Maps to 'data.num_epochs' [default: None]                       │
│    --learning-rate             FLOAT        Learning rate. Maps to 'optimizer.learning_rate' [default: None]                           │
│    --beta1                     FLOAT        Decay rate. Maps to 'optimizer.beta1' [default: None]                                      │
│    --conv-activation           [gelu|relu]  Activation function. Maps to 'net.conv_net.block.activation' [default: None]               │
│    --head-activation           [gelu|relu]  Activation function. Maps to 'net.head.block.activation' [default: None]                   │
│    --num-conv-layers           INTEGER      Number of layers. Maps to 'net.conv_net.num_layers' [default: None]                        │
│    --num-mlp-layers            INTEGER      Number of layers. Maps to 'net.head.num_layers' [default: None]                            │
│    --install-completion                     Install completion for the current shell.                                                  │
│    --show-completion                        Show completion for the current shell, to copy it or customize the installation.           │
│    --help                                   Show this message and exit.                                                                │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### Simple run (base config only)

Train once with the default YAML:

```console
uv run python src/cifar10/train.py \
    --config-paths configs/base/default.yaml
```

### CLI overrides

Same base config, but override a few fields from the command line (no second YAML needed):

```console
uv run python src/cifar10/train.py \
    --config-paths configs/base/default.yaml \
    --learning-rate 1e-3 \
    --batch-size 64 \
    --num-epochs 2
```

### Hyperparameter sweep

Run an Optuna study over the learning rate and beta1 search space. Each trial merges a sampled patch onto the base config and calls the same `train_model`:

```console
uv run python src/cifar10/train.py \
    --config-paths configs/base/default.yaml \
    --sweep-paths configs/sweep/lr_beta1.yaml
```

### Sweep plus CLI overrides

CLI args still apply on top of the base config before sampling. Useful for fixing something like epoch count while sweeping the optimizer:

```console
uv run python src/cifar10/train.py \
    --config-paths configs/base/default.yaml \
    --sweep-paths configs/sweep/lr_beta1.yaml \
    --num-epochs 1 \
    --batch-size 128
```

!!! tip
    Pass multiple `--config-paths` to merge base + patch YAML files before training or sweeping. Later files overlay earlier ones the same way as elsewhere in `py-gen-ml`.

## Conclusion

This example is a small but complete training project built around a protobuf schema. You write `config.proto` and the YAML. `py-gen-ml` generates the typed base / patch / sweep / CLI layer. `train.py` stays ordinary PyTorch. The same entrypoint covers a single run, CLI experiments, and Optuna sweeps without forking the train loop.
