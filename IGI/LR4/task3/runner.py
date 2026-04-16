"""Lab 4, Task 3 — Interactive runner."""

from __future__ import annotations
from pathlib import Path
from series import ArcsinAnalyser

_PLOT_PATH = Path("data/task3/arcsin_plot.png")


def _prompt_int(prompt: str, lo: int, hi: int) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            v = int(raw)
            if lo <= v <= hi:
                return v
            print(f"  ✗  Enter a value in [{lo}, {hi}].")
        except ValueError:
            print("  ✗  Not a valid integer.")


def run() -> None:
    print("\n" + "═" * 55)
    print("  Lab 4 · Task 3 · arcsin Series + Stats  (var 22)")
    print("═" * 55)

    n_terms = _prompt_int("  Number of series terms [1–50]: ", 1, 50)
    n_pts   = _prompt_int("  Number of x sample points [5–200]: ", 5, 200)

    import numpy as np
    x_values = list(np.linspace(-0.95, 0.95, n_pts))

    analyser = ArcsinAnalyser(n_terms)
    analyser.compute(x_values)

    print(f"\n  {analyser!r}")
    print(f"\n  {'x':>8}  {'Series F(x)':>14}  {'math.asin':>14}  {'error':>12}")
    print("  " + "-" * 56)
    step = max(1, len(analyser) // 15)
    for p in list(analyser)[::step]:
        print(f"  {p.x:>8.4f}  {p.value:>14.8f}  {p.ref_value:>14.8f}  {p.error:>12.2e}")

    print("\n  Statistics of series values:")
    for key, val in analyser.statistics().items():
        print(f"    {key:<12}: {val}")

    analyser.plot_and_save(_PLOT_PATH)
    print(f"\n  Plot saved to '{_PLOT_PATH}'.")

if __name__ == "__main__":
    run()