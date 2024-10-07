import typing

import py_gen_ml as pgml

from . import dataloader_patch as patch
from . import dataloader_base as base


class DataLoaderConfigSweep(pgml.Sweeper[patch.DataLoaderConfigPatch]):
    """DataLoader configuration"""

    batch_size: pgml.IntSweep | None = None
    """Batch size"""

    num_workers: pgml.IntSweep | None = None
    """Number of workers"""

    pin_memory: pgml.BoolSweep | None = None
    """Pin memory"""

    persistent_workers: pgml.BoolSweep | None = None
    """Persistent workers"""

    prefetch_factor: pgml.IntSweep | None = None
    """Prefetch factor"""



DataLoaderConfigSweepField = typing.Union[
    DataLoaderConfigSweep,
    pgml.NestedChoice[DataLoaderConfigSweep, patch.DataLoaderConfigPatch],  # type: ignore
]

