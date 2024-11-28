# 🔍 Parameter Sweeping

For parameter sweeps, `py-gen-ml` generates a Pydantic base model that replaces the types in the original config with structures that allow for defining the sampling space for each parameter.

The sweep config is then passed to a `py_gen_ml.OptunaSampler` which will sample the parameter space and return a patch that can be applied to a base config.

Your training code shouldn't have to be changed for a parameter sweep. It will receive the modified config as input and can remain oblivious to the fact that it has been sampled from a larger space.

## 🧪 Defining a parameter sweep

Let's do a benchmark on how to iterate throug a `torch.utils.data.DataLoader` as fast as possible.

### 🔧 The schema
We will define a simple schema with some parameter that influence the dataloader.

```proto
--8<-- "docs/snippets/proto/dataloader.proto"
```

When we run `py-gen-ml` it will generate a Pydantic model for parameter sweeps for us.

```python { .generated-code }
--8<-- "docs/snippets/src/pgml_out/dataloader_sweep.py"
```

You can see that it replaced the types in the original config with structures that allow for defining the sampling space for each parameter. The `pgml.IntSweep` type allows for several sampling strategies:

1. **Uniform sampling**: sample uniformly from a range by specifying `low`, `high` and optionally `step`.
2. **Discrete sampling**: sample from a list of discrete values by specifying `options`.

The `pgml.BoolSweep` type allows for sampling from a boolean space.

## ⚾ The base config
To run a benchmark we need a base config. Any sweeps will be applied to the base config by overlaying the sampled parameters.

The default YAML config is given below:
```yaml
--8<-- "docs/snippets/configs/base/dataloader_base.yaml"
```

## ✍️ The script
We will load this config in the following script:

```python linenums="1" hl_lines="3 7 9-10"
--8<-- "docs/snippets/src/snippets/sweep_dataloader.py:71:92"
```

- Line 3: the path to the config can be passed as a CLI option
- Line 7: we parse the config file
- line 9, 10: if there is no sweep file given, we run a benchmark on the base config

## 🛠️ The sweep config
Next, we'll define a minimalistic sweep config to sweep over the batch size.

```yaml
--8<-- "docs/snippets/configs/sweep/dataloader_sweep.yaml"
```

In the `run` function we load this sweep config and set a few things related to Optuna.

```python linenums="1" hl_lines="4 13 15-18 20-21"
--8<-- "docs/snippets/src/snippets/sweep_dataloader.py:71:92"
```

- Line 4: add a CLI option for the sweep config
- Line 13: load the sweep config
- Line 15-18: define the objective function. This is the function that will be optimized. It takes a `trial` object, samples the parameters for the dataloader and returns the result of the benchmark.
- Line 20: create a new study
- Line 21: run the study for a given amount of trials


We can now run the sweep with the following command:

```console
python sweep_dataloader.py \
  --config_paths \
  configs/base/default.yaml \
  --sweep_paths \
  configs/sweep/batch_size.yaml \
  --num_trials 2
```

You will see something like the following:

```
[I 2024-10-07 11:10:54,448] A new study created in RDB with name: no-name-724460b6-177e-4750-b046-15627aad8711
Files already downloaded and verified
Time taken: 1.173576545715332
[I 2024-10-07 11:11:07,083] Trial 0 finished with value: 1.173576545715332 and parameters: {'batch_size': 64}. Best is trial 0 with value: 1.173576545715332.
Files already downloaded and verified
Time taken: 1.3076978921890259
[I 2024-10-07 11:11:21,024] Trial 1 finished with value: 1.3076978921890259 and parameters: {'batch_size': 32}. Best is trial 0 with value: 1.173576545715332.
Best value: 1.173576545715332 (params: {'batch_size': 64})
```

### 💻 Benchmark
The code that actually runs the benchmark is the following:

```python linenums="1"
--8<-- "docs/snippets/src/snippets/sweep_dataloader.py:36:58"
```

## ⏳ Full sweep
A more elaborate sweep can be configured as follows:

```yaml
--8<-- "docs/snippets/configs/sweep/dataloader_sweep_full.yaml"
```

We'll keep the batch size fixed at 64 and sweep over the other parameters.

```console
python sweep_dataloader.py \
  --config_paths \
  configs/base/default.yaml \
  --sweep_paths \
  configs/sweep/full.yaml \
  --num_trials 20
```

After running this for a while, open up Optuna dashboard to see the results:

```console
optuna-dashboard sqlite:///sweep_dataloader.db
```

It will show you a web interface to inspect the results. Here's what it looks like:

![Optuna Dashboard](../assets/images/optuna_dashboard.png)

You can then quickly see the optimal set of parameters in the bottom left corner.

## 🤸‍♂️ Sweep type reference
Below, we give an overview of how field types map to the different options for sweep sampling strategies.

### 🏗️ Built-in types

#### 1️⃣ `pgml.IntSweep`
For an `int` field, `pgml.IntSweep` will offer the following sampling strategies:

- Uniform sampling: `low`, `high` and optionally `step` must be set.
- Discrete sampling: `options` must be set.
- Fixed: just provide an int

Imagine we have the following schema:

```proto
message Example {
    int32 int_field = 1;
}
```

For example, this allows you to create the following YAML structures:

```yaml title="Uniform"
int_field:
  low: 1
  high: 10
  step: 1
```

```yaml title="Discrete"
int_field:
  options:
  - 1
  - 2
  - 3
```

```yaml title="Constant"
int_field: 5
```

#### ⛵ `pgml.FloatSweep`
For a `float` field, `pgml.FloatSweep` will offer the following sampling strategies:

- Uniform sampling: `low`, `high` and optionally `step` must be set.
- Log uniform sampling: `log_low`, `log_high` must be set.
- Discrete sampling: `options` must be set.
- Fixed: just provide a float

Imagine we have the following schema:

```proto
message Example {
    float float_field = 1;
}
```

This allows you to create the following YAML structures:

```yaml title="Uniform"
float_field:
  low: 1.0
  high: 10.0
  step: 1.0
```

```yaml title="Log uniform"
float_field:
  log_low: 1.0
  log_high: 10.0
```

```yaml title="Discrete uniform"
float_field:
  options:
  - 1.0
  - 2.0
  - 5.0
```

```yaml title="Constant"
float_field: 5.0
```

#### ✅ `pgml.BoolSweep`
For a `bool` field, `pgml.BoolSweep` will offer the following sampling strategies:

- Any: use a string `"any"`. This samples from both `True` and `False`.
- Fixed: just provide a bool

Imagine we have the following schema:

```proto
message Example {
    bool bool_field = 1;
}
```

This allows us to create any of the following YAML files:

```yaml title="Uniform"
bool_field: any
```

```yaml title="Constant"
bool_field: true
```

#### ⛓️ `pgml.StringSweep`
For a `string` field, `pgml.StringSweep` will offer the following sampling strategies:

- Choice: provide a list of strings to choose from
- Fixed: just provide a string

Imagine we have the following schema:

```proto
message Example {
    string string_field = 1;
}
```

This allows us to create any of the following YAML files:

```yaml title="Uniform"
string_field:
  options:
  - hello
  - world
```

```yaml title="Constant"
string_field: hello
```


### 🧱 Custom types


#### 🐣 Nested configs
With nested configs, the ways to sweep are slightly different. Let's say we have the following schema:

```proto
message Config {
    int32 int_field = 1;
}

message Example {
    Config config_field = 1;
}
```

For the `config_field` we have the following strategies:

- Sweep: just provide one sweep for the `config_field`
- Nested sweep: provide several sweeps for the `config_field`

This allows us to create any of the following YAML files:

```yaml title="Sweep"
config_field:
  int_field:
    low: 1
    high: 10
    step: 1
```

```yaml title="Nested sweep"
config_field:
  nested_options:
    first:
      int_field:
        low: 1
        high: 10
        step: 1
    second:
      int_field:
        options:
        - 1
        - 2
        - 3
```

For the nested sweep, we'll sample categorically between `first` and `second`. We then sample uniformly between 1 and 10 for the `int_field` in case of `first` and choose from 1, 2 or 3 for the `int_field` in case of `second`.

#### 🔠 Enums
For an `enum` field, `py-gen-ml` generates a type that enables the following sampling strategies:

- Choice: provide a list of enums to choose 
- Any: use a string `"any"`. This samples from all the enum values.
- Fixed: just provide an enum

Imagine we have the following schema:

```proto
enum Color {
    RED = 0;
    GREEN = 1;
    BLUE = 2;
}

message Example {
    Color color_field = 1;
}
```

This allows us to create any of the following YAML files:

```yaml title="Discrete with options"
color_field:
  options:
  - RED
  - GREEN
  - BLUE
```

```yaml title="Discrete with all options"
color_field: any
```

```yaml title="Fixed"
color_field: RED
```
