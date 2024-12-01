import os
import time
from functools import lru_cache
from typing import Any, List

import optuna
import torch
import torch.utils.data
import torchvision
import torchvision.transforms as transforms
import typer
from pgml_out.dataloader_base import DataLoaderConfig
from pgml_out.dataloader_sweep import DataLoaderConfigSweep

import py_gen_ml as pgml


def get_transform() -> transforms.Compose:
    return transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ])


app = typer.Typer(pretty_exceptions_enable=False)


@lru_cache
def get_dataset() -> torch.utils.data.Dataset[Any]:
    dataset = torchvision.datasets.CIFAR10(
        root=f"{os.environ['HOME']}/data/torchvision", train=True, download=True, transform=get_transform()
    )
    dataset = torch.utils.data.Subset(dataset, indices=list(range(10000)))
    return dataset


def dataloader_speed_benchmark(config: DataLoaderConfig, num_iters: int = 100) -> float:
    torch.cuda.empty_cache()
    dataloader = torch.utils.data.DataLoader(
        get_dataset(),
        batch_size=config.batch_size,
        num_workers=config.num_workers,
        pin_memory=config.pin_memory,
        persistent_workers=config.persistent_workers,
        prefetch_factor=config.prefetch_factor
    )
    has_started = False
    for i in range(num_iters):
        for images, labels in dataloader:
            if not has_started:  # only start timing after the first iteration
                has_started = True
                start_time = time.time()
            images.to('cuda')
            labels.to('cuda')
            torch.cuda.synchronize()
    end_time = time.time()
    time_per_epoch = (end_time - start_time) / num_iters
    print(f'Time taken: {time_per_epoch}')
    return time_per_epoch


class RepeatPruner(optuna.pruners.BasePruner):

    def prune(self, study: optuna.Study, trial: optuna.trial.FrozenTrial) -> bool:
        trials = study.get_trials(deepcopy=False)
        if any(other_trial.params == trial.params and other_trial.number < trial.number for other_trial in trials):
            return True
        return False


@app.command()
def run(
    config_paths: List[str] = typer.Option(..., help='Paths to config files'),
    sweep_paths: List[str] = typer.Option(default_factory=list, help='Paths to sweep files'),
    num_trials: int = typer.Option(50, help='Number of trials to run')
) -> None:
    dataloader_config = DataLoaderConfig.from_yaml_files(config_paths)

    if len(sweep_paths) == 0:
        dataloader_speed_benchmark(dataloader_config, num_iters=10)
        return

    sweep_config = DataLoaderConfigSweep.from_yaml_files(sweep_paths)

    def objective(trial: optuna.Trial) -> float:
        sampler = pgml.OptunaSampler(trial=trial)
        patch = sampler.sample(sweep_config)
        return dataloader_speed_benchmark(dataloader_config.merge(patch), num_iters=10)

    study = optuna.create_study(storage='sqlite:///sweep_dataloader.db', direction='minimize', pruner=RepeatPruner())
    study.optimize(objective, n_trials=num_trials)
    print(f'Best value: {study.best_value} (params: {study.best_params})')


if __name__ == '__main__':
    app()
