# `py-gen-ml`

Generate Pydantic models from a protobuf definition.

This command is the core of the `py-gen-ml` toolbox. It is used to generate Pydantic models
from a protobuf definition. By default, it generates models in the `src/pgml_out`
directory. If your proto is called `example.proto`, it generates the following files:

- `src/pgml_out/example_base.py` for a base model that follows the protobuf definition
- `src/pgml_out/example_sweep.py` for a sweep model that can be used to sweep the base model
- `src/pgml_out/example_patch.py` for a patch model that can be used to patch the base model

If you've set the CLI option on a message called `Foo`, it will also generate

- `src/pgml_out/example_cli_args.py` for CLI argument models
- `src/pgml_out/foo_entrypoint.py` for an entrypoint that combines the base config, sweep, and CLI arguments.

Other than that, it will generate JSON schemas in the `configs` directory.

The structure of the schemas is as follows:

- `configs/base/schemas/<message_name>.json`    
- `configs/patch/schemas/<message_name>.json`
- `configs/sweep/schemas/<message_name>.json`

**Usage**:

```console
$ py-gen-ml [OPTIONS] PROTO_FILE...
```

**Arguments**:

* `PROTO_FILE...`: Path to the protobuf file.  [required]

**Options**:

* `--proto-root TEXT`: Path to the root of the protobuf files which will be passed to theprotoc command as an include path. If not specified, the script will try to infer it from the proto_file arguments by adding the parent of the proto_file arguments.
* `--code-dir TEXT`: Path to the generated code directory.  [default: src/pgml_out]
* `--source-root TEXT`: Path to the root of the source code.  [default: src]
* `--configs-dir TEXT`: Path to the base directory for configs.  [default: configs]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.
