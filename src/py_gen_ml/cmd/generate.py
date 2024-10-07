import importlib
import pathlib
import sys
from typing import Optional

import grpc_tools
import grpc_tools.protoc
import typer

import py_gen_ml as pgml

app = typer.Typer(pretty_exceptions_enable=False)


@app.command()
def generate(
    proto_file: list[str] = typer.Argument(..., help='Path to the protobuf file.'),
    proto_root: Optional[str
                        ] = typer.Option(
                            None,
                            help=(
                                'Path to the root of the protobuf files which will be passed to the'
                                'protoc command as an include path. If not specified, the script '
                                'will try to infer it from the proto_file arguments by adding the '
                                'parent of the proto_file arguments.'
                            ),
                        ),
    code_dir: str = typer.Option(
        'src/pgml_out',
        help='Path to the generated code directory.',
    ),
    source_root: str = typer.Option(
        'src',
        help='Path to the root of the source code.',
    ),
    configs_dir: str = typer.Option(
        'configs',
        help='Path to the base directory for configs.',
    ),
) -> None:
    """
    Generate Pydantic models from a protobuf definition.

    This command is the core of the `py-gen-ml` toolbox. It is used to generate Pydantic models
    from a protobuf definition. By default, it will generate the models in the `src/pgml_out`
    directory. If your proto is called `example.proto`, it will generate the following files:

    - `src/pgml_out/example_base.py`
    - `src/pgml_out/example_sweep.py`
    - `src/pgml_out/example_patch.py`
    - `src/pgml_out/example_cli_args.py`

    Other than that, it will generate JSON schemas in the `configs` directory.

    The structure of the schemas is as follows:

    - `configs/base/schemas/<message_name>.json`
    - `configs/sweep/schemas/<message_name>.json`
    """
    if not code_dir.startswith(source_root):
        raise ValueError(
            'The code_dir option must be a subdirectory of the source_root option.',
        )

    # Expand any glob patterns in the proto_file arguments
    proto_files = list[pathlib.Path]()
    for path in proto_file:
        as_path = pathlib.Path(path)
        if as_path.is_absolute():
            root = pathlib.Path('/')
        else:
            root = pathlib.Path.cwd()
        proto_files.extend(root.glob(str(as_path)))

    if proto_root is None:
        proto_file_parents = set[str]()
        for pf in proto_files:
            proto_file_parents.add(str(pf.parent))
        pgml_root = pathlib.Path(pgml.__file__).parent

        parent_cli_options = [f'-I{parent}' for parent in proto_file_parents]
    else:
        parent_cli_options = [f'-I{proto_root}']

    pgml_root = pathlib.Path(pgml.__file__).parent
    cmd = [
        f"-I{pathlib.Path(grpc_tools.__file__).parent / '_proto'}",
        f"-I{grpc_tools.protoc._get_resource_file_name('grpc_tools', '_proto')}",
        *parent_cli_options,
        f'-I{str(pgml_root.parent.absolute())}',
        '--plugin=protoc-gen-py-ml=.venv/bin/protoc-gen-py-ml',
        f'--py-ml_out={code_dir}',
        f'--py-ml_opt=output_dir={code_dir}',
        f'--py-ml_opt=source_root={source_root}',
        f'--py-ml_opt=configs_dir={configs_dir}',
        *map(str, proto_files),
    ]
    pathlib.Path(code_dir).mkdir(parents=True, exist_ok=True)
    grpc_tools.protoc.main(cmd)

    python_import_path = str(
        pathlib.Path(code_dir).relative_to(pathlib.Path(source_root)),
    ).replace('/', '.') + '.__json_schema_tasks__'
    sys.path.append(source_root)
    module = importlib.import_module(python_import_path)
    tasks = module.json_schema_gen_tasks
    for task in tasks:
        task.generate()


if __name__ == '__main__':
    app()
