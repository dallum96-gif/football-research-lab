"""Profile the FRL variable universe by grain and navigation/semantic status."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "frl_variable_dictionary.csv"
DICTIONARY = ROOT / "data" / "frl_variable_dictionary.csv"

JOIN_KEYS = ("source_surface", "resource", "grain", "field_name")


def load_rows(path: Path = INPUT) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def _dictionary_index(path: Path = DICTIONARY) -> dict[tuple[str, str, str, str], dict[str, str]]:
    if not path.exists():
        return {}
    rows = load_rows(path)
    return {
        tuple(row.get(key, "") for key in JOIN_KEYS): row
        for row in rows
    }


def _enrich_decomposed_rows(
    rows: list[dict[str, str]],
    dictionary_path: Path = DICTIONARY,
) -> list[dict[str, str]]:
    """Enrich a decomposed master file with dictionary metadata when available."""
    if not rows or "decomposed_grain" not in rows[0]:
        return rows

    index = _dictionary_index(dictionary_path)
    enriched: list[dict[str, str]] = []
    for row in rows:
        key = tuple(row.get(k, "") for k in JOIN_KEYS)
        base = dict(index.get(key, {}))
        base.update(row)
        # Resolved/decomposed grain is authoritative for this profiling pass.
        base["profile_grain"] = row.get("decomposed_grain", "")
        enriched.append(base)
    return enriched


def profile(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "grain": Counter(r.get("profile_grain", r.get("grain", "")) for r in rows),
        "original_grain": Counter(r.get("grain", "") for r in rows),
        "resource": Counter(r.get("resource", "") for r in rows),
        "category": Counter(r.get("navigation_category", "") or "UNAVAILABLE_FOR_INPUT" for r in rows),
        "semantic": Counter(r.get("semantic_status", "") or "UNAVAILABLE_FOR_INPUT" for r in rows),
        "source_surface": Counter(r.get("source_surface", "") for r in rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=INPUT)
    parser.add_argument(
        "--dictionary",
        type=Path,
        default=DICTIONARY,
        help="Dictionary used to enrich decomposed master-universe rows.",
    )
    args = parser.parse_args()

    rows = _enrich_decomposed_rows(load_rows(args.input), args.dictionary)
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
