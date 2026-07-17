<p align="center">
   <a href="https://jostosh.github.io/py-gen-ml"><img src="docs/assets/images/logo.svg" alt="py-gen-ml" width="200"></a>

</p>
<p align="center">
    <em>py-gen-ml. Typed ML configuration tooling, generated from Protocol Buffer schemas.</em>
</p>
<p align="center">

---

**Documentation**: <a href="https://jostosh.github.io/py-gen-ml" target="_blank">https://jostosh.github.io/py-gen-ml</a>

---

# 🌟 Project Introduction

`py-gen-ml` simplifies the configuration and management of machine learning projects. You define your config schema in Protocol Buffers (protobufs). A deterministic `protoc` plugin then generates strongly typed Pydantic models, JSON Schemas, patch and sweep types, and optional Typer CLIs. Experiment configs stay robust, editable in YAML, and easy to vary without rewriting training code.

## 🧭 What this is (and isn't)

**What this is:**

- You author `.proto` files that describe your ML configuration (model hyperparams, data loaders, optimizers, and so on).
- You run `py-gen-ml`, which invokes the `protoc-gen-py-ml` plugin. That is ordinary schema-driven code generation, the same kind of pipeline as other protobuf tooling.
- From that schema you get base configs, patches, sweeps, JSON Schemas for YAML validation, CLI parsers, and optional factories to instantiate classes from config fields.

**What this isn't:**

- Not an LLM. Nothing here invents schemas, protobufs, or training code from a prompt.
- Not “AI generates your protobufs.” The direction is the opposite: **protobuf → ML config tooling**.

If you already like typed schemas and dislike hand-maintaining parallel Pydantic models for base / patch / sweep / CLI shapes, this library is for you.

## 🔄 How it fits together

```text
You write .proto
       │
       ▼
  py-gen-ml  (protoc plugin)
       │
       ├── Base Pydantic models      → load / validate YAML
       ├── Patch models              → overlay experiments
       ├── Sweep models              → Optuna search spaces
       ├── JSON Schemas              → IDE YAML validation
       └── CLI args / entrypoint     → override values from the command line
                │
                ▼
         Your training code
```

The training loop stays yours. Generated code handles loading configs, merging patches, sampling sweeps, and applying CLI overrides.

## 🔑 Key Features

**📌 Single Source of Truth**:

- The Protobuf schema provides a centralized definition for your configurations. Change the schema once. Regenerate the derived tooling.

**🔧 Flexible Configuration Management**:

- **Minimal Change Amplification**: Automatically generated code reduces cascading manual changes when modifying configurations.
- **Flexible Patching**: Easily modify base configurations with patches for quick experimentation.
- **Flexible YAML**: Use human-readable YAML with support for advanced references within and across files.
- **Hyperparameter Sweeps**: Effortlessly define and manage hyperparameter tuning.
- **CLI Argument Parsing**: Automatically generate command-line interfaces from your configuration schemas.
- **Factories**: Optionally generate `build()` helpers that instantiate Python classes from config fields.

**✅ Validation and Type Safety**:

- **JSON Schema Generation**: Easily validate your YAML content as you type.
- **Strong Typing**: The generated code comes with strong typing that will help you, your IDE, the type checker and your team to better understand the codebase and to build more robust ML code.

# 🚦 Getting Started

To start using py-gen-ml, you can install it via pip:

```console
pip install py-gen-ml
```

For a quick example of how to use py-gen-ml in your project, check out our [Quick Start Guide](https://jostosh.github.io/py-gen-ml/quickstart/).

# 💡 Motivation

Machine learning projects often involve complex configurations with many interdependent parameters. Changing one config (e.g., the dataset) might require adjusting several other parameters for optimal performance. Traditional approaches to organizing configs can become unwieldy and tightly coupled with code, making changes difficult.

`py-gen-ml` addresses these challenges by:

1. 📊 Providing a single, strongly-typed schema definition for configurations. You write that schema in protobuf.
2. 🔄 Generating deterministic code to manage configuration changes automatically (base, patch, sweep, CLI).
3. 📝 Offering flexible YAML configurations with advanced referencing and variable support.
4. 🛠️ Generating JSON schemas for real-time YAML validation.
5. 🔌 Seamlessly integrating into your workflow with multiple experiment running options:
   - Single experiments with specific config values
   - Base config patching
   - Parameter sweeps via JSON schema validated YAML files
   - Quick value overrides via a generated CLI parser
   - Arbitrary combinations of the above options

This approach results in more robust ML code, leveraging strong typing and IDE support while avoiding the burden of change amplification in complex configuration structures.

# 🎯 When to use `py-gen-ml`

Consider using `py-gen-ml` when you need to:

- 📈 Manage complex ML projects more efficiently
- 🔬 Streamline experiment running and hyperparameter tuning
- 🛡️ Reduce the impact of configuration changes on your workflow
- 💻 Leverage type safety and IDE support in your ML workflows

## 📚 Where to go from here

- [Quickstart](https://jostosh.github.io/py-gen-ml/quickstart/): A quick intro to the most important concepts.
- [Protobuf crash course](https://jostosh.github.io/py-gen-ml/guides/protobuf/): How schemas map to generated tooling.
- [Command Line Interface](https://jostosh.github.io/py-gen-ml/guides/cli_argument_parsing/): How to use the generated CLI parser.
- [Parameter Sweeps](https://jostosh.github.io/py-gen-ml/guides/sweep/): How to run parameter sweeps.
- [Generated factories](https://jostosh.github.io/py-gen-ml/guides/builders/): How to generate factories to instantiate your classes.
- [Cifar 10 example project](https://jostosh.github.io/py-gen-ml/example_projects/cifar10/): A more elaborate example of a machine learning project using `py-gen-ml`.
