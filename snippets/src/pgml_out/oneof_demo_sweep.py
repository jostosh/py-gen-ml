import typing

import py_gen_ml as pgml

from . import oneof_demo_patch as patch
from . import oneof_demo_base as base


class TransformerSweep(pgml.Sweeper[patch.TransformerPatch]):
    """Transformer configuration"""

    num_layers: pgml.IntSweep | None = None
    """Number of layers"""

    num_heads: pgml.IntSweep | None = None
    """Number of heads"""

    activation: pgml.StrSweep | None = None
    """Activation function"""


TransformerSweepField = typing.Union[
    TransformerSweep,
    pgml.NestedChoice[TransformerSweep, patch.TransformerPatch],  # type: ignore
]


class ConvBlockSweep(pgml.Sweeper[patch.ConvBlockPatch]):
    """Conv block"""

    out_channels: pgml.IntSweep | None = None
    """Number of output channels"""

    kernel_size: pgml.IntSweep | None = None
    """Kernel size"""

    activation: pgml.StrSweep | None = None
    """Activation function"""


ConvBlockSweepField = typing.Union[
    ConvBlockSweep,
    pgml.NestedChoice[ConvBlockSweep, patch.ConvBlockPatch],  # type: ignore
]


class ConvNetSweep(pgml.Sweeper[patch.ConvNetPatch]):
    """Convolutional neural network configuration"""

    layers: ConvBlockSweepField | None = None
    """Conv layer configuration"""


ConvNetSweepField = typing.Union[
    ConvNetSweep,
    pgml.NestedChoice[ConvNetSweep, patch.ConvNetPatch],  # type: ignore
]


class ModelSweep(pgml.Sweeper[patch.ModelPatch]):
    """Model configuration"""

    backbone: pgml.Sweeper[TransformerSweepField] | pgml.Sweeper[ConvNetSweepField
                                                                ] | None = None



ModelSweepField = typing.Union[
    ModelSweep,
    pgml.NestedChoice[ModelSweep, patch.ModelPatch],  # type: ignore
]

