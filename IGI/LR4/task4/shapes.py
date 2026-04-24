"""
Lab 4, Task 4 — Geometric figures with matplotlib (variant 21).
Variant 21: Parallelogram by diagonals d1, d2 and angle X (degrees).
"""

import abc
import math
from pathlib import Path
from typing import ClassVar



class ColorMixin:
    """Mixin providing a validated colour property."""

    _KNOWN_COLORS: ClassVar[frozenset[str]] = frozenset({
        "red", "green", "blue", "yellow", "orange", "purple",
        "cyan", "magenta", "white", "black", "gray", "pink",
    })

    def __init__(self, color: str = "blue") -> None:
        self._color: str = ""
        self.color = color

    @property
    def color(self) -> str:
        return self._color

    @color.setter
    def color(self, value: str) -> None:
        norm = value.strip().lower()
        if norm not in self._KNOWN_COLORS:
            raise ValueError(
                f"Unknown color {value!r}. "
                f"Choose from: {', '.join(sorted(self._KNOWN_COLORS))}"
            )
        self._color = norm



class Shape(abc.ABC):
    """Abstract geometric shape."""

    @abc.abstractmethod
    def area(self) -> float:
        """Return the area of the shape."""

    @abc.abstractmethod
    def vertices(self) -> list[tuple[float, float]]:
        """Return the vertices of the shape as (x, y) pairs."""

    @abc.abstractmethod
    def describe(self) -> str:
        """Return a human-readable description."""



class Parallelogram(ColorMixin, Shape):
    """
    Parallelogram defined by diagonals *d1*, *d2* and the angle *angle_deg*
    between them.
    """

    figure_name: ClassVar[str] = "Parallelogram"

    def __init__(self, d1: float, d2: float, angle_deg: float, color: str = "blue") -> None:
        super().__init__(color=color)
        self.d1        = d1
        self.d2        = d2
        self.angle_deg = angle_deg
        self._validate()

    def _validate(self) -> None:
        if self.d1 <= 0 or self.d2 <= 0:
            raise ValueError("Diagonals must be positive.")
        if not (0 < self.angle_deg < 180):
            raise ValueError("Angle between diagonals must be in (0°, 180°).")

    @property
    def sides(self) -> tuple[float, float]:
        """Return (side_a, side_b) using the parallelogram diagonal law."""
        half_d1 = self.d1 / 2
        half_d2 = self.d2 / 2
        rad = math.radians(self.angle_deg)
        a = math.sqrt(half_d1**2 + half_d2**2 - 2*half_d1*half_d2*math.cos(rad))
        b = math.sqrt(half_d1**2 + half_d2**2 + 2*half_d1*half_d2*math.cos(rad))
        return a, b

    def area(self) -> float:
        return (self.d1 * self.d2 * math.sin(math.radians(self.angle_deg))) / 2

    def vertices(self) -> list[tuple[float, float]]:
        """
        Place the parallelogram centred at origin.
        Diagonal 1 is horizontal; diagonal 2 is at *angle_deg*.
        """
        a, b = self.d1 / 2, self.d2 / 2
        rad  = math.radians(self.angle_deg)
        # the four vertices are the four half-diagonal endpoints
        v1 = ( a,  0.0)
        v2 = ( b * math.cos(rad),  b * math.sin(rad))
        v3 = (-a,  0.0)
        v4 = (-b * math.cos(rad), -b * math.sin(rad))
        return [v1, v2, v3, v4]

    @classmethod
    def shape_name(cls) -> str:
        return cls.figure_name

    def __str__(self) -> str:
        a, b = self.sides
        return (
            "{name} (color={color!r}): "
            "d1={d1:.2f}, d2={d2:.2f}, angle={angle:.1f}° | "
            "sides=({a:.2f}, {b:.2f}) | area={area:.4f}"
        ).format(
            name  = self.figure_name,
            color = self.color,
            d1    = self.d1,
            d2    = self.d2,
            angle = self.angle_deg,
            a=a, b=b,
            area  = self.area(),
        )

    def describe(self) -> str:
        """Human-readable description (satisfies Shape contract)."""
        return str(self)

    def __repr__(self) -> str:
        return (
            f"Parallelogram(d1={self.d1}, d2={self.d2}, "
            f"angle_deg={self.angle_deg}, color={self.color!r})"
        )


def draw_shape(shape: Shape, label: str, out_path: Path) -> None:
    """Draw *shape* filled with its color, add *label*, save to *out_path*."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MplPolygon

    verts = shape.vertices()
    xs = [v[0] for v in verts] + [verts[0][0]]
    ys = [v[1] for v in verts] + [verts[0][1]]

    fig, ax = plt.subplots(figsize=(7, 6))
    patch = MplPolygon(
        verts, closed=True,
        facecolor=shape.color,
        edgecolor="black", linewidth=2, alpha=0.6,
    )
    ax.add_patch(patch)
    ax.plot(xs, ys, color="black", linewidth=1.5)

    cx = sum(v[0] for v in verts) / len(verts)
    cy = sum(v[1] for v in verts) / len(verts)
    ax.text(cx, cy, label, ha="center", va="center", fontsize=11,
            fontweight="bold", color="white")

    ax.set_aspect("equal")
    ax.autoscale()
    ax.margins(0.2)
    ax.set_title(shape.describe())
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True, linestyle=":", alpha=0.5)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path)
    plt.close(fig)
    print(f"Figure saved to '{out_path}'.")