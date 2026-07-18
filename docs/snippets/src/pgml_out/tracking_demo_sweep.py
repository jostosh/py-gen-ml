import typing

import py_gen_ml as pgml

from . import tracking_demo_patch as patch
from . import tracking_demo_base as base


class OptimizerCfgSweep(pgml.Sweeper[patch.OptimizerCfgPatch]):
    learning_rate: typing.Optional[pgml.FloatSweep] = None
    weight_decay: typing.Optional[pgml.FloatSweep] = None


OptimizerCfgSweepField = typing.Union[
    OptimizerCfgSweep,
    pgml.NestedChoice[OptimizerCfgSweep, patch.OptimizerCfgPatch],  # type: ignore
]


class TrainingConfigSweep(pgml.Sweeper[patch.TrainingConfigPatch]):
    """Training run hyperparameters for experiment tracking demos."""

    run_name: typing.Optional[pgml.StrSweep] = None
    """Human-readable run name (tracker tag)."""

    epochs: typing.Optional[pgml.IntSweep] = None
    optimizer: typing.Optional[OptimizerCfgSweepField] = None


TrainingConfigSweepField = typing.Union[
    TrainingConfigSweep,
    pgml.NestedChoice[TrainingConfigSweep, patch.TrainingConfigPatch],  # type: ignore
]


class TrainMetricsSweep(pgml.Sweeper[patch.TrainMetricsPatch]):
    """Metrics logged once per step or epoch."""

    accuracy: typing.Optional[pgml.FloatSweep] = None
    loss: typing.Optional[pgml.FloatSweep] = None



TrainMetricsSweepField = typing.Union[
    TrainMetricsSweep,
    pgml.NestedChoice[TrainMetricsSweep, patch.TrainMetricsPatch],  # type: ignore
]

