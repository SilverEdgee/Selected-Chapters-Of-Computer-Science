import csv
import pickle

from models import Student
from abc import ABC, abstractmethod
from typing import List


class Storage(ABC):
    """Abstract base class for storage objects."""
    @abstractmethod
    def load(self, path: str) -> List[Student]:
        pass

    @abstractmethod
    def save(self, path: str, students: List[Student]):
        pass

class CsvStorage(Storage):
    """Class for CSV storage."""

    def load(self, path: str) -> List[Student]:
        with open(path, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            return [Student.from_dict(row) for row in reader]

    def save(self, path: str, students: List[Student]):
        with open(path, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["surname", "age"])
            writer.writeheader()
            for s in students:
                writer.writerow(s.to_dict())


class PickleStorage(Storage):
    """Class for pickle storage."""

    def load(self, path: str) -> List[Student]:
        with open(path, "rb") as pf:
            pickled = pickle.load(pf)
            return pickled

    def save(self, path: str, students: List[Student]):
        with open(path, "wb") as pf:
            pickle.dump(list(students), pf)




