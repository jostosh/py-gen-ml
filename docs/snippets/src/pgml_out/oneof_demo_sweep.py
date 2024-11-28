import typing

import py_gen_ml as pgml

from . import oneof_demo_patch as patch
from . import oneof_demo_base as base


class TransformerSweep(pgml.Sweeper[patch.TransformerPatch]):
    """Transformer configuration"""

    num_layers: typing.Optional[pgml.IntSweep] = None
    """Number of layers"""

    num_heads: typing.Optional[pgml.IntSweep] = None
    """Number of heads"""

    activation: typing.Optional[pgml.StrSweep] = None
    """Activation function"""


TransformerSweepField = typing.Union[
    TransformerSweep,
    pgml.NestedChoice[TransformerSweep, patch.TransformerPatch],  # type: ignore
]


class ConvBlockSweep(pgml.Sweeper[patch.ConvBlockPatch]):
    """Conv block"""

    out_channels: typing.Optional[pgml.IntSweep] = None
    """Number of output channels"""

    kernel_size: typing.Optional[pgml.IntSweep] = None
    """Kernel size"""

    activation: typing.Optional[pgml.StrSweep] = None
    """Activation function"""


ConvBlockSweepField = typing.Union[
    ConvBlockSweep,
    pgml.NestedChoice[ConvBlockSweep, patch.ConvBlockPatch],  # type: ignore
]


class ConvNetSweep(pgml.Sweeper[patch.ConvNetPatch]):
    """Convolutional neural network configuration"""

    layers: typing.Optional[ConvBlockSweepField] = None
    """Conv layer configuration"""


ConvNetSweepField = typing.Union[
    ConvNetSweep,
    pgml.NestedChoice[ConvNetSweep, patch.ConvNetPatch],  # type: ignore
]


class ModelSweep(pgml.Sweeper[patch.ModelPatch]):
    """Model configuration"""

    backbone: typing.Optional[typing.Union[pgml.Sweeper[TransformerSweepField],
                                           pgml.Sweeper[ConvNetSweepField]]] = None



ModelSweepField = typing.Union[
    ModelSweep,
    pgml.NestedChoice[ModelSweep, patch.ModelPatch],  # type: ignore
]

