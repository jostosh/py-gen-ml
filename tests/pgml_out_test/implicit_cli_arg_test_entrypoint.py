import typing

import optuna
import pgml_out_test.unit_base as base
import pgml_out_test.unit_cli_args as cli_args
import pgml_out_test.unit_sweep as sweep
import typer

import py_gen_ml as pgml

app = typer.Typer(pretty_exceptions_enable=False)


def run_trial(
    implicit_cli_arg_test: base.ImplicitCLIArgTest,
    trial: typing.Optional[optuna.Trial] = None,
) -> typing.Union[float, typing.Sequence[float]]:
    """
    Run a trial with the given values for implicit_cli_arg_test. The sampled
    hyperparameters have already been added to the trial.
    """
    # TODO: Implement this function
    return 0.0


@pgml.pgml_cmd(app=app)
def main(
    config_paths: typing.List[str] = typer.Option(..., help='Paths to config files'),
    sweep_paths: typing.List[str] = typer.Option(
        default_factory=list,
        help='Paths to sweep files',
    ),
    cli_args: cli_args.ImplicitCLIArgTestArgs = typer.Option(...),
) -> None:
    implicit_cli_arg_test = base.ImplicitCLIArgTest.from_yaml_files(config_paths)
    implicit_cli_arg_test = implicit_cli_arg_test.apply_cli_args(cli_args)
    if len(sweep_paths) == 0:
        run_trial(implicit_cli_arg_test)
        return
    implicit_cli_arg_test_sweep = sweep.ImplicitCLIArgTestSweep.from_yaml_files(sweep_paths)

    def objective(trial: optuna.Trial) -> typing.Union[
        float,
        typing.Sequence[float],
    ]:
        optuna_sampler = pgml.OptunaSampler(trial)
        implicit_cli_arg_test_patch = optuna_sampler.sample(implicit_cli_arg_test_sweep)
        implicit_cli_arg_test_patched = implicit_cli_arg_test.merge(implicit_cli_arg_test_patch)
        objective_value = run_trial(implicit_cli_arg_test_patched, trial)
        return objective_value

    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=100)


if __name__ == '__main__':
    app()
