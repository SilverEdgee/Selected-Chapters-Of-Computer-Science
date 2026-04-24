"""
Lab Work #4
Module: series.py
Description: Mathematical tasks — power series
Version: 1.1
Developer: Pometko D.I., Variant 22
Date: 20-03-2026
"""

import math
import statistics
from dataclasses import dataclass
import abc
from typing import ClassVar
import matplotlib.pyplot as plt
from pathlib import Path

class StatsMixin:
    """
    Mixin: descriptive statistics over a list of floats.
    Reads self._values from the host class.
    """

    def mean(self):
        return statistics.mean(self._values)

    def median(self):
        return statistics.median(self._values)

    def mode(self):
        return statistics.mode(self._values)

    def variance(self):
        return statistics.variance(self._values)

    def stdev(self):
        return statistics.stdev(self._values)

    def statistics(self) -> dict[str, float]:
        return {
            "mean": self.mean(),
            "median": self.median(),
            "mode": self.mode(),
            "variance": self.variance(),
            "stdev": self.stdev(),
        }


@dataclass
class SeriesPoint:
    """Stores one computed point: x, series value, reference value, error."""
    x: float
    n_terms: int
    value: float
    ref_value: float

    @property
    def error(self) -> float:
        return abs(self.value - self.ref_value)


class SeriesBase(abc.ABC):
    """
    Abstract base for Taylor-series analysers.
    Class attribute : default_terms
    Magic methods   : __len__, __repr__, __iter__
    """

    default_terms: ClassVar[int] = 10

    def __init__(self, n_terms: int) -> None:
        self._n_terms: int = 0
        self.n_terms = n_terms
        self._points: list[SeriesPoint] = []
        self._values: list[float] = []

    @property
    def n_terms(self) -> int:
        return self._n_terms

    @n_terms.setter
    def n_terms(self, value: int) -> None:
        if not isinstance(value, int) or value < 1:
            raise ValueError("n_terms must be a positive integer.")
        self._n_terms = value

    def __len__(self) -> int:
        return len(self._points)

    def __iter__(self):
        return iter(self._points)

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}"
                f"(n_terms={self._n_terms}, points={len(self._points)})")

    @abc.abstractmethod
    def compute_term(self, n: int, x: float) -> float:
        """Return the n-th term of the series at x."""

    @abc.abstractmethod
    def ref_value(self, x: float) -> float:
        """Return the reference (math) value at x."""

    def series_value(self, x: float) -> float:
        """Sum the first n_terms terms of the series at x."""
        return sum(self.compute_term(n, x) for n in range(self._n_terms))

    def compute(self, x_values: list[float]) -> list[SeriesPoint]:
        """Compute series for each x; store internally and return the list."""
        self._points = [
            SeriesPoint(
                x=x,
                n_terms=self._n_terms,
                value=self.series_value(x),
                ref_value=self.ref_value(x),
            )
            for x in x_values
        ]
        self._values = [p.value for p in self._points]
        return self._points



class ArcsinSeries(SeriesBase):
    """
    Compute arcsin Taylor series
    """

    def compute_term(self, n: int, x: float) -> float:
        num = math.factorial(2 * n)
        den = (4 ** n) * (math.factorial(n) ** 2) * (2 * n + 1)
        return (num / den) * (x ** (2 * n + 1))

    def ref_value(self, x: float) -> float:
        return math.asin(x)


class ArcsinAnalyser(StatsMixin, ArcsinSeries):
    """
    Full analyser: arcsin series + statistics + matplotlib.
    """

    series_label: ClassVar[str] = "arcsin Taylor"

    def __init__(self, n_terms: int = ArcsinSeries.default_terms) -> None:
        super().__init__(n_terms)

    @classmethod
    def with_default_terms(cls) -> "ArcsinAnalyser":
        """Convenience constructor using class default."""
        return cls(cls.default_terms)

    def plot_and_save(self, out_path: Path) -> None:
        """Plot series vs math.asin and save to out_path."""
        if not self._points:
            raise RuntimeError("No data — call compute() first.")


        xs = [p.x for p in self._points]
        series_ys = [p.value for p in self._points]
        math_ys = [p.ref_value for p in self._points]

        fig, ax = plt.subplots(figsize=(9, 5))
        ax.plot(xs, series_ys, color="blue", lw=2,
                label=f"{self.series_label} (n={self.n_terms})",
                marker="o", markersize=3)
        ax.plot(xs, math_ys, color="tomato", lw=2,
                label="math.asin(x)", linestyle="--")

        ax.axhline(0, color="black", lw=0.7)
        ax.axvline(0, color="black", lw=0.7)

        idx = min(range(len(xs)), key=lambda i: abs(xs[i] - 0.5))
        ax.annotate(
            f"x=0.5\nS≈{series_ys[idx]:.4f}",
            xy=(xs[idx], series_ys[idx]),
            xytext=(xs[idx] + 0.05, series_ys[idx] - 0.15),
            arrowprops=dict(arrowstyle="->", color="gray"),
            fontsize=8,
        )

        ax.set_xlabel("x")
        ax.set_ylabel("arcsin(x)")
        ax.set_title("arcsin(x): Taylor series vs math.asin  [Variant 22]")
        ax.legend()
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.text(0.02, 0.02, "LR-4, Task 3", transform=ax.transAxes,
                fontsize=7, alpha=0.5)

        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path)
        plt.close(fig)
