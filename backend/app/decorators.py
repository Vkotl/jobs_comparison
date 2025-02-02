"""Module with decorators."""
from functools import wraps
from typing import Callable

from .constants import BAD_DATE_FORMAT_ERROR


def date_verification(func: Callable) -> Callable:
    """Verify that the date format is correct."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> dict:
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            print(e)
            if 'not match format' in str(e):
                return {'error': BAD_DATE_FORMAT_ERROR}
            else:
                raise e
    return wrapper
