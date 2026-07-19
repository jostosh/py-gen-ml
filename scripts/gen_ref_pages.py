from pathlib import Path
import shutil
from typing import List
import typer 


import mkdocs_gen_files


nav = mkdocs_gen_files.Nav()

def main(
    include: List[str] = ["**/*.py"],
    exclude: List[str] = [
        "py_gen_ml/cmd/*.py",
        "py_gen_ml/plugin/*.py",
        "py_gen_ml/typing/*.py",
        "py_gen_ml/logging/*.py",
        "**/*_pb2.py",
    ],
) -> None:
    root = Path(__file__).parents[2]
    source_dir = root / "src"
    included_files = set()
    for include_pattern in include:
        included_files.update(Path(source_dir).glob(include_pattern))
    
    excluded_files = set()
    for exclude_pattern in exclude:
        excluded_files.update(Path(source_dir).glob(exclude_pattern))
    
    files = included_files - excluded_files

    source_dir = Path(source_dir)
    for path in files: 
        module_path = path.relative_to(source_dir).with_suffix("")
        doc_path = path.relative_to(source_dir).with_suffix(".md")
        full_doc_path = Path("reference", doc_path)
        
        parts = tuple(module_path.parts)

        if parts[-1] == "__init__":
            parts = parts[:-1]
            doc_path = doc_path.with_name("index.md")
            full_doc_path = full_doc_path.with_name("index.md")
        elif parts[-1] == "__main__":
            continue

        nav[parts] = doc_path.as_posix()        
        with mkdocs_gen_files.open(full_doc_path, "w") as fd:
            ident = ".".join(parts)
            fd.write(f"::: {ident}")
            
        mkdocs_gen_files.set_edit_path(full_doc_path, path.relative_to(root))

        
    with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
        nav_file.writelines(nav.build_literate_nav())

main()