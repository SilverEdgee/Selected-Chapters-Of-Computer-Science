"""
Lab Work #3: Standard Data Types, Collections, Functions, Modules
Module: init_module.py
Description: Functions for initializing sequences — generator-based and user input.
             Kept in a separate module as required by task condition 9.
Version: 1.0
Developer: Pometko D.I., Variant 22
Date: 20-03-2026
"""

import random


def init_by_generator(sequence: list, n: int, low: float = -10.0, high: float = 10.0) -> list:
    """
    Initialize a sequence with random float values using a generator function.

    Args:
        sequence (list): The list to fill.
        n (int): Number of elements to generate.
        low (float): Lower bound for random values.
        high (float): Upper bound for random values.

    Returns:
        list: The filled sequence.
    """
    def random_float_generator(count, lo, hi):
        """Yield 'count' random floats in [lo, hi]."""
        for _ in range(count):
            yield round(random.uniform(lo, hi), 2)

    sequence.clear()
    sequence.extend(random_float_generator(n, low, high))
    return sequence


def init_by_user(sequence: list, n: int) -> list:
    """
    Initialize a sequence by reading float values from the user.

    Args:
        sequence (list): The list to fill.
        n (int): Number of elements to read.

    Returns:
        list: The filled sequence.
    """
    sequence.clear()
    print(f"  Enter {n} real numbers:")
    for i in range(n):
        while True:
            try:
                val = float(input(f"    element[{i}]: "))
                sequence.append(val)
                break
            except ValueError:
                print("   Invalid input. Please enter a real number.")
    return sequence