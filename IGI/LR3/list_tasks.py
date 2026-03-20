"""
Lab Work #3: Standard Data Types, Collections, Functions, Modules
Module: list_tasks.py
Description: List processing task (Task 5) — count elements > C,
             product of elements before the max-absolute-value element.
Version: 1.0
Developer: Student, Variant 22
Date: 20-03-2026
"""

from utils import get_float_input


def task5a_count_greater_than_c(lst: list, c: float) -> int:
    """
    Count elements in the list that are greater than C.

    Args:
        lst (list): List of real numbers.
        c (float): Threshold value.

    Returns:
        int: Number of elements strictly greater than c.
    """
    return sum(1 for x in lst if x > c)


def task5b_product_before_max_abs(lst: list):
    """
    Find the product of all elements located
    before the element with the maximum absolute value.
    If that element is at index 0, the product is 1 (empty product).

    Args:
        lst (list): List of real numbers.

    Returns:
        tuple: (product: float, max_abs_index: int)

    Raises:
        ValueError: If the list is empty.
    """
    if not lst:
        raise ValueError("List is empty.")

    max_abs_idx = max(range(len(lst)), key=lambda k: abs(lst[k]))

    product = 1.0
    for i in range(max_abs_idx):
        product *= lst[i]

    return product, max_abs_idx


def task5_list_processing(lst: list) -> None:
    """
    Display the list, ask for threshold C, then run
    both sub-tasks and print results.

    Args:
        lst (list): The list of real numbers to process.
    """
    if not lst:
        print("  The list is empty.")
        return

    print(f"\n  List ({len(lst)} elements): {lst}\n")

    c = get_float_input("  Enter threshold C: ")

    count = task5a_count_greater_than_c(lst, c)
    print(f"\n  a) Elements greater than {c}: {count}")

    try:
        product, idx = task5b_product_before_max_abs(lst)
        max_elem = lst[idx]
        print(f"  b) Max |element| = {max_elem} at index {idx}")
        if idx == 0:
            print("     No elements before it — product = 1 (empty product)")
        else:
            elems_before = lst[:idx]
            print(f"     Elements before it: {elems_before}")
            print(f"     Product = {product:.6f}")
    except ValueError as e:
        print(f"  Error: {e}")