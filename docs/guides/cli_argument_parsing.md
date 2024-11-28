# 🖥️ CLI Argument Parsing 

## ✨ Implicit Argument References

`py-gen-ml` generates a smart CLI argument parser using Pydantic base models. It shortens CLI argument names for deeply nested fields in your config when there's exactly one path to a field and the field name is unique.

Example protobuf structure:

```protobuf hl_lines="6 10"
--8<-- "docs/snippets/proto/cli_demo.proto"
```

This generates a CLI args class:

```python { .generated-code }
--8<-- "docs/snippets/src/pgml_out/cli_demo_cli_args.py"
```

### 🚪 Generated Entrypoint

It also generates a skeleton entrypoint:

```python { .generated-code }
--8<-- "docs/snippets/src/pgml_out/cli_demo_entrypoint.py"
```

It is a standard Typer app, so you can run it like a normal Python script:

```console
python src/pgml_out/cli_demo_entrypoint.py --help
```

Which should show something like:

```console 
                                                                            
 Usage: cli_demo_entrypoint.py [OPTIONS]                                    
                                                                            
╭─ Options ────────────────────────────────────────────────────────────────╮
│ *  --config-paths              TEXT     Paths to config files            │
│                                         [default: None]                  │
│                                         [required]                       │
│    --sweep-paths               TEXT     Paths to sweep files             │
│                                         [default: <class 'list'>]        │
│    --num-epochs                INTEGER  Number of epochs. Maps to        │
│                                         'num_epochs'                     │
│                                         [default: None]                  │
│    --path                      TEXT     Path to the dataset. Maps to     │
│                                         'path'                           │
│                                         [default: None]                  │
│    --num-layers                INTEGER  Number of layers. Maps to        │
│                                         'num_layers'                     │
│                                         [default: None]                  │
│    --num-workers               INTEGER  Number of workers for loading    │
│                                         the dataset. Maps to             │
│                                         'num_workers'                    │
│                                         [default: None]                  │
│    --install-completion                 Install completion for the       │
│                                         current shell.                   │
│    --show-completion                    Show completion for the current  │
│                                         shell, to copy it or customize   │
│                                         the installation.                │
│    --help                               Show this message and exit.      │
╰──────────────────────────────────────────────────────────────────────────╯
```

Notice how the names of the args are just the names of the fields in the innermost message of the nested structure. The names are unique globally, so these short names suffice for finding the intended field within the full structure.

### 💡 Workflow

We recommend copying the generated entrypoint and modifying it to fit your needs.

For example, you might write a `run_trial` function that interfaces with your model and training code.

## ⏩ Shortening CLI arguments

As stated before, CLI argument names are shortened for deeply nested fields in your config when there's exactly one path to a field and the field name is unique. If the field name is not unique, we will prepend accessors to the field name until it is unique. 

Take for example the following protobuf file:

```protobuf
--8<-- "docs/snippets/proto/cli_demo_deep.proto"
```

This generates the following CLI arguments:

```python { .generated-code hl_lines="39-53" } 
--8<-- "docs/snippets/src/pgml_out/cli_demo_deep_cli_args.py"
```

Notice how `data.train_dataset.path` is shortened to `train_dataset_path` and `data.test_dataset.path` is shortened to `test_dataset_path`.

## 🎯 Explicit Argument References

For more control, use explicit argument references in your protobuf:

```protobuf
--8<-- "docs/snippets/proto/cli_extension_demo.proto"
```

The explicit argument references will replace the ones we have seen previously:

```python { .generated-code hl_lines="14-28" }
--8<-- "docs/snippets/src/pgml_out/cli_extension_demo_cli_args.py"
```

## 📚 Summary

With `py-gen-ml`, you get powerful, flexible CLI argument parsing that adapts to your needs, whether using implicit shortcuts or explicit references.