"""
Lab 4, Task 5 — NumPy matrix operations (variant 22).

Task: find the smallest element on the anti-diagonal (побочная диагональ).
      Compute variance two ways:
        a) numpy.var()
        b) manual formula  Var = mean((x - mean)^2)
      Round results to 2 decimal places.


Variant 22 · Lab 4
Version: 1.0
"""

from __future__ import annotations
import abc
import numpy as np
from typing import ClassVar



class MatrixStatsMixin:
    """
    Mixin: statistical analysis of the full matrix.
    Reads self._data (np.ndarray) from the host class.
    """

    @property
    def _flat(self) -> np.ndarray:
        return self._data.flatten().astype(float)

    def stat_mean(self) -> float:
        """Mean of all elements via numpy.mean()."""
        return round(float(np.mean(self._flat)), 2)

    def stat_median(self) -> float:
        """Median of all elements via numpy.median()."""
        return round(float(np.median(self._flat)), 2)

    def stat_var(self) -> float:
        """Variance of all elements via numpy.var()."""
        return round(float(np.var(self._flat)), 2)

    def stat_std(self) -> float:
        """Standard deviation via numpy.std()."""
        return round(float(np.std(self._flat)), 2)

    def stat_corrcoef(self) -> float:
        """Correlation coefficient between first and second halves of elements."""
        flat = self._flat
        half = len(flat) // 2
        if half < 2:
            return float("nan")
        return round(float(np.corrcoef(flat[:half], flat[half: 2 * half])[0, 1]), 4)

    def statistics(self) -> dict[str, float]:
        return {
            "mean":             self.stat_mean(),
            "median":           self.stat_median(),
            "variance (numpy)": self.stat_var(),
            "std_dev (numpy)":  self.stat_std(),
            "corrcoef_halves":  self.stat_corrcoef(),
        }


# ── Abstract base ─────────────────────────────────────────────────────────────

class MatrixBase(MatrixStatsMixin, abc.ABC):
    """
    Abstract matrix wrapper.
    """

    default_range: ClassVar[tuple[int, int]] = (-50, 50)

    def __init__(self, data: np.ndarray) -> None:
        self._data: np.ndarray = np.asarray(data, dtype=int)

    # --- property ---
    @property
    def shape(self) -> tuple[int, ...]:
        return tuple(self._data.shape)

    @property
    def data(self) -> np.ndarray:
        return self._data

    def __len__(self) -> int:
        return self._data.shape[0]

    def __getitem__(self, key):
        return self._data[key]

    def __str__(self) -> str:
        rows = [" ".join(f"{v:>5}" for v in row) for row in self._data]
        return "\n".join(rows)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(shape={self.shape})"

    @abc.abstractmethod
    def analyse(self) -> dict:
        """Perform task-specific analysis and return results."""


class RandomMatrix(MatrixBase):
    """
    n×m integer matrix generated from a random seed.
    Contains all required NumPy demo methods.
    Demonstrates: classmethod, super(), polymorphic analyse().
    """

    def __init__(self, data: np.ndarray) -> None:
        super().__init__(data)

    @classmethod
    def create(cls,
               n: int, m: int,
               low: int | None = None,
               high: int | None = None) -> "RandomMatrix":
        """Create an n×m random integer matrix."""
        lo  = low  if low  is not None else cls.default_range[0]
        hi  = high if high is not None else cls.default_range[1]
        rng = np.random.default_rng()
        return cls(rng.integers(lo, hi, size=(n, m)))


    @staticmethod
    def demo_creation() -> dict[str, np.ndarray]:
        """Demonstrate array(), values(), zeros, ones, eye, arange, linspace."""
        return {
            "array()":    np.array([1, 2, 3, 4]),
            "zeros(2,3)": np.zeros((2, 3), dtype=int),
            "ones(2,3)":  np.ones((2, 3),  dtype=int),
            "eye(3)":     np.eye(3,         dtype=int),
            "arange":     np.arange(0, 10, 2),
            "linspace":   np.linspace(0.0, 1.0, 5),
        }


    def demo_indexing(self) -> dict[str, object]:
        """Index, slice, fancy indexing."""
        d = self._data
        return {
            "element [0,0]":     d[0, 0],
            "first row":         d[0, :],
            "first column":      d[:, 0],
            "top-left 2×2":      d[:2, :2],
            "fancy rows [0,1]":  d[[0, min(1, len(d) - 1)], :],
        }


    def demo_ufuncs(self) -> dict[str, object]:
        """Element-wise operations and universal functions."""
        d = self._data.astype(float)
        return {
            "np.abs":           np.abs(d),
            "np.sqrt(abs)":     np.sqrt(np.abs(d)),
            "np.sum":           float(np.sum(d)),
            "np.cumsum row[0]": np.cumsum(d[0]),
            "d * 2":            d * 2,
        }

    def analyse(self) -> dict:
        """Basic full-matrix stats (base class version)."""
        return {"statistics": self.statistics()}



class Variant22Matrix(RandomMatrix):
    """
    Variant 22 task: anti-diagonal minimum + variance (two methods).
    Extends RandomMatrix with task-specific analysis.
    """

    def anti_diagonal(self) -> np.ndarray:
        """Elements on the secondary diagonal (побочная диагональ)."""
        n, m = self._data.shape
        # size = min(n, m)
        return np.diag(np.fliplr(self._data))

    def min_anti_diagonal(self) -> int:
        """Smallest element on the anti-diagonal."""
        return int(self.anti_diagonal().min())

    def variance_numpy(self) -> float:
        """Variance via numpy.var() — method 1."""
        return round(float(np.var(self.anti_diagonal())), 2)

    def variance_manual(self) -> float:
        """Variance via formula  E[(x-mean)^2] — method 2."""
        ad   = self.anti_diagonal().astype(float)
        mean = float(ad.mean())
        return round(float(((ad - mean) ** 2).mean()), 2)

    def analyse(self) -> dict:
        """Full variant-22 analysis (calls super() for base stats)."""
        base = super().analyse()
        ad   = self.anti_diagonal()
        return {
            **base,
            "anti_diagonal":      ad.tolist(),
            "min_anti_diagonal":  self.min_anti_diagonal(),
            "variance_numpy":     self.variance_numpy(),
            "variance_manual":    self.variance_manual(),
        }

    def __repr__(self) -> str:
        return f"Variant22Matrix(shape={self.shape})"