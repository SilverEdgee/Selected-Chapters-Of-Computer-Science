"""
Module for calculation arcsin(x).
Lab Work №3
Name: Standard data types, collections, functions, modules
Version: v1.0
Author: Pometko D. I.
Created: 16-03-2026
"""
from typing import Iterable, Tuple
from validation import validate_x
from math import asin
def term_calculate_generator(x: float) -> Iterable[float]:
    """
    Generator function to calculate terms of arcsin(x) expression.
    Args:
        x (float): Value of x.
    Yields:
        float: Terms of arcsin(x) expression.
    """
    n = 0
    term = x
    while True:
        yield term
        n += 1
        term *= ((2 * n - 1) ** 2) * x * x / (2 * n * (2 * n + 1))

@validate_x
def calculate_arcsin(x: float, eps: float, max_iter: int = 500) -> Tuple[float, int, float, float, float]:
    """
    Function to calculate arcsin(x) expression.
    Args:
        x (float): Value of x.
        eps (float): Precision of calculation.
        max_iter (int): Maximum number of iterations.
    Returns:
        Tuple[float, int, float, float, float]: x value, number of iterations, calculated value, math value, precision.
     Raises:
        ValueError: Maximum number of iterations reached.
    """
    result = 0.0
    math_result = asin(x)
    for n, term in enumerate(term_calculate_generator(x), 1):
        result += term
        if abs(result - math_result) < eps:
            return x, n, result, math_result, eps
        if n >= max_iter:
            break

    raise ValueError(f"Maximum number of iterations reached ({max_iter}).")

