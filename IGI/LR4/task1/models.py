from typing import ClassVar

class AgeMixin:
    """Mixin that adds age classification"""

    AGE_GROUPS: ClassVar[dict[str, tuple[int, int]]] = {
        "junior": (6, 10),
        "middle": (11, 13),
        "senior": (14, 17),
        "graduate": (18, 99),
    }

    def get_age_group(self):
        age = getattr(self, "age")
        for label, (lo, hi) in self.AGE_GROUPS.items():
            if lo <= age <= hi:
                return label
        return "Unknown"


class Person:
    """Base class for student with surname and age"""
    def __init__(self, surname: str, age: int):
        self._surname = surname
        self._age = age

    @property
    def surname(self):
        return self._surname
    @surname.setter
    def surname(self, new_surname: str):
        self._surname = new_surname

    @property
    def age(self):
        return self._age
    @age.setter
    def age(self, new_age: int):
        self._age = new_age

    def __str__(self):
        return self.surname

class Student(Person, AgeMixin):
    """School student"""

    institution: ClassVar[str] = "School"

    def __init__(self, surname: str, age: int):
        super().__init__(surname, age)

    def __lt__(self, other):
        return self.age < other.age

    def __eq__(self, other):
        return self.age == other.age and self.surname == other.surname

    def to_dict(self) -> dict[str, str | int]:
        return {"surname": self.surname, "age": self.age}

    @classmethod
    def from_dict(cls, student: dict[str, str | int]):
        return cls(student["surname"], int(student["age"]))