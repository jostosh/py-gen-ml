import os
from typing import Any

import torch
import torchvision
import torchvision.transforms as transforms


def get_transform() -> transforms.Compose:
    return transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ],)


def get_data_loader(transform: transforms.Compose, batch_size: int, train: bool) -> torch.utils.data.DataLoader[Any]:
    trainset = torchvision.datasets.CIFAR10(
        root=f"{os.environ['HOME']}/data/torchvision",
        train=train,
        download=train,
        transform=transform,
    )
    return torch.utils.data.DataLoader[Any](
        trainset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=4,
        prefetch_factor=4,
    )
