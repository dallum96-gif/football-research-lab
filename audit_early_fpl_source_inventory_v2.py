"""Compact discovery audit for early-season FPL source files.

Read-only: inventory candidate CSV/source files under the configured local
source tree, summarising file counts, schemas and identity-like columns.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
from pathlib import Path

ROOT = Path(r"C:\Users\dlall\football_database\Premier-League-Stats\pl_stats")
SEASONS = ("2016-17", "2017-18", "2018-19", "2019-20")
KEYWORDS = ("fpl", "gameweek", "player", "squad", "team", "gw", "fantasy")
ID_KEYWORDS = ("player", "element", "team", "club", "code", "id", "name")


def headers(path: Path) -> tuple[str, ...]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            return tuple(csv.reader(f).__next__())
    except Exception:
        return ()


def main() -> None:
    print("=" * 96)
    print("FRL EARLY-SEASON FPL SOURCE INVENTORY V2")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 96)
    print(f"Source root: {ROOT}")
    if not ROOT.exists():
        print("SOURCE ROOT MISSING")
        return

    all_csv = list(ROOT.rglob("*.csv"))
    by_season = {s: [] for s in SEASONS}
    for p in all_csv:
        low = p.as_posix().casefold()
        for s in SEASONS:
            if s in p.name or s in low:
                by_season[s].append(p)

    for season, paths in by_season.items():
        print(f"\n{season}: {len(paths)} CSV files")
        keyword_paths = [p for p in paths if any(k in p.as_posix().casefold() for k in KEYWORDS)]
        print(f"  keyword-matching files: {len(keyword_paths)}")
        schema_counts: Counter[tuple[str, ...]] = Counter()
        examples: defaultdict[tuple[str, ...], list[str]] = defaultdict(list)
        for p in keyword_paths:
            h = headers(p)
            if not h:
                continue
            schema_counts[h] += 1
            if len(examples[h]) < 3:
                examples[h].append(str(p))
        for i, (h, count) in enumerate(schema_counts.most_common(8), 1):
            ids = [c for c in h if any(k in c.casefold() for k in ID_KEYWORDS)]
            print(f"  schema {i}: {count} files")
            print(f"    identity-like columns: {ids[:20]}")
            print(f"    example: {examples[h][0]}")

    print("\nCANDIDATE FILES CONTAINING IDENTITY-LIKE COLUMNS:")
    shown = 0
    seen = set()
    for p in all_csv:
        low = p.as_posix().casefold()
        if not any(s in low for s in SEASONS):
            continue
        h = headers(p)
        ids = tuple(c for c in h if any(k in c.casefold() for k in ID_KEYWORDS))
        if not ids:
            continue
        key = (tuple(h), p.parent.as_posix().casefold())
        if key in seen:
            continue
        seen.add(key)
        print(f"  {p} | ids={list(ids)[:15]}")
        shown += 1
        if shown >= 50:
            print("  ... output capped at 50 representative files")
            break

    print("\nNo files were written or modified.")
    print("=" * 96)


if __name__ == "__main__":
    main()
