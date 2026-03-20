"""
Lab Work #3: Standard Data Types, Collections, Functions, Modules
Module: main.py  (entry point)
Description: Main menu. Imports and tests all task modules.
Version: 1.0
Developer: Pometko D.I., Variant 22
Date: 20-03-2026
"""

from math_tasks   import task1_arcsin_series, task2_sum_of_cubes
from string_tasks import task3_binary_check, task4_text_analysis
from list_tasks   import task5_list_processing

from init_module  import init_by_generator, init_by_user
from utils        import get_int_input, ask_repeat, print_header, print_separator

MENU = {
    1: "Task 1 — arcsin(x) via power series",
    2: "Task 2 — Sum of cubes (stop at 12)",
    3: "Task 3 — Binary number check",
    4: "Task 4 — Text analysis",
    5: "Task 5 — List processing",
}

def print_menu() -> None:
    """Print the main application menu."""
    print_header("LAB WORK #3  |  Variant 22")
    for num, desc in MENU.items():
        print(f"  [{num}] {desc}")
    print("  [0] Exit")
    print_separator()


def _init_list() -> list:
    """
    Ask the user how to initialise the list for Task 5, then return it.

    Returns:
        list: Initialised list of real numbers.
    """
    print_separator()
    print("  Initialisation method:")
    print("  [1] Random generator")
    print("  [2] Manual input")
    choice = get_int_input("  Your choice: ", min_val=1, max_val=2)
    n = get_int_input("  List size (1–50): ", min_val=1, max_val=50)

    lst = []
    if choice == 1:
        init_by_generator(lst, n)
        print(f"  Generated: {lst}")
    else:
        init_by_user(lst, n)
    return lst


def run_task1() -> None:
    """Run Task 1 with repeat support."""
    while True:
        print_header("TASK 1 — arcsin(x) Power Series")
        task1_arcsin_series()
        if not ask_repeat():
            break


def run_task2() -> None:
    """Run Task 2 with repeat support."""
    while True:
        print_header("TASK 2 — Sum of Cubes")
        task2_sum_of_cubes()
        if not ask_repeat():
            break


def run_task3() -> None:
    """Run Task 3 with repeat support."""
    while True:
        print_header("TASK 3 — Binary Number Check")
        task3_binary_check()
        if not ask_repeat():
            break


def run_task4() -> None:
    """Run Task 4 (text is fixed, no repeat needed)."""
    print_header("TASK 4 — Text Analysis")
    task4_text_analysis()
    input("\n  Press Enter to return to menu...")


def run_task5() -> None:
    """Run Task 5 with repeat support; list is re-initialised each time."""
    while True:
        print_header("TASK 5 — List Processing")
        lst = _init_list()
        task5_list_processing(lst)
        if not ask_repeat():
            break


_RUNNERS = {1: run_task1, 2: run_task2, 3: run_task3, 4: run_task4, 5: run_task5}


def main() -> None:
    """Main loop: show menu, dispatch selected task, exit on 0."""
    print("\n  Welcome to Lab Work #3, Variant 22!")
    while True:
        print()
        print_menu()
        choice = get_int_input("  Your choice (0–5): ", min_val=0, max_val=5)
        if choice == 0:
            break
        _RUNNERS[choice]()


if __name__ == "__main__":
    main()