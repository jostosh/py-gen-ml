import pgml_out.dataloader_base as base
import pgml_out.dataloader_sweep as sweep
import pgml_out.dataloader_cli_args as cli_args
import typer
import py_gen_ml as pgml
import optuna
import typing

app = typer.Typer(pretty_exceptions_enable=False)

def run_trial(
    data_loader_config: base.DataLoaderConfig,
    trial: typing.Optional[optuna.Trial] = None
) -> typing.Union[float, typing.Sequence[float]]:
    """
    Run a trial with the given values for data_loader_config. The sampled
    hyperparameters have already been added to the trial.
    """
    # TODO: Implement this function
    return 0.0

@pgml.pgml_cmd(app=app)
def main(
    config_paths: typing.List[str] = typer.Option(..., help="Paths to config files"),
    sweep_paths: typing.List[str] = typer.Option(
        default_factory=list,
        help="Paths to sweep files"
    ),
    cli_args: cli_args.DataLoaderConfigArgs = typer.Option(...),
) -> None:
    data_loader_config = base.DataLoaderConfig.from_yaml_files(config_paths)
    data_loader_config = data_loader_config.apply_cli_args(cli_args)
    if len(sweep_paths) == 0:
        run_trial(data_loader_config)
        return
    data_loader_config_sweep = sweep.DataLoaderConfigSweep.from_yaml_files(sweep_paths)

    def objective(trial: optuna.Trial) -> typing.Union[
        float,
        typing.Sequence[float]
    ]:
        optuna_sampler = pgml.OptunaSampler(trial)
        data_loader_config_patch = optuna_sampler.sample(data_loader_config_sweep)
        data_loader_config_patched = data_loader_config.merge(data_loader_config_patch)
        objective_value = run_trial(data_loader_config_patched, trial)
        return objective_value

    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=100)


if __name__ == "__main__":
    app()