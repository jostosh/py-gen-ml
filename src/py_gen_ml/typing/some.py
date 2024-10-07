from typing import TypeVar

T = TypeVar('T')


def some(value: T | None) -> T:
    """
    Get the value if it is not None.

    Args:
        value (T | None): The value to get.

    Raises:
        ValueError: If the value is None.

    Returns:
        T: The value.
    """
    if value is None:
        raise ValueError('Value is None')
    return value
