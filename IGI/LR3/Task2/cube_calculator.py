"""
Module for cube calculation.
Lab Work №3
Name: Standard data types, collections, functions, modules
Version: v1.0
Author: Pometko D. I.
Created: 16-03-2026
"""

def cube_calculate(numbers: list) -> int:
    """
    Calculate sum of cubes of numbers.
    Args:
        numbers (list): List of numbers.
    Returns:
        int: Sum of cubes of numbers.
    """
    result = 0
    for number in numbers:
        result += number ** 3
    return result

