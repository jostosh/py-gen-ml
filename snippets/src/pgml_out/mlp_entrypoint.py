import pgml_out.proto_intro_base as base
import pgml_out.proto_intro_sweep as sweep
import pgml_out.proto_intro_cli_args as cli_args
import typer
import py_gen_ml as pgml
import optuna
import typing

app = typer.Typer(pretty_exceptions_enable=False)

def run_trial(
    mlp: base.MLP,
    trial: typing.Optional[optuna.Trial] = None
) -> typing.Union[float, typing.Sequence[float]]:
    """
    Run a trial with the given values for mlp. The sampled hyperparameters have
    already been added to the trial.
    """
    # TODO: Implement this function
    return 0.0

@pgml.pgml_cmd(app=app)
def main(
    config_paths: list[str] = typer.Option(..., help="Paths to config files"),
    sweep_paths: list[str] = typer.Option(
        default_factory=list,
        help="Paths to sweep files"
    ),
    cli_args: cli_args.MLPArgs = typer.Option(...),
) -> None:
    mlp = base.MLP.from_yaml_files(config_paths)
    mlp = mlp.apply_cli_args(cli_args)
    if len(sweep_paths) == 0:
        run_trial(mlp)
        return
    mlp_sweep = sweep.MLPSweep.from_yaml_files(sweep_paths)

    def objective(trial: optuna.Trial) -> typing.Union[
        float,
        typing.Sequence[float]
    ]:
        optuna_sampler = pgml.OptunaSampler(trial)
        mlp_patch = optuna_sampler.sample(mlp_sweep)
        mlp_patched = mlp.merge(mlp_patch)
        objective_value = run_trial(mlp_patched, trial)
        return objective_value

    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=100)


if __name__ == "__main__":
    app()