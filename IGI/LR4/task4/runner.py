"""
Lab 4, Task 4 — Interactive runner (variant 21: parallelogram by d1, d2, angle X).
"""

from __future__ import annotations
from pathlib import Path

from shapes import Parallelogram, ColorMixin, draw_shape


_OUT_PATH = Path("data/task4/parallelogram.png")


def _prompt_positive_float(prompt: str) -> float:
    while True:
        raw = input(prompt).strip()
        try:
            v = float(raw)
            if v > 0:
                return v
            print("  ✗  Value must be positive.")
        except ValueError:
            print("  ✗  Not a valid number.")


def _prompt_angle(prompt: str) -> float:
    while True:
        raw = input(prompt).strip()
        try:
            v = float(raw)
            if 0 < v < 180:
                return v
            print("  ✗  Angle must be in the open interval (0°, 180°).")
        except ValueError:
            print("  ✗  Not a valid number.")


def _prompt_color() -> str:
    known = sorted(ColorMixin._KNOWN_COLORS)
    print(f"  Available colors: {', '.join(known)}")
    while True:
        raw = input("  Color: ").strip().lower()
        if raw in ColorMixin._KNOWN_COLORS:
            return raw
        print(f"  ✗  Unknown color. Choose from: {', '.join(known)}")


def run() -> None:
    print("\n" + "═" * 55)
    print("  Lab 4 · Task 4 · Parallelogram (d1, d2, angle)  (var 21)")
    print("═" * 55)
    print(f"  Shape type: {Parallelogram.shape_name()}")

    while True:
        d1    = _prompt_positive_float("  Diagonal d1: ")
        d2    = _prompt_positive_float("  Diagonal d2: ")
        angle = _prompt_angle("  Angle between diagonals X (degrees): ")
        color = _prompt_color()
        label = input("  Label text (shown on shape): ").strip() or "P"

        try:
            shape = Parallelogram(d1, d2, angle, color)
        except ValueError as exc:
            print(f"  ✗ {exc}")
            continue

        print(f"\n  {shape}")
        print(f"  Area: {shape.area():.4f}")
        a, b = shape.sides
        print(f"  Side lengths: a={a:.4f}, b={b:.4f}")

        draw_shape(shape, label, _OUT_PATH)

        again = input("\n  Draw another? [y/N]: ").strip().lower()
        if again != "y":
            break

if __name__ == "__main__":
    run()