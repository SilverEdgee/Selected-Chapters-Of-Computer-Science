"""
Lab 4, Bonus — Pandas analysis on a Kaggle dataset (variant 22).

Uses the FIFA players dataset (available on Kaggle).
Demonstrates: Series, DataFrame, display-equivalent, loc/iloc,
              statistical methods, groupby.

Version: 1.0
"""

import abc
from pathlib import Path
from typing import ClassVar

import pandas as pd


# ── Abstract base ─────────────────────────────────────────────────────────────

class DatasetAnalyserBase(abc.ABC):
    """
    Abstract base for Pandas dataset analysers.

    Class attribute  : dataset_name — human-readable label.
    Instance attrs   : _df (DataFrame), _path (source path).
    Magic methods    : __len__, __str__, __repr__.
    """

    dataset_name: ClassVar[str] = "Dataset"

    def __init__(self, df: pd.DataFrame) -> None:
        self._df: pd.DataFrame = df

    @classmethod
    def from_csv(cls, path: Path) -> "DatasetAnalyserBase":
        """Load a CSV file and return a new analyser instance."""
        df = pd.read_csv(path)
        return cls(df)

    # --- property ---
    @property
    def df(self) -> pd.DataFrame:
        return self._df

    @property
    def shape(self) -> tuple[int, int]:
        return self._df.shape

    # --- magic ---
    def __len__(self) -> int:
        return len(self._df)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.dataset_name}, rows={len(self)})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(shape={self.shape})"

    def show_head(self, n: int = 5) -> pd.DataFrame:
        """Return (and print) the first n rows — replaces display()."""
        result = self._df.head(n)
        print(result.to_string())
        return result

    def info_dict(self) -> dict:
        """DataFrame info: shape, columns, dtypes, null counts, memory."""
        return {
            "shape":     self._df.shape,
            "columns":   list(self._df.columns),
            "dtypes":    self._df.dtypes.to_dict(),
            "null_counts": self._df.isnull().sum().to_dict(),
            "memory_bytes": int(self._df.memory_usage(deep=True).sum()),
        }

    @abc.abstractmethod
    def analyse(self) -> dict:
        """Run dataset-specific analysis."""



class FifaAnalyser(DatasetAnalyserBase):
    """
    Analysis of the FIFA players dataset.
      a) Series and DataFrame creation / access.
      b) How many times is avg ShotPower of most-aggressive players
         higher than avg ShotPower of least-aggressive players?
      c) Average SprintSpeed of players whose Wage is below average.
    """

    dataset_name: ClassVar[str] = "FIFA Players"

    _COL_AGGRESSION: ClassVar[str] = "Aggression"
    _COL_SHOTPOWER:  ClassVar[str] = "ShotPower"
    _COL_SPRINT:     ClassVar[str] = "SprintSpeed"
    _COL_WAGE:       ClassVar[str] = "Wage"

    def demo_series(self) -> dict:
        """Demonstrate Series creation and .loc/.iloc access."""
        if self._COL_SHOTPOWER not in self._df.columns:
            return {"note": "ShotPower column not found in dataset."}

        s = self._df[self._COL_SHOTPOWER].dropna()
        return {
            "type":          type(s).__name__,
            "dtype":         str(s.dtype),
            "iloc[0:3]":     s.iloc[:3].tolist(),
            "loc by index":  s.loc[s.index[:3]].tolist(),
            "describe":      s.describe().to_dict(),
        }

    def demo_dataframe(self) -> pd.DataFrame:
        """Return a small sub-DataFrame (first 5 rows, first 6 cols)."""
        return self._df.iloc[:5, :6]

    def shotpower_aggression_ratio(self) -> float | None:
        """
        How many times avg ShotPower of max-aggression players
        is greater than avg ShotPower of min-aggression players.
        """
        needed = {self._COL_AGGRESSION, self._COL_SHOTPOWER}
        if not needed.issubset(self._df.columns):
            return None

        agg_col = pd.to_numeric(self._df[self._COL_AGGRESSION], errors="coerce")
        sp_col  = pd.to_numeric(self._df[self._COL_SHOTPOWER],  errors="coerce")
        tmp = pd.DataFrame({"agg": agg_col, "sp": sp_col}).dropna()

        max_agg = tmp["agg"].max()
        min_agg = tmp["agg"].min()

        avg_sp_max = tmp.loc[tmp["agg"] == max_agg, "sp"].mean()
        avg_sp_min = tmp.loc[tmp["agg"] == min_agg, "sp"].mean()

        if avg_sp_min == 0:
            return None
        return round(avg_sp_max / avg_sp_min, 2)

    def avg_sprint_below_avg_wage(self) -> float | None:
        """Average SprintSpeed among players whose Wage is below average."""
        needed = {self._COL_SPRINT, self._COL_WAGE}
        if not needed.issubset(self._df.columns):
            return None

        def _parse_wage(w):
            """Handle strings like '€110K' or '€2.5M'."""
            import re
            if isinstance(w, (int, float)):
                return float(w)
            s = str(w).replace("€", "").replace(",", "").strip()
            m = re.match(r"([\d.]+)([KkMm]?)", s)
            if not m:
                return float("nan")
            val = float(m.group(1))
            suffix = m.group(2).upper()
            if suffix == "K":
                val *= 1_000
            elif suffix == "M":
                val *= 1_000_000
            return val

        wages  = self._df[self._COL_WAGE].apply(_parse_wage)
        sprint = pd.to_numeric(self._df[self._COL_SPRINT], errors="coerce")
        tmp = pd.DataFrame({"wage": wages, "sprint": sprint}).dropna()

        avg_wage = tmp["wage"].mean()
        below    = tmp.loc[tmp["wage"] < avg_wage, "sprint"]
        return round(below.mean(), 2) if not below.empty else None

    def analyse(self) -> dict:
        return {
            "info":                     self.info_dict(),
            "series_demo":              self.demo_series(),
            "shotpower_aggression_ratio": self.shotpower_aggression_ratio(),
            "avg_sprint_below_avg_wage":  self.avg_sprint_below_avg_wage(),
        }