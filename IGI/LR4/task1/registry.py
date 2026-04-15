from models import Student


class Registry:
    """Class for age-group breakdown, search, sort"""

    @staticmethod
    def group_by_age(students: list[Student]) -> dict[str, list[Student]]:
        "Partition students into named age groups"
        groups: dict[str, list[Student]] = {}
        for s in students:
            groups.setdefault(s.get_age_group(), []).append(s)
        return groups

    @staticmethod
    def search(students: list[Student], surname: str) -> list[Student]:
        """Returns students whose surname matches"""
        query = surname.strip().lower()
        return [s for s in students if s.surname.lower() == query]

    @staticmethod
    def sort_by_age(students: list[Student], *, reverse: bool = False) -> list[Student]:
        """Return a new list sorted by age."""
        return sorted(students, reverse=reverse)


