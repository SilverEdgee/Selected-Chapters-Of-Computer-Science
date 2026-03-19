"""
Program to calculate sum of cubes of input integers
Lab Work №3
Name: Standard data types, collections, functions, modules
Version: v1.0
Author: Pometko D. I.
Created: 19-03-2026
"""
from user_inteface import get_user_numbers
from cube_calculator import cube_calculate

def main():
    numbers = get_user_numbers()
    print("Result: ", cube_calculate(numbers))

if __name__ == "__main__":
    main()

