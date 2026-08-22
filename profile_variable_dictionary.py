"""Profile the FRL variable dictionary by grain and navigation/semantic status."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "frl_variable_dictionary.csv"


def load_rows(path: Path = INPUT) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def profile(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "grain": Counter(r.get("grain", "") for r in rows),
        "resource": Counter(r.get("resource", "") for r in rows),
        "category": Counter(r.get("navigation_category", "") for r in rows),
        "semantic": Counter(r.get("semantic_status", "") for r in rows),
        "source_surface": Counter(r.get("source_surface", "") for r in rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=INPUT)
    args = parser.parse_args()
    rows = load_rows(args.input)
    p = profile(rows)
    print("FRL VARIABLE DICTIONARY PROFILE")
    print("=" * 90)
    print(f"Variables: {len(rows)}")
    for title, counter in p.items():
        print(f"\n{title.upper()}")
        for key, count in counter.most_common():
            print(f"  {count:4d}  {key}")


if __name__ == "__main__":
    main()
