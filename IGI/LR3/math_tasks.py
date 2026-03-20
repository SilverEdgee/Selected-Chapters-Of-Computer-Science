"""
Lab Work #3: Standard Data Types, Collections, Functions, Modules
Module: math_tasks.py
Description: Mathematical tasks — power series (Task 1) and numeric loop (Task 2)
Version: 1.0
Developer: Pometko D.I., Variant 22
Date: 20-03-2026
"""

import math
from utils import get_float_input, get_int_input, timing_decorator


@timing_decorator
def task1_arcsin_series() -> None:
    """
    Task 1 (Variant 22): Compute arcsin(x) via power series expansion.
    Prints x, F(x), number of terms, and math.asin(x) for comparison.
    """
    while True:
        x = get_float_input("  Enter x (|x| < 1): ")
        if abs(x) < 1:
            break
        print(" |x| must be strictly less than 1. Try again.")

    eps = get_float_input("  Enter precision eps (e.g. 0.0001): ")
    if eps <= 0:
        eps = 1e-6
        print(f"eps must be positive. Using default eps = {eps}")

    MAX_ITER = 500
    total = 0.0
    term = x
    n = 0

    while n < MAX_ITER:
        total += term
        n += 1
        term *= (2 * n - 1) ** 2 * x * x / (2 * n * (2 * n + 1))
        if abs(term) < eps:
            total += term
            n += 1
            break

    math_val = math.asin(x)
    print(f"\n  {'x':>10} | {'F(x) series':>15} | {'n terms':>8} | {'math.asin(x)':>15}")
    print("  " + "-" * 55)
    print(f"  {x:>10.6f} | {total:>15.8f} | {n:>8} | {math_val:>15.8f}")


def task2_sum_of_cubes() -> None:
    """
    Task 2 (Variant 22): Read integers from the user and accumulate their cubes.
    The loop terminates when the sentinel value 12 is entered.
    Prints the total sum of cubes and the count of numbers entered.
    """
    print("\n  Enter integers one by one. Enter 12 to stop.\n")

    total = 0
    count = 0

    while True:
        try:
            num = int(input("  Enter integer: "))
        except ValueError:
            print(" Not an integer, try again.")
            continue

        if num == 12:
            print("Number 12 received. Stopping.")
            break

        total += num ** 3
        count += 1
        print(f"      cube({num}) = {num ** 3},  running sum = {total}")

    print(f"\n  Numbers entered : {count}")
    print(f"  Sum of cubes    : {total}")