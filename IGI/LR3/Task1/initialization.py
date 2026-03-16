"""
Module for initialization of sequences
Lab Work №3
Name: Standard data types, collections, functions, modules
Version: v1.0
Author: Pometko D. I.
Created: 16-03-2026
"""
from typing import Iterable, Callable

def sequence_generator(n: int) -> Iterable[int]:
    """
    Generator function to generate a sequence of integers from 0 to n-1.
    Args:
        n (int): Number of integers to generate.
    Yields:
        int: Numbers from 0 to n-1.
    """
    for i in range(n):
        yield i

def initialize_with_generator(n: int, gen: Callable[[int], Iterable[int]]) -> list:
    """
    Initializes sequence using generator
    Args:
        n: Number of integers to generate.
        gen (Callable[[int], Iterable[int]]): Generator function to generate the sequence.
    Returns:
        list: Sequence of integers from 0 to n-1.
    """
    return list(gen(n))

def initialize_with_user_input(n: int) -> list:
    """
    Initializes sequence with user input
    Args:
        n (int): Number of integers to generate.
    Returns:
        list: Sequence of integers from 0 to n-1.
    Raises:
        ValueError: Invalid input.
    """
    seq = []
    for i in range(n):
        while True:
            try:
                seq.append(float(input(f"Enter {i + 1} number: ")))
                break
            except ValueError:
                print("Invalid number. Try again.")
    return seq






