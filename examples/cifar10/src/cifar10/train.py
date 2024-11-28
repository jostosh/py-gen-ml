import os
import pathlib
import typing
import uuid
from typing import Any, List, Optional

import optuna
import pgml_out.config_base as base
import pgml_out.config_cli_args as cli_args
import pgml_out.config_sweep as sweep
import rich
import torch
import torch.nn as nn
import torch.optim as optim
import torch.utils.data
import torchmetrics
import torchmetrics.classification
import tqdm
import typer
from cifar10.data import get_data_loader, get_transform
from cifar10.modules import CLASSES, Model

import py_gen_ml as pgml


class Trainer:

    def __init__(
        self,
        model: torch.nn.Module,
        train_loader: torch.utils.data.DataLoader[Any],
        test_loader: torch.utils.data.DataLoader[Any],
        criterion: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        accuracy_metric_train: torchmetrics.classification.MulticlassAccuracy,
        accuracy_metric_test: torchmetrics.classification.MulticlassAccuracy,
        train_loss_metric: torchmetrics.MeanMetric,
        test_loss_metric: torchmetrics.MeanMetric,
        trial: Optional[optuna.Trial] = None,
    ) -> None:
        self._train_loader = train_loader
        self._test_loader = test_loader
        self._model = model
        self._criterion = criterion
        self._optimizer = optimizer
        self._accuracy_metric_train = accuracy_metric_train
        self._accuracy_metric_test = accuracy_metric_test
        self._train_loss_metric = train_loss_metric
        self._test_loss_metric = test_loss_metric
        self._trial = trial

    def train(self, num_epochs: int) -> float:
        device = get_device()
        step = 0
        for epoch in tqdm.trange(num_epochs, position=0, desc='Epoch'):
            batch_bar = tqdm.tqdm(self._train_loader, position=1, desc='Batch')
            for inputs, labels in batch_bar:
                inputs = inputs.to(device)
                labels = labels.to(device)

                self._optimizer.zero_grad()
                outputs = self._model(inputs)
                loss = self._criterion(outputs, labels)
                loss.backward()
                self._optimizer.step()

                self._train_loss_metric.update(loss)
                self._accuracy_metric_train.update(outputs, labels)
                step += 1

                if step % 10 == 0:
                    batch_bar.set_postfix(
                        loss=self._train_loss_metric.compute().item(),
                        accuracy=self._accuracy_metric_train.compute().item(),
                    )
                    self._train_loss_metric.reset()
                    self._accuracy_metric_train.reset()

            self._evaluate()
            if self._trial is not None:
                self._trial.report(self._accuracy_metric_test.compute().item(), epoch)
        return self._accuracy_metric_test.compute().item()

    @torch.inference_mode()
    def _evaluate(self) -> None:
        self._model.eval()
        self._accuracy_metric_test.reset()
        self._test_loss_metric.reset()
        for images, labels in tqdm.tqdm(self._test_loader, position=1, desc='Evaluating'):
            images = images.to(get_device())
            labels = labels.to(get_device())
            outputs = self._model(images)
            loss = self._criterion(outputs, labels)
            self._test_loss_metric.update(loss)
            self._accuracy_metric_test.update(outputs, labels)
        print(f'Test accuracy: {self._accuracy_metric_test.compute().item()}')
        print(f'Test loss: {self._test_loss_metric.compute().item()}')
        self._model.train()


def get_accuracy_metric(num_classes: int) -> torchmetrics.Metric:
    device = get_device()
    return torchmetrics.classification.MulticlassAccuracy(num_classes=num_classes).to(device)


def train_model(project: base.Project, trial: typing.Optional[optuna.Trial] = None) -> float:
    rich.print(project)

    transform = get_transform()
    train_loader = get_data_loader(transform=transform, batch_size=project.data.batch_size, train=True)
    test_loader = get_data_loader(transform=transform, batch_size=project.data.batch_size, train=False)

    device = get_device()
    print(f'device {device}')

    model = Model.from_config(config=project.net).to(device)
    path = pathlib.Path(f"{os.environ['HOME']}/gen_ml/logs/{uuid.uuid4()}")
    print(f'Storing logs at {path}')

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(params=model.parameters(), lr=project.optimizer.learning_rate)
    accuracy_metric_train = get_accuracy_metric(num_classes=len(CLASSES))
    accuracy_metric_test = get_accuracy_metric(num_classes=len(CLASSES))
    train_loss_metric = torchmetrics.MeanMetric().to(device)
    test_loss_metric = torchmetrics.MeanMetric().to(device)
    trainer = Trainer(
        model=model,
        train_loader=train_loader,
        test_loader=test_loader,
        criterion=criterion,
        optimizer=optimizer,
        accuracy_metric_train=accuracy_metric_train,
        accuracy_metric_test=accuracy_metric_test,
        train_loss_metric=train_loss_metric,
        test_loss_metric=test_loss_metric,
        trial=trial,
    )
    accuracy = trainer.train(num_epochs=project.data.num_epochs)
    return accuracy


app = typer.Typer(pretty_exceptions_enable=False)


@pgml.pgml_cmd(app=app)
def main(
    config_paths: List[str] = typer.Option(..., help='Paths to config files'),
    sweep_paths: List[str] = typer.Option(default_factory=list, help='Paths to sweep files'),
    cli_args: cli_args.ProjectArgs = typer.Option(...),
) -> None:
    config = base.Project.from_yaml_files(config_paths)
    config = config.apply_cli_args(cli_args)

    if len(sweep_paths) == 0:
        train_model(config, trial=None)
        return

    sweep_config = sweep.ProjectSweep.from_yaml_files(sweep_paths)

    def objective(trial: optuna.Trial) -> float:
        sampler = pgml.OptunaSampler(trial=trial)
        patch = sampler.sample(sweep_config)
        accuracy = train_model(project=config.merge(patch), trial=trial)
        return accuracy

    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=100)


def get_device() -> torch.device:
    return torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')


if __name__ == '__main__':
    app()
