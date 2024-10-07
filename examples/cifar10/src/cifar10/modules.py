from typing import Self

import pgml_out.config_base as base
import torch

CLASSES = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']


def create_activation(activation: base.Activation) -> torch.nn.Module:
    if activation == base.Activation.GELU:
        return torch.nn.GELU()
    elif activation == base.Activation.RELU:
        return torch.nn.ReLU()
    else:
        raise ValueError(f'Invalid activation function: {activation}')


class LinearBlock(torch.nn.Module):
    """Linear layer with activation configuration"""

    def __init__(self, out_features: int, activation: base.Activation) -> None:
        super().__init__()
        self.linear = torch.nn.LazyLinear(out_features=out_features)
        self.activation = create_activation(activation)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.activation(self.linear(x))


class ConvBlock(torch.nn.Module):
    """Convolutional layer with activation configuration"""

    def __init__(self, out_channels: int, kernel_size: int, pool_size: int, activation: base.Activation) -> None:
        super().__init__()
        self.conv = torch.nn.LazyConv2d(out_channels=out_channels, kernel_size=kernel_size)
        self.pool = torch.nn.MaxPool2d(kernel_size=pool_size)
        self.activation = create_activation(activation)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.activation(self.pool(self.conv(x)))


class ConvNet(torch.nn.Module):

    def __init__(self, block: base.ConvBlock, num_layers: int) -> None:
        super().__init__()
        self.layers = [block.build() for _ in range(num_layers)]
        self.net = torch.nn.Sequential(*self.layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class MLP(torch.nn.Module):

    def __init__(self, block: base.LinearBlock, num_layers: int) -> None:
        super().__init__()
        self.layers = [block.build() for _ in range(num_layers)]
        self.net = torch.nn.Sequential(*self.layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class Model(torch.nn.Module):

    def __init__(self, conv_net: ConvNet, head: MLP) -> None:
        super().__init__()
        self.conv_net = conv_net
        self.head = head
        self.class_logits = torch.nn.LazyLinear(out_features=len(CLASSES),)
        self.flatten = torch.nn.Flatten()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.conv_net(x)
        x = self.head(x)
        x = self.flatten(x)
        x = self.class_logits(x)
        return x

    @classmethod
    def from_config(cls, config: base.Model) -> Self:
        conv_net = ConvNet(
            block=config.conv_net.block,
            num_layers=config.conv_net.num_layers,
        )
        head = MLP(
            block=config.head.block,
            num_layers=config.head.num_layers,
        )
        return cls(conv_net, head)
