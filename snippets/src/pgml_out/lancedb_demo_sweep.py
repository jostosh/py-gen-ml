import typing

import py_gen_ml as pgml

from . import lancedb_demo_patch as patch
from . import lancedb_demo_base as base


class SampleMetaSweep(pgml.Sweeper[patch.SampleMetaPatch]):
    """Metadata nested under each training row."""

    label: typing.Optional[pgml.StrSweep] = None
    split_id: typing.Optional[pgml.IntSweep] = None


SampleMetaSweepField = typing.Union[
    SampleMetaSweep,
    pgml.NestedChoice[SampleMetaSweep, patch.SampleMetaPatch],  # type: ignore
]


class EmbeddingSampleSweep(pgml.Sweeper[patch.EmbeddingSamplePatch]):
    """Root table schema for a LanceDB dataset of embedding rows."""

    id: typing.Optional[pgml.StrSweep] = None
    embedding: typing.Optional[pgml.FloatSweep] = None
    """Fixed-size vector column for similarity search / training."""

    meta: typing.Optional[SampleMetaSweepField] = None



EmbeddingSampleSweepField = typing.Union[
    EmbeddingSampleSweep,
    pgml.NestedChoice[EmbeddingSampleSweep, patch.EmbeddingSamplePatch],  # type: ignore
]

