import typing

import py_gen_ml as pgml

from . import dataloader_patch as patch
from . import dataloader_base as base


class DataLoaderConfigSweep(pgml.Sweeper[patch.DataLoaderConfigPatch]):
    """DataLoader configuration"""

    batch_size: typing.Optional[pgml.IntSweep] = None
    """Batch size"""

    num_workers: typing.Optional[pgml.IntSweep] = None
    """Number of workers"""

    pin_memory: typing.Optional[pgml.BoolSweep] = None
    """Pin memory"""

    persistent_workers: typing.Optional[pgml.BoolSweep] = None
    """Persistent workers"""

    prefetch_factor: typing.Optional[pgml.IntSweep] = None
    """Prefetch factor"""



DataLoaderConfigSweepField = typing.Union[
    DataLoaderConfigSweep,
    pgml.NestedChoice[DataLoaderConfigSweep, patch.DataLoaderConfigPatch],  # type: ignore
]

