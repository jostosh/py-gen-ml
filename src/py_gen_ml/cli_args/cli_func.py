import inspect
from typing import Any, Callable, Dict, Optional, Union

import typer
import typer.core
import typer.models
from pydantic import BaseModel

from py_gen_ml.typing.some import some


def pgml_cmd(
    app: typer.Typer,
    name: Optional[str] = None,
    *,
    cls: Optional[type[typer.core.TyperCommand]] = None,
    context_settings: Optional[Dict[Any, Any]] = None,
    help: Optional[str] = None,
    epilog: Optional[str] = None,
    short_help: Optional[str] = None,
    options_metavar: str = '[OPTIONS]',
    add_help_option: bool = True,
    no_args_is_help: bool = False,
    hidden: bool = False,
    deprecated: bool = False,
    rich_help_panel: Union[str, None] = typer.models.Default(None),
) -> Callable[[Callable[..., Any]], None]:
    """
    Decorator to create a Typer command from a function.

    This decorator creates a Typer command from a given function. It expects
    at least one parameter that is a Pydantic model. This model is used to
    parse command-line arguments.

    Other parameters are passed to the function as-is.

    Args:
        app (typer.Typer): The Typer app to add the command to.
        name (Optional[str]): The name of the command.
        cls (Optional[type[typer.core.TyperCommand]]): The Typer command class to use.
        context_settings (Optional[Dict[Any, Any]]): Context settings for the command.
        help (Optional[str]): The help text for the command.
        epilog (Optional[str]): The epilog text for the command.
        short_help (Optional[str]): The short help text for the command.
        options_metavar (str): The metavar for the options.
        add_help_option (bool): Whether to add a help option to the command.
        no_args_is_help (bool): When no arguments are provided, whether to show help.
        hidden (bool): Whether to hide the command from help messages.
        deprecated (bool): Whether to mark the command as deprecated.
        rich_help_panel (Union[str, None]): The rich help panel for the command.
    """

    def decorator(func: Callable[..., Any]) -> None:
        _command_from_func(
            app,
            func,
            name=name,
            cls=cls,
            context_settings=context_settings,
            help=help,
            epilog=epilog,
            short_help=short_help,
            options_metavar=options_metavar,
            add_help_option=add_help_option,
            no_args_is_help=no_args_is_help,
            hidden=hidden,
            deprecated=deprecated,
            rich_help_panel=rich_help_panel,
        )

    return decorator


def _command_from_func(
    app: typer.Typer,
    func: Callable[..., Any],
    name: Optional[str] = None,
    *,
    cls: Optional[type[typer.core.TyperCommand]] = None,
    context_settings: Optional[Dict[Any, Any]] = None,
    help: Optional[str] = None,
    epilog: Optional[str] = None,
    short_help: Optional[str] = None,
    options_metavar: str = '[OPTIONS]',
    add_help_option: bool = True,
    no_args_is_help: bool = False,
    hidden: bool = False,
    deprecated: bool = False,
    rich_help_panel: Union[str, None] = typer.models.Default(None),
) -> None:
    """
    Create a Typer command from a function.

    This function creates a Typer command from a given function. It expects
    at least one parameter that is a Pydantic model. This model is used to
    parse command-line arguments.

    Other parameters are passed to the function as-is.

    The function is then wrapped to accept both the Pydantic model and other
    arguments, allowing for a flexible command-line interface.

    Args:
        app (typer.Typer): The Typer app to add the command to.
        func (Callable[..., Any]): The function to create a command from.
        name (Optional[str]): The name of the command.
        cls (Optional[type[typer.core.TyperCommand]]): The Typer command class to use.
        context_settings (Optional[Dict[Any, Any]]): Context settings for the command.
        help (Optional[str]): The help text for the command.
        epilog (Optional[str]): The epilog text for the command.
        short_help (Optional[str]): The short help text for the command.
        options_metavar (str): The metavar for the options.
        add_help_option (bool): Whether to add a help option to the command.
        no_args_is_help (bool): When no arguments are provided, whether to show help.
        hidden (bool): Whether to hide the command from help messages.
        deprecated (bool): Whether to mark the command as deprecated.
        rich_help_panel (Union[str, None]): The rich help panel for the command.
    """
    func_sig = inspect.signature(func)

    # Find the Pydantic model parameter
    model_param_name = None
    model_class = None
    for param in func_sig.parameters.values():
        if not inspect.isclass(param.annotation) or not issubclass(param.annotation, BaseModel):
            continue
        if model_class is not None:
            raise ValueError('pgml_cmd supports only one base model')
        model_class = param.annotation
        model_param_name = param.name

    if model_class is None:
        raise ValueError('No Pydantic model found in function parameters')

    # Create a new function with combined parameters
    def command_fn(**kwargs: Any) -> None:
        # Extract arguments for the Pydantic model
        model_args = {k: v for k, v in kwargs.items() if k in model_class.model_fields}
        # Create an instance of the Pydantic model
        model_instance = model_class(**model_args)

        # Extract arguments for the function
        non_model_kwargs = {k: v for k, v in kwargs.items() if k in func_sig.parameters if k != model_param_name}
        func(**{some(model_param_name): model_instance, **non_model_kwargs})

    # Combine the parameters
    func_params = {k: v for k, v in func_sig.parameters.items() if k != model_param_name}
    combined_params = {**func_params, **model_class.__signature__.parameters}
    command_fn.__signature__ = inspect.Signature(list(combined_params.values()))  # type: ignore

    # Register the combined function with Typer
    app.command(
        name=name,
        cls=cls,
        context_settings=context_settings,
        help=help,
        epilog=epilog,
        short_help=short_help,
        options_metavar=options_metavar,
        add_help_option=add_help_option,
        no_args_is_help=no_args_is_help,
        hidden=hidden,
        deprecated=deprecated,
        rich_help_panel=rich_help_panel,
    )(command_fn)
