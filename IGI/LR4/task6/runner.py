"""Lab 4, Bonus — Pandas interactive runner."""

from __future__ import annotations
from pathlib import Path
from pandas_analysis import FifaAnalyser

_DEFAULT_CSV = Path("data/bonus/fifa_players.csv")


def _make_sample_df():
    """Generate a small synthetic FIFA-like DataFrame for demo purposes."""
    import pandas as pd, numpy as np
    rng = np.random.default_rng(42)
    n = 200
    return pd.DataFrame({
        "Name":        [f"Player_{i}" for i in range(n)],
        "Aggression":  rng.integers(20, 100, n),
        "ShotPower":   rng.integers(30, 100, n),
        "SprintSpeed": rng.integers(40, 99,  n),
        "Wage":        [f"€{rng.integers(1, 500)}K" for _ in range(n)],
        "Age":         rng.integers(16, 38, n),
    })


def run() -> None:
    print("\n" + "═" * 55)
    print("  Lab 4 · Bonus · Pandas Analysis")
    print("═" * 55)
    print("  1  Use synthetic demo data")
    print("  2  Load CSV from path")

    while True:
        choice = input("  Your choice: ").strip()
        if choice == "1":
            import pandas as pd
            analyser = FifaAnalyser(_make_sample_df())
            break
        elif choice == "2":
            p = Path(input("  CSV path: ").strip())
            if p.exists():
                analyser = FifaAnalyser.from_csv(p)
                break
            print("  ✗  File not found.")
        else:
            print("  ✗  Enter 1 or 2.")

    print(f"\n  {analyser}")
    print(f"  {analyser!r}")

    print("\n  ── DataFrame head ──")
    print(analyser.demo_dataframe().to_string())

    print("\n  ── DataFrame info ──")
    info = analyser.info_dict()
    print(f"  shape:  {info['shape']}")
    print(f"  columns ({len(info['columns'])}): {info['columns']}")
    print(f"  memory: {info['memory_bytes']} bytes")

    print("\n  ── Series demo (ShotPower) ──")
    for k, v in analyser.demo_series().items():
        print(f"  {k}: {v}")

    result = analyser.analyse()

    ratio = result["shotpower_aggression_ratio"]
    print(f"\n  ShotPower ratio (max-agg / min-agg): {ratio}")

    sprint = result["avg_sprint_below_avg_wage"]
    print(f"  Avg SprintSpeed (below avg wage):    {sprint}")

if __name__ == "__main__":
    run()