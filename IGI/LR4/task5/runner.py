"""Lab 4, Task 5 — Interactive runner."""

from __future__ import annotations
from matrix import Variant22Matrix


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
    print("  Lab 4 · Task 5 · NumPy Matrix Analysis  (var 22)")
    print("═" * 55)

    n = _prompt_int("  Matrix rows    n [2–10]: ", 2, 10)
    m = _prompt_int("  Matrix columns m [2–10]: ", 2, 10)

    mat = Variant22Matrix.create(n, m)
    print(f"\n  Generated matrix {n}×{m}:\n{mat}")
    print(f"\n  {mat!r}")

    result = mat.analyse()
    print(f"\n  Anti-diagonal elements: {result['anti_diagonal']}")
    print(f"  Min on anti-diagonal:   {result['min_anti_diagonal']}")
    print(f"  Variance (numpy.var):   {result['variance_numpy']}")
    print(f"  Variance (manual):      {result['variance_manual']}")

    print("\n  Full matrix statistics:")
    for k, v in result["statistics"].items():
        print(f"    {k:<24}: {v}")

    print("\n  ── Array creation demos ──")
    for name, val in Variant22Matrix.demo_creation().items():
        print(f"    {name:<14}: {val}")

    print("\n  ── Indexing demos ──")
    for name, val in mat.demo_indexing().items():
        print(f"    {name:<22}: {val}")

    print("\n  ── Ufunc demos ──")
    for name, val in mat.demo_ufuncs().items():
        print(f"    {name:<22}: {str(val)[:55]}")

if __name__ == "__main__":
    run()