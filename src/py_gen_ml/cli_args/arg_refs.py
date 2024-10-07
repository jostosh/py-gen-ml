import typing
from typing import NamedTuple

import pydantic

TBaseModel = typing.TypeVar('TBaseModel', bound=pydantic.BaseModel)


class ArgRef(NamedTuple):
    """A reference to an argument."""

    path: str
    """The path to the argument."""


def apply_args(model: TBaseModel, arg_ref_model: pydantic.BaseModel) -> TBaseModel:
    """
    Apply arguments from arg_ref_model to model.

    Args:
        model (TBaseModel): The model to apply the arguments to.
        arg_ref_model (pydantic.BaseModel): The model containing the arguments to apply.

    Returns:
        TBaseModel: The model with the applied arguments.
    """
    out = model.model_copy()
    for name, field_info in arg_ref_model.model_fields.items():
        # Find shortcuts and replace the values in the given model
        if any(isinstance(arg_ref := m, ArgRef) for m in getattr(field_info, 'metadata', [])):
            current = out
            *path_to_container, field_in_container = arg_ref.path.split('.')
            for part in path_to_container:
                current = getattr(current, part)
            value = getattr(arg_ref_model, name)
            if value is None:
                continue
            setattr(current, field_in_container, value)
        elif name in model.model_fields and (value := getattr(arg_ref_model, name)) is not None:
            setattr(out, name, value)

    return out
