from typing import Any

import optuna
from pydantic import BaseModel

from py_gen_ml.sweep.sweep import (
    Choice,
    FloatLogUniform,
    FloatUniform,
    IntUniform,
    NestedChoice,
    Sweeper,
    SweepModel,
    SweepSampler,
    SweepSamplerContext,
    TBaseModel,
    TScalar,
    TSweep,
)


class OptunaSampler(SweepSampler):
    """
    A sampler that uses Optuna for hyperparameter optimization.

    Args:
        trial (optuna.Trial): The optuna trial to use for hyperparameter optimization.
    """

    def __init__(self, trial: optuna.Trial) -> None:
        """
        Initialize the OptunaSampler.

        Args:
            trial (optuna.Trial): The optuna trial to use for hyperparameter optimization.
        """
        self._trial = trial

    def visit_float_log_uniform(self, log_uniform: FloatLogUniform, context: SweepSamplerContext) -> float:
        """
        Visit a float log uniform and resolve its value.

        Args:
            log_uniform (FloatLogUniform): The float log uniform to visit.
            context (SweepSamplerContext): The context for the sweep sampler.

        Returns:
            float: The resolved value.
        """
        return self._trial.suggest_float(
            name=context.path,
            low=log_uniform.log_low,
            high=log_uniform.log_high,
            log=True,
        )

    def visit_int_uniform(self, uniform: IntUniform, context: SweepSamplerContext) -> int:
        """
        Visit an int uniform and resolve its value.

        Args:
            uniform (IntUniform): The int uniform to visit.
            context (SweepSamplerContext): The context for the sweep sampler.

        Returns:
            int: The resolved value.
        """
        return self._trial.suggest_int(
            name=context.path,
            low=uniform.low,
            high=uniform.high,
            step=uniform.step,
        )

    def visit_float_uniform(self, uniform: FloatUniform, context: SweepSamplerContext) -> float:
        """
        Visit a float uniform and resolve its value.

        Args:
            uniform (FloatUniform): The float uniform to visit.
            context (SweepSamplerContext): The context for the sweep sampler.

        Returns:
            float: The resolved value.
        """
        return self._trial.suggest_float(
            name=context.path,
            low=uniform.low,
            high=uniform.high,
            step=uniform.step,
        )

    def visit_nested_choice(
        self,
        sweep_choice: NestedChoice[TSweep, TBaseModel],
        context: SweepSamplerContext,
    ) -> TBaseModel:
        """
        Visit a nested choice and resolve its value.

        Args:
            sweep_choice (NestedChoice[TSweep, TBaseModel]): The nested choice to visit.
            context (SweepSamplerContext): The context for the sweep sampler.

        Returns:
            TBaseModel: The resolved base model.
        """
        random_choice = self._trial.suggest_categorical(
            name=context.path,
            choices=list(sweep_choice.nested_options.keys()),
        )
        value = sweep_choice.nested_options[random_choice]
        return value.accept(self, context=context)  # type: ignore

    def visit_choice(self, choice: Choice[TScalar], context: SweepSamplerContext) -> TScalar:
        """
        Visit a choice and resolve its value.

        Args:
            choice (Choice[TScalar]): The choice to visit.
            context (SweepSamplerContext): The context for the sweep sampler.

        Returns:
            TScalar: The resolved value.
        """
        return self._trial.suggest_categorical(  # type: ignore
            name=context.path,
            choices=choice.options,  # type: ignore
        )

    def visit_sweep_model(self, sweep_model: Sweeper[TBaseModel], context: SweepSamplerContext) -> BaseModel:
        """
        Visit a sweep model and resolve its fields.

        Args:
            sweep_model (Sweeper[TBaseModel]): The sweep model to visit.
            context (SweepSamplerContext): The context for the sweep sampler.

        Returns:
            BaseModel: The resolved base model.
        """
        kwargs = dict[str, Any]()
        for field_name in sweep_model.model_fields.keys():
            field_value = getattr(sweep_model, field_name)
            if isinstance(field_value, SweepModel):
                kwargs[field_name] = field_value.accept(self, context=context.step(field_name))
            elif isinstance(field_value, list):
                resolved_list = []
                for index, item in enumerate(field_value):
                    if isinstance(item, SweepModel):
                        resolved_list.append(item.accept(self, context=context.step(field_name, index=index)))
                    else:
                        raise ValueError(f'SweepModel field {field_name} is not a Node')
            else:
                kwargs[field_name] = field_value
        return sweep_model.new_base_model(**kwargs)
