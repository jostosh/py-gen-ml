#! /bin/bash

set -e

rm -rf docs/snippets/src/pgml_out

find docs/snippets/proto -name "*.proto" -exec py-gen-ml --source-root docs/snippets/src --code-dir docs/snippets/src/pgml_out --configs-dir docs/snippets/configs {} \;
