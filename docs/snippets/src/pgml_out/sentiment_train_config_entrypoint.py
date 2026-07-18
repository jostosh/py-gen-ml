import pgml_out.sentiment_demo_base as base
import pgml_out.sentiment_demo_sweep as sweep
import pgml_out.sentiment_demo_cli_args as cli_args
import typer
import py_gen_ml as pgml
import optuna
import typing

app = typer.Typer(pretty_exceptions_enable=False)

def run_trial(
    sentiment_train_config: base.SentimentTrainConfig,
    trial: typing.Optional[optuna.Trial] = None
) -> typing.Union[float, typing.Sequence[float]]:
    """
    Run a trial with the given values for sentiment_train_config. The sampled
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
    cli_args: cli_args.SentimentTrainConfigArgs = typer.Option(...),
) -> None:
    sentiment_train_config = base.SentimentTrainConfig.from_yaml_files(config_paths)
    sentiment_train_config = sentiment_train_config.apply_cli_args(cli_args)
    if len(sweep_paths) == 0:
        run_trial(sentiment_train_config)
        return
    sentiment_train_config_sweep = sweep.SentimentTrainConfigSweep.from_yaml_files(sweep_paths)

    def objective(trial: optuna.Trial) -> typing.Union[
        float,
        typing.Sequence[float]
    ]:
        optuna_sampler = pgml.OptunaSampler(trial)
        sentiment_train_config_patch = optuna_sampler.sample(sentiment_train_config_sweep)
        sentiment_train_config_patched = sentiment_train_config.merge(sentiment_train_config_patch)
        objective_value = run_trial(sentiment_train_config_patched, trial)
        return objective_value

    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=100)


if __name__ == "__main__":
    app()