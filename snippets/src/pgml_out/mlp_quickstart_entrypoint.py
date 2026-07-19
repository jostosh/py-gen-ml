import pgml_out.quickstart_b_base as base
import pgml_out.quickstart_b_sweep as sweep
import pgml_out.quickstart_b_cli_args as cli_args
import typer
import py_gen_ml as pgml
import optuna
import typing

app = typer.Typer(pretty_exceptions_enable=False)

def run_trial(
    mlp_quickstart: base.MLPQuickstart,
    trial: typing.Optional[optuna.Trial] = None
) -> typing.Union[float, typing.Sequence[float]]:
    """
    Run a trial with the given values for mlp_quickstart. The sampled
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
    cli_args: cli_args.MLPQuickstartArgs = typer.Option(...),
) -> None:
    mlp_quickstart = base.MLPQuickstart.from_yaml_files(config_paths)
    mlp_quickstart = mlp_quickstart.apply_cli_args(cli_args)
    if len(sweep_paths) == 0:
        run_trial(mlp_quickstart)
        return
    mlp_quickstart_sweep = sweep.MLPQuickstartSweep.from_yaml_files(sweep_paths)

    def objective(trial: optuna.Trial) -> typing.Union[
        float,
        typing.Sequence[float]
    ]:
        optuna_sampler = pgml.OptunaSampler(trial)
        mlp_quickstart_patch = optuna_sampler.sample(mlp_quickstart_sweep)
        mlp_quickstart_patched = mlp_quickstart.merge(mlp_quickstart_patch)
        objective_value = run_trial(mlp_quickstart_patched, trial)
        return objective_value

    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=100)


if __name__ == "__main__":
    app()