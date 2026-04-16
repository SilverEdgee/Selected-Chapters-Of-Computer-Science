"""Lab 4, Task 2 — Interactive runner."""

from pathlib import Path
from regex import FileAnalyser

_SAMPLE_TEXT = (
    "Alice Johnson: alice@example.com sent a message. "
    "Bob Smith <bob@mail.org> replied quickly. "
    "is it important? it is indeed! "
    "The formula $v_(1)$ and $v_(a)$ but NOT $v_(ab)$. "
    "Alice and Bob met Alice again today. "
    "is is is. "
    ":) ;-( :---[[ ;-) "
    "Have you seen the issue? Yes! I agree."
)
_OUT_DIR = Path("data/task2")


def run() -> None:
    print("\n" + "═" * 55)
    print("  Lab 4 · Task 2 · Regex Text Analysis  (var 22)")
    print("═" * 55)
    print("  1  Use sample text")
    print("  2  Enter path to a text file")

    while True:
        choice = input("  Your choice: ").strip()
        if choice == "1":
            analyser = FileAnalyser.from_string(_SAMPLE_TEXT, "sample")
            break
        elif choice == "2":
            p = Path(input("  File path: ").strip())
            if p.exists():
                analyser = FileAnalyser(p)
                break
            print("  ✗  File not found.")
        else:
            print("  ✗  Enter 1 or 2.")

    print(f"\n  {analyser}")
    txt_path, zip_path = analyser.save_report(_OUT_DIR)

    report = analyser.cached_report
    print(FileAnalyser.format_report(report))

    print(f"\n  Results '{txt_path}'")
    print(f"  Archive  '{zip_path}'")
    print(analyser.zip_info(zip_path))

if __name__ == "__main__":
    run()