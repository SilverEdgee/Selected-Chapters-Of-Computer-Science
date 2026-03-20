"""
Lab Work #3: Standard Data Types, Collections, Functions, Modules
Module: utils.py
Description: Shared utility functions — input validation, repeat prompt,
             timing decorator, and display helpers.
Version: 1.0
Developer: Pometko D.I., Variant 22
Date: 20-03-2026
"""

import time
import functools


def get_float_input(prompt: str) -> float:
    """
    Safely read a float from the user, repeating on invalid input.
    Args:
        prompt (str): Message shown to the user.

    Returns:
        float: Valid float value.
    """
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a number.")


def get_int_input(prompt: str, min_val: int = None, max_val: int = None) -> int:
    """
    Safely read an integer from the user with optional range check.

    Args:
        prompt (str): Message shown to the user.
        min_val (int, optional): Minimum allowed value.
        max_val (int, optional): Maximum allowed value.

    Returns:
        int: Valid integer value.
    """
    while True:
        try:
            val = int(input(prompt))
            if min_val is not None and val < min_val:
                print(f"Value must be >= {min_val}.")
                continue
            if max_val is not None and val > max_val:
                print(f"Value must be <= {max_val}.")
                continue
            return val
        except ValueError:
            print("Invalid input. Please enter an integer.")


def ask_repeat() -> bool:
    """
    Ask the user whether to repeat the current task.

    Returns:
        bool: True to repeat, False to return to menu.
    """
    while True:
        answer = input("\n  Repeat this task? (y/n): ").strip().lower()
        if answer in ('y', 'yes'):
            return True
        if answer in ('n', 'no'):
            return False
        print("Please enter 'y' or 'n'.")


def timing_decorator(func):
    """
    Decorator: measures and prints the execution time of the wrapped function.

    Args:
        func: Function to wrap.

    Returns:
        wrapper: Wrapped function with timing output.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"Execution time: {elapsed:.6f} s")
        return result
    return wrapper


def print_separator(width: int = 55) -> None:
    """Print a horizontal line separator."""
    print("─" * width)


def print_header(title: str, width: int = 55) -> None:
    """
    Print a formatted section header between two separator lines.

    Args:
        title (str): Header text.
        width (int): Width of the separator lines.
    """
    print_separator(width)
    print(f"  {title}")
    print_separator(width)