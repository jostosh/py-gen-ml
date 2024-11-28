from __future__ import annotations

import abc
from dataclasses import dataclass
from dataclasses import replace as dataclass_replace
from typing import Any, Dict, Generic, List, Literal, Optional, TypeVar, Union

from pydantic import BaseModel

from py_gen_ml.yaml.yaml_model import YamlBaseModel

T = TypeVar('T')
Tb = TypeVar('Tb')
TScalar = TypeVar('TScalar', float, int, bool, str, bytes)
TBaseModel = TypeVar('TBaseModel', bound=BaseModel)


@dataclass
class SweepSamplerContext(Generic[T]):
    """A context for a sweep sampler."""

    path_parts: List[str]
    """The path parts of the sweep sampler context."""

    ctx: T
    """The context of the sweep sampler."""

    def step(self, name: str, index: Optional[int] = None) -> SweepSamplerContext[T]:
        """
        Step into a nested object.

        Args:
            name (str): The name of the object.
            index (Optional[int]): The index of the object.

        Returns:
            SweepSamplerContext: The context with the step.
        """
        if index is not None:
            name = f'{name}[{index}]'
        return dataclass_replace(self, path_parts=[*self.path_parts, name])

    @property
    def path(self) -> str:
        """
        Get the path to the current object.

        Returns:
            str: The path to the current object.
        """
        return '.'.join(self.path_parts)


class SweepModel(YamlBaseModel, Generic[T], abc.ABC):
    """
    A sweep model.

    This is a pydantic base model that defines sweeps for its fields.
    """

    @abc.abstractmethod
    def accept(self, visitor: SweepVisitor[Tb], context: SweepSamplerContext[Tb]) -> T:
        """
        Accept a visitor.

        Args:
            visitor (SweepVisitor[Tb]): The visitor to accept.
            context (SweepSamplerContext[Tb]): The context to use for the visitor.

        Returns:
            T: The result of the visitor.
        """


class SweepVisitor(abc.ABC, Generic[T]):
    """
    A sweep sampler.

    Defines a visitor pattern for sampling a model from a sweep configuration.
    """

    @abc.abstractmethod
    def visit_float_log_uniform(self, log_uniform: FloatLogUniform, context: SweepSamplerContext[T]) -> float:
        """
        Visit a float log uniform.

        Args:
            log_uniform (FloatLogUniform): The float log uniform to visit.
            context (SweepSamplerContext): The context to use for the visitor.

        Returns:
            float: The sampled float.
        """

    @abc.abstractmethod
    def visit_int_uniform(self, uniform: IntUniform, context: SweepSamplerContext[T]) -> int:
        """
        Visit an int uniform.

        Args:
            uniform (IntUniform): The int uniform to visit.
            context (SweepSamplerContext): The context to use for the visitor.

        Returns:
            int: The sampled int.
        """

    @abc.abstractmethod
    def visit_float_uniform(self, uniform: FloatUniform, context: SweepSamplerContext[T]) -> float:
        """
        Visit a float uniform.

        Args:
            uniform (FloatUniform): The float uniform to visit.
            context (SweepSamplerContext): The context to use for the visitor.

        Returns:
            float: The sampled float.
        """

    @abc.abstractmethod
    def visit_sweep_model(self, sweep_model: Sweeper[TBaseModel], context: SweepSamplerContext[T]) -> TBaseModel:
        """
        Visit a sweep model.

        Args:
            sweep_model (Sweeper[TBaseModel]): The sweep model to visit.
            context (SweepSamplerContext): The context to use for the visitor.

        Returns:
            TBaseModel: The sampled model.
        """

    @abc.abstractmethod
    def visit_nested_choice(
        self,
        sweep_choice: NestedChoice[TSweep, TBaseModel],
        context: SweepSamplerContext[T],
    ) -> TBaseModel:
        """
        Visit a nested choice.

        Args:
            sweep_choice (NestedChoice[TSweep, TBaseModel]): The nested choice to visit.
            context (SweepSamplerContext): The context to use for the visitor.

        Returns:
            TBaseModel: The sampled model.
        """

    @abc.abstractmethod
    def visit_choice(self, choice: Choice[TScalar], context: SweepSamplerContext[T]) -> TScalar:
        """
        Visit a choice.

        Args:
            choice (Choice[TScalar]): The choice to visit.
            context (SweepSamplerContext): The context to use for the visitor.

        Returns:
            TScalar: The sampled value.
        """


class SweepSampler(abc.ABC, Generic[TBaseModel]):
    """
    A sweep sampler.

    Defines a visitor pattern for sampling a model from a sweep configuration.
    """

    @abc.abstractmethod
    def sample(self, sweep_model: Sweeper[TBaseModel]) -> TBaseModel:
        """
        Sample a model.

        The sample should be a patch that is then applied to the corresponding base model.

        Args:
            sweep_model (Sweeper[TBaseModel]): The model to sample.

        Returns:
            TBaseModel: The sampled model.
        """


class Sweeper(SweepModel[TBaseModel]):
    """
    A sweeper.

    Sweepers allow for sampling a model from a set of options.
    """

    def accept(self, visitor: SweepVisitor[T], context: SweepSamplerContext[T]) -> TBaseModel:
        """
        Accept a visitor.

        Args:
            visitor (SweepVisitor[T]): The visitor to accept.
            context (SweepSamplerContext[T]): The context to use for the visitor.

        Returns:
            TBaseModel: The sampled model.
        """
        return visitor.visit_sweep_model(self, context)

    def new_base_model(self, **kwargs: Any) -> TBaseModel:
        """
        Create a new base model.

        Args:
            kwargs (Any): The keyword arguments to pass to the base model.

        Returns:
            TBaseModel: The new base model.
        """
        return self._get_base_type_from_generic_arg()(**kwargs)

    @classmethod
    def _get_base_type_from_generic_arg(cls) -> type[TBaseModel]:
        return cls.__bases__[0].__pydantic_generic_metadata__['args'][0]


class FloatLogUniform(SweepModel[float]):
    """
    A float log uniform.

    Float log uniforms allow for sampling a float value within a logarithmic range.
    """

    log_low: float
    log_high: float

    def accept(self, visitor: SweepVisitor[T], context: SweepSamplerContext[T]) -> float:
        """
        Visit a float log uniform.

        Args:
            visitor (SweepVisitor[T]): The visitor to accept.
            context (SweepSamplerContext[T]): The context to use for the visitor.

        Returns:
            float: The sampled float.
        """
        return visitor.visit_float_log_uniform(self, context=context)


class IntUniform(SweepModel[int]):
    """
    An int uniform.

    Int uniforms allow for sampling an int value within a range.
    """

    low: int
    high: int
    step: int = 1

    def accept(self, visitor: SweepVisitor[T], context: SweepSamplerContext[T]) -> int:
        """
        Visit an int uniform.

        Args:
            visitor (SweepVisitor[T]): The visitor to accept.
            context (SweepSamplerContext[T]): The context to use for the visitor.

        Returns:
            int: The sampled int.
        """
        return visitor.visit_int_uniform(self, context=context)


class FloatUniform(SweepModel[float]):
    """
    A float uniform.

    Float uniforms allow for sampling a float value within a range.
    """

    low: float
    high: float
    step: Optional[float] = None

    def accept(self, visitor: SweepVisitor[T], context: SweepSamplerContext[T]) -> float:
        """
        Visit a float uniform.

        Args:
            visitor (SweepVisitor[T]): The visitor to accept.
            context (SweepSamplerContext[T]): The context to use for the visitor.

        Returns:
            float: The sampled float.
        """
        return visitor.visit_float_uniform(self, context=context)


# In fact we'd like to have a higher-kinded type here, but that's not possible in Python without resorting
# to external libraries. So we just use a generic type variable here.
TSweep = TypeVar('TSweep', bound=Sweeper[BaseModel])


class NestedChoice(SweepModel[TBaseModel], Generic[TSweep, TBaseModel]):
    """
    A nested choice.

    Nested choices allow for sampling from a set of options by name. The structures
    that are sampled again are also sweep models, so they can be nested arbitrarily
    deep.
    """

    nested_options: Dict[str, TSweep]

    def accept(self, visitor: SweepVisitor[T], context: SweepSamplerContext[T]) -> TBaseModel:
        """
        Visit a nested choice.

        Args:
            visitor (SweepVisitor[T]): The visitor to accept.
            context (SweepSamplerContext[T]): The context to use for the visitor.

        Returns:
            TBaseModel: The sampled model.
        """
        return visitor.visit_nested_choice(self, context=context)


class Choice(SweepModel[TScalar]):
    """
    A choice.

    Choices allow for sampling from a set of options.
    """

    options: list[TScalar]

    def accept(self, visitor: SweepVisitor[T], context: SweepSamplerContext[T]) -> TScalar:
        """
        Visit a choice.

        Args:
            visitor (SweepVisitor[T]): The visitor to accept.
            context (SweepSamplerContext[T]): The context to use for the visitor.

        Returns:
            TScalar: The sampled value.
        """
        return visitor.visit_choice(self, context=context)


IntSweep = Union[int, Choice[int], IntUniform]
FloatSweep = Union[float, Choice[float], FloatLogUniform, FloatUniform]
BoolSweep = Union[bool, Literal['any']]
StrSweep = Union[str, Choice[str]]
BytesSweep = Union[bytes, Choice[bytes]]
