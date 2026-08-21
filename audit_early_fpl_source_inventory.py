"""Read-only inventory of early-season FPL source-family candidates.

Scans the configured local Premier-League-Stats source tree for 2016-17..2019-20
CSV files containing player/club/team identity fields. Prints only compact
summary metadata; it never writes data or infers identities.
"""
from __future__ import annotations

import csv
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"C:\Users\dlall\football_database\Premier-League-Stats\pl_stats")
SEASONS = ("2016-17", "2017-18", "2018-19", "2019-20")


def headers(path: Path):
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as fh:
            return tuple(next(csv.reader(fh), []))
    except Exception:
        for enc in ("cp1252", "latin-1"):
            try:
                with path.open("r", encoding=enc, newline="") as fh:
                    return tuple(next(csv.reader(fh), []))
            except Exception:
                continue
    return ()


def relevant(cols):
    joined = "|".join(c.casefold() for c in cols)
    return any(k in joined for k in ("player", "element", "team", "club", "squad"))


def main():
    print("=" * 96)
    print("FRL EARLY FPL SOURCE INVENTORY")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 96)
    print(f"Source root: {ROOT}")
    if not ROOT.is_dir():
        print("SOURCE ROOT MISSING")
        return

    counts = Counter()
    by_season = defaultdict(list)
    for path in ROOT.rglob("*.csv"):
        name = path.name
        hit = next((s for s in SEASONS if s in name or s in str(path)), None)
        if not hit:
            continue
        cols = headers(path)
        if not relevant(cols):
            continue
        rel = str(path.relative_to(ROOT))
        identity_cols = tuple(c for c in cols if any(k in c.casefold() for k in ("player", "element", "team", "club")))
        counts[identity_cols] += 1
        by_season[hit].append((rel, cols))

    for season in SEASONS:
        rows = by_season.get(season, [])
        print(f"\n{season}: {len(rows)} candidate CSV files")
        # group by exact header signature, compactly
        sigs = Counter(tuple(cols) for _, cols in rows)
        for sig, n in sigs.most_common(10):
            short = ", ".join(sig[:18])
            extra = f" ... (+{len(sig)-18} cols)" if len(sig) > 18 else ""
            print(f"  {n} file(s) | headers: {short}{extra}")
        print("  SAMPLE PATHS:")
        for rel, cols in rows[:12]:
            print(f"    {rel}")

    print("\nCANDIDATE FILES BY IDENTITY-RELATED HEADER SIGNATURE:")
    for sig, n in counts.most_common(20):
        print(f"  {n:4} | {', '.join(sig)}")
    print("\nNo files were written or modified.")
    print("=" * 96)


if __name__ == "__main__":
    main()
