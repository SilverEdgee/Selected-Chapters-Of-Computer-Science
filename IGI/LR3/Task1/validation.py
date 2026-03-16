"""
Module for validation  of input data.
Lab Work №3
Name: Standard data types, collections, functions, modules
Version: v1.0
Author: Pometko D. I.
Created: 16-03-2026
"""
from functools import wraps
from typing import Callable

def validate_x(func: Callable) -> Callable:
    """
    Function decorator for validation of input data.
    Args:
        func (Callable): Function to validate.
    Returns;
        Callable: Validated function.
    Raises:
        ValueError: Invalid input.
    """
    @wraps(func)
    def wrapper(x: float, eps: float, max_iter: int = 500):
        if abs(x) >= 1:
            raise ValueError("x must satisfy |x| < 1.")
        if eps <= 0:
            raise ValueError("eps must be greater than 0.")
        if not isinstance(max_iter, int) or max_iter <= 0:
            raise ValueError("max_iter must be a positive integer.")
        return func(x, eps, max_iter)
    return wrapper



