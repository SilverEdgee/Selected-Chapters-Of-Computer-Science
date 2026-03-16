"""
Module for user interface of the program.
Lab Work №3
Name: Standard data types, collections, functions, modules
Version: v1.0
Author: Pometko D. I.
Created: 16-03-2026
"""
from typing import Tuple

def display_results_table(results: Tuple[float, int, float, float, float]) -> None:
    """
    Display the results of the table
    Args:
    results: The results of the table
    """
    x, n, result, math_result, eps = results
    print("+-----------+-----------+-----------+-----------+-----------+")
    print("|     x     |     n     |   F(x)    | Math F(x) |    eps    |")
    print("+-----------+-----------+-----------+-----------+-----------+")
    print(f"| {x:9.6f} | {n:9d} | {result:9.6f} | {math_result:9.6f} | {eps:9.6f} |")
    print("+-----------+-----------+-----------+-----------+-----------+")


def get_float_input(prompt: str, min_val: float = None, max_val: float = None) -> float:
    """
    Get validated float input from user.

    Args:
        prompt: Message to display
        min_val: Minimum allowed value (optional)
        max_val: Maximum allowed value (optional)

    Returns:
        float: Validated user input
    """
    while True:
        try:
            value = float(input(prompt))
            if min_val is not None and value <= min_val:
                print(f"Value must be greater than {min_val}")
                continue
            if max_val is not None and value >= max_val:
                print(f"Value must be less than {max_val}")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a number.")

def get_yes_no_input(prompt: str) -> bool:
    """
    Get validated yes/no input from user.

    Args:
        prompt: Message to display
    Returns:
        bool: Validated user input
    """
    while True:
        choice = input(prompt).strip().lower()
        if choice in ("y", "yes"):
            return True
        elif choice in ("n", "no"):
            return False
        print("Please enter yes or no")
