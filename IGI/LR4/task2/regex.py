"""
Lab 4, Task 2 — Text analysis with regex (variant 22).
All analysis logic lives in a class hierarchy.

Author: Denis Pometko
Variant 22 · Lab 4
Version: 1.0
"""

import abc
import re
import zipfile
from pathlib import Path
from typing import ClassVar



class SentenceMixin:
    """Mixin: sentence-level statistics. Reads self._text from the host."""

    def count_sentences(self) -> dict[str, int]:
        """Count declarative / interrogative / imperative sentences."""
        text  = self._text 
        decl  = len(re.findall(r'[^.!?]+\.', text))
        interr = len(re.findall(r'[^.!?]+\?', text))
        imper  = len(re.findall(r'[^.!?]+!',  text))
        return {"declarative": decl, "interrogative": interr,
                "imperative": imper, "total": decl + interr + imper}

    def avg_sentence_length(self) -> float:
        """Average sentence length in characters (word chars only)."""
        sentences = [s.strip() for s in re.split(r'[.!?]+', self._text) if s.strip()]  # type: ignore
        if not sentences:
            return 0.0
        lengths = [len(re.sub(r'[^A-Za-zА-Яа-яЁё0-9]', '', s)) for s in sentences]
        return round(sum(lengths) / len(lengths), 2)

    def avg_word_length(self) -> float:
        """Average word length in characters."""
        words = re.findall(r'[A-Za-zА-Яа-яЁё]+', self._text)  # type: ignore
        return round(sum(len(w) for w in words) / len(words), 2) if words else 0.0


class SmileyMixin:
    """
    Mixin: smiley detection per spec.
    Pattern: [:;] followed by 0+ '-', followed by 1+ identical bracket chars.
    """

    _SMILEY_RE: ClassVar[re.Pattern] = re.compile(r'[:;]-*[()\[\]]+')

    def count_smileys(self) -> int:
        """Count valid smileys in self._text."""
        raw = self._SMILEY_RE.findall(self._text)  # type: ignore[attr-defined]
        count = 0
        for m in raw:
            bracket_part = re.sub(r'^[:;]-*', '', m)
            if len(set(bracket_part)) == 1:
                count += 1
        return count



class TextAnalyserBase(SentenceMixin, SmileyMixin, abc.ABC):
    """
    Abstract base for text analysers.

    Class attribute : default_encoding — used for all file I/O.
    Instance attribute: _text — the working text.
    Magic methods   : __len__, __bool__, __str__, __repr__.
    """

    # static (class-level) attribute
    default_encoding: ClassVar[str] = "utf-8"

    def __init__(self, text: str) -> None:
        self._text: str = text

    # --- property: text ---
    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("text must be a string.")
        self._text = value

    def __len__(self) -> int:
        return len(self._text)

    def __bool__(self) -> bool:
        return bool(self._text.strip())

    def __str__(self) -> str:
        preview = self._text[:60].replace("\n", " ")
        return f"{self.__class__.__name__}(len={len(self)}, preview={preview!r})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(text_length={len(self._text)})"

    @abc.abstractmethod
    def analyse(self) -> dict:
        """Run all analysis and return a structured results dict."""

    def _words(self) -> list[str]:
        return re.findall(r'[A-Za-zА-Яа-яЁё]+', self._text.lower())

    def common_stats(self) -> dict:
        """Common stats required from every variant."""
        return {
            "sentence_counts":           self.count_sentences(),
            "avg_sentence_length_chars": self.avg_sentence_length(),
            "avg_word_length_chars":     self.avg_word_length(),
            "smiley_count":              self.count_smileys(),
        }



class Variant22Analyser(TextAnalyserBase):
    """
    Concrete analyser for variant 22.
    Individual tasks:
      a) Extract emails + recipient names.
      b) Replace $v_(i)$ (single-char i) → v[i].
      c) Words with odd letter count.
      d) Shortest word starting with 'i'.
      e) Duplicate (repeated) words.
    Demonstrates: super(), polymorphic analyse(), instance attribute caching.
    """

    def __init__(self, text: str) -> None:
        super().__init__(text)
        self._cached_report: dict | None = None


    def extract_emails_with_names(self) -> list[tuple[str, str]]:
        """Find 'Name <email>' or 'Name: email' pairs in the text."""
        pattern = (r'([A-Za-z][A-Za-z\s]+?)\s*[:<]\s*'
                   r'([A-Za-z0-9_.+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,})[>]?')
        return [(m.group(1).strip(), m.group(2))
                for m in re.finditer(pattern, self._text)]

    def replace_v_subscript(self) -> str:
        """Replace $v_(i)$ where i is exactly one digit or letter with v[i]."""
        return re.sub(r'\$v_\(([A-Za-z0-9])\)\$', r'v[\1]', self._text)

    def words_with_odd_letter_count(self) -> list[str]:
        """Return words whose letter count is odd."""
        return [w for w in self._words() if len(w) % 2 == 1]

    def shortest_word_starting_with_i(self) -> str | None:
        """Shortest word starting with 'i', or None if absent."""
        candidates = [w for w in self._words() if w.startswith("i")]
        return min(candidates, key=len, default=None)

    def duplicate_words(self) -> list[str]:
        """Words that appear more than once (sorted alphabetically)."""
        seen: dict[str, int] = {}
        for w in self._words():
            seen[w] = seen.get(w, 0) + 1
        return sorted(w for w, cnt in seen.items() if cnt > 1)


    def analyse(self) -> dict:
        """Run all tasks; cache and return the report."""
        self._cached_report = {
            **self.common_stats(),
            "emails_with_names":      self.extract_emails_with_names(),
            "v_subscript_replaced":   self.replace_v_subscript(),
            "words_odd_letter_count": self.words_with_odd_letter_count(),
            "shortest_word_i":        self.shortest_word_starting_with_i(),
            "duplicate_words":        self.duplicate_words(),
        }
        return self._cached_report

    def __repr__(self) -> str:
        cached = "yes" if self._cached_report else "no"
        return f"Variant22Analyser(len={len(self)}, cached={cached})"

    @property
    def cached_report(self):
        return self._cached_report


class FileAnalyser(Variant22Analyser):
    """
    Extends Variant22Analyser with file I/O and ZIP archiving.
    """

    def __init__(self, source_path: Path) -> None:
        text = source_path.read_text(encoding=self.default_encoding)
        super().__init__(text)
        self._source_path = source_path

    @classmethod
    def from_string(cls, text: str, label: str = "input") -> "FileAnalyser":
        """Construct from a raw string by first saving it to a temp file."""
        tmp = Path(f"data/task2/_{label}.txt")
        tmp.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_text(text, encoding=cls.default_encoding)
        return cls(tmp)

    @property
    def source_path(self) -> Path:
        return self._source_path

    def save_report(self, out_dir: Path) -> tuple[Path, Path]:
        """Analyse, write report to .txt, zip it; return (txt_path, zip_path)."""
        report = self.analyse()
        out_dir.mkdir(parents=True, exist_ok=True)
        txt_path = out_dir / "task2_results.txt"
        zip_path = out_dir / "task2_results.zip"

        txt_path.write_text(self.format_report(report), encoding=self.default_encoding)
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.write(txt_path, txt_path.name)

        return txt_path, zip_path

    @staticmethod
    def zip_info(zip_path: Path) -> str:
        """Human-readable summary of the zip archive."""
        lines = [f"Archive: {zip_path}"]
        with zipfile.ZipFile(zip_path) as zf:
            for info in zf.infolist():
                lines.append(
                    f"  {info.filename:<40} "
                    f"size={info.file_size} B  "
                    f"compressed={info.compress_size} B"
                )
        return "\n".join(lines)

    # --- private formatting ---
    @staticmethod
    def format_report(report: dict) -> str:
        lines = ["=" * 60, "Text Analysis Report — Variant 22", "=" * 60, ""]
        sc = report["sentence_counts"]
        lines += [
            "── Common stats ──",
            f"  Total sentences:     {sc['total']}",
            f"  Declarative:         {sc['declarative']}",
            f"  Interrogative:       {sc['interrogative']}",
            f"  Imperative:          {sc['imperative']}",
            f"  Avg sentence length: {report['avg_sentence_length_chars']} chars",
            f"  Avg word length:     {report['avg_word_length_chars']} chars",
            f"  Smileys:             {report['smiley_count']}",
            "",
            "── Emails with recipient names ──",
        ]
        for name, email in report["emails_with_names"]:
            lines.append(f"  {name!r:30} → {email}")
        lines += [
            "",
            "── $v_(i)$ substitution result ──",
            f"  {report['v_subscript_replaced']}",
            "",
            "── Words with odd letter count ──",
            f"  {', '.join(report['words_odd_letter_count']) or '(none)'}",
            "",
            "── Shortest word starting with 'i' ──",
            f"  {report['shortest_word_i'] or '(none)'}",
            "",
            "── Duplicate words ──",
            f"  {', '.join(report['duplicate_words']) or '(none)'}",
        ]
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"FileAnalyser(source={self._source_path.name!r}, len={len(self)})"