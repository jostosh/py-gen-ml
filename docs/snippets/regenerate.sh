#! /bin/bash

set -e

rm -rf docs/snippets/src/pgml_out

# Include opt-in generators (e.g. lancedb, bentoml, litserve). Protos without matching
# extensions are skipped by those generators.
for proto in docs/snippets/proto/*.proto; do
  uv run py-gen-ml \
    --source-root docs/snippets/src \
    --code-dir docs/snippets/src/pgml_out \
    --configs-dir docs/snippets/configs \
    --generators=base,patch,sweep,cli_args,lancedb,bentoml,litserve \
    "$proto"
done
