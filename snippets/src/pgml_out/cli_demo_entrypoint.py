import pgml_out.cli_demo_base as base
import pgml_out.cli_demo_sweep as sweep
import pgml_out.cli_demo_cli_args as cli_args
import typer
import py_gen_ml as pgml
import optuna
import typing

app = typer.Typer(pretty_exceptions_enable=False)

def run_trial(
    cli_demo: base.CLIDemo,
    trial: typing.Optional[optuna.Trial] = None
) -> typing.Union[float, typing.Sequence[float]]:
    """
    Run a trial with the given values for cli_demo. The sampled hyperparameters have
    already been added to the trial.
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
    cli_args: cli_args.CLIDemoArgs = typer.Option(...),
) -> None:
    cli_demo = base.CLIDemo.from_yaml_files(config_paths)
    cli_demo = cli_demo.apply_cli_args(cli_args)
    if len(sweep_paths) == 0:
        run_trial(cli_demo)
        return
    cli_demo_sweep = sweep.CLIDemoSweep.from_yaml_files(sweep_paths)

    def objective(trial: optuna.Trial) -> typing.Union[
        float,
        typing.Sequence[float]
    ]:
        optuna_sampler = pgml.OptunaSampler(trial)
        cli_demo_patch = optuna_sampler.sample(cli_demo_sweep)
        cli_demo_patched = cli_demo.merge(cli_demo_patch)
        objective_value = run_trial(cli_demo_patched, trial)
        return objective_value

    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=100)


if __name__ == "__main__":
    app()