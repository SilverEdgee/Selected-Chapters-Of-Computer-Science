"""
Program to calculate arcsin(x) expression.
Lab Work №3
Name: Standard data types, collections, functions, modules
Version: v1.0
Author: Pometko D. I.
Created: 16-03-2026
"""
from calculation import calculate_arcsin
from user_interface import display_results_table, get_float_input, get_yes_no_input

def main():
    while True:
        x = get_float_input("Enter x (|x| < 1): ", min_val=-1.0, max_val=1.0)
        eps = get_float_input("Enter epsilon (> 0): ", min_val=0.0)

        try:
            results = calculate_arcsin(x, eps, max_iter=500)
            display_results_table(results)
        except ValueError as error:
            print(f"Error: {error}")

        if not get_yes_no_input("Want to continue? [y/n]: "):
            break

if __name__ == "__main__":
    main()
