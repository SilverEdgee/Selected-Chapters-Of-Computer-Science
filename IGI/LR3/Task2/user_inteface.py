"""
Module for user interface of the program.
Lab Work №3
Name: Standard data types, collections, functions, modules
Version: v1.0
Author: Pometko D. I.
Created: 16-03-2026
"""
from typing import Iterable

def get_user_numbers() -> list:
    """
    Function to get user numbers.
    Returns:
        number_list: List of user numbers.
    """
    number_list = []
    number = None

    while True:
        try:
            number = int(input("Enter a number: "))
            if number == 12:
                break
            number_list.append(number)
        except ValueError:
            print("Invalid input. Please try again.")
    return number_list

def get_numbers_generator() -> Iterable[int]:
    """
    Function to get user numbers using generator.
    Yields:
        number: User number.
    """
    number = None
    number_list = []
    while number != 12:
        try:
            number = int(input("Enter a number: "))
            yield number
        except ValueError:
            print("Invalid input. Please try again.")
        generator_numbers_to_list(number)


def generator_numbers_to_list(number: int) -> list:
    """
    Function to make a list of user numbers.
    Args:
        number: User number.
    Returns:
        number_list: List of user numbers.
    """
    number_list = []
    if number != 12:
        number_list.append(number)
    return number_list