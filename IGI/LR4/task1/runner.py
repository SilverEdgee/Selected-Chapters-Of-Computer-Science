"""
Lab 4, Task 1 — Interactive CLI for student registry (variant 22).
"""

from __future__ import annotations
from pathlib import Path

from models import Student
from storage import CsvStorage, PickleStorage
from registry import Registry

_CSV_PATH    = Path("data/students.csv")
_PICKLE_PATH = Path("data/students.pkl")

_SAMPLE_DATA: list[Student] = [
    Student("Ivanov",    14),
    Student("Petrova",   11),
    Student("Sidorov",   17),
    Student("Kozlova",   8),
    Student("Morozov",   15),
    Student("Volkova",   12),
    Student("Novikov",   9),
    Student("Sokolova",  16),
    Student("Popov",     13),
    Student("Lebedev",   18),
]


def _prompt_int(prompt: str, lo: int, hi: int) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
            if lo <= value <= hi:
                return value
            print(f"  ✗  Enter a number between {lo} and {hi}.")
        except ValueError:
            print("  ✗  That is not a valid integer.")


def _prompt_str(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("  ✗  Input must not be empty.")


def _print_students(students: list[Student], indent: int = 4) -> None:
    pad = " " * indent
    for s in students:
        print(f"{pad}{s.surname:<20} age={s.age:<3} group={s.get_age_group()}")


def _load_data(use_pickle: bool) -> list[Student]:
    path = _PICKLE_PATH if use_pickle else _CSV_PATH
    loader = PickleStorage().load if use_pickle else CsvStorage().load
    if not path.exists():
        print("  → No saved data found; loading sample dataset.")
        students = list(_SAMPLE_DATA)
        (PickleStorage().save if use_pickle else CsvStorage().save)(str(path), students)
        return students
    return loader(path)


def run() -> None:
    """Entry point for task 1 interactive session."""
    print("\n" + "═" * 55)
    print("  Lab 4 · Task 1 · Student Age-Group Registry  (var 22)")
    print("═" * 55)

    fmt_choice = _prompt_int(
        "  Select storage format:\n"
        "    1 — CSV\n"
        "    2 — Pickle\n"
        "  Your choice: ",
        1, 2,
    )
    use_pickle = fmt_choice == 2
    students = _load_data(use_pickle)

    while True:
        print("\n  Menu:")
        print("    1  Show all students (sorted by age)")
        print("    2  Show age groups")
        print("    3  Search by surname")
        print("    4  Add student")
        print("    5  Save and exit")

        choice = _prompt_int("  Your choice: ", 1, 5)

        if choice == 1:
            print()
            _print_students(Registry.sort_by_age(students))

        elif choice == 2:
            groups = Registry.group_by_age(students)
            for group_name, members in sorted(groups.items()):
                print(f"\n  [{group_name.upper()}]")
                _print_students(members)

        elif choice == 3:
            surname = _prompt_str("  Enter surname: ")
            found = Registry.search(students, surname)
            if found:
                print()
                _print_students(found)
            else:
                print(f"  No student named '{surname}' found.")

        elif choice == 4:
            surname = _prompt_str("  Surname: ")
            age = _prompt_int("  Age [6–18]: ", 6, 18)
            try:
                students.append(Student(surname, age))
                print("  ✓ Student added.")
            except ValueError as exc:
                print(f"  ✗ {exc}")

        elif choice == 5:
            path   = _PICKLE_PATH if use_pickle else _CSV_PATH
            saver  = PickleStorage().save  if use_pickle else CsvStorage().save
            saver(str(path), students)
            print(f"  ✓ Data saved to '{path}'.")
            break

if __name__ == "__main__":
    run()