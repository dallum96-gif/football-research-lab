"""Audit that complete upstream events_stats fields are preserved."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from build_fixture_team_evidence import FIXTURE_FIELDS, PL_ROOT, _read_csv if False else None

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "data" / "fixture_team_evidence.csv"


def read_header(path: Path):
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                return next(csv.reader(handle))
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode CSV: {path}")


def source_files(season: str):
    expected = f"{season}_events_stats.csv"
    paths = []
    for club_dir in PL_ROOT.iterdir():
        if not club_dir.is_dir() or club_dir.name.startswith("_"):
            continue
        path = club_dir / "events_stats" / expected
        if path.is_file():
            paths.append(path)
    return tuple(sorted(paths))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", required=True)
    args = parser.parse_args()

    files = source_files(args.season)
    source_fields = set()
    for path in files:
        source_fields.update(read_header(path))

    frl_header = set(read_header(OUTPUT)) if OUTPUT.is_file() else set()
    frl_source_fields = {f[len("source_"):] for f in frl_header if f.startswith("source_")}

    missing = sorted(source_fields - frl_source_fields)
    unexpected = sorted(frl_source_fields - source_fields)

    print(f"SOURCE FILES: {len(files)}")
    print(f"SOURCE NATIVE FIELDS: {len(source_fields)}")
    print(f"FRL PRESERVED SOURCE FIELDS: {len(frl_source_fields)}")
    print(f"MISSING SOURCE FIELDS IN EVIDENCE: {len(missing)}")
    print(f"UNEXPECTED SOURCE FIELDS IN EVIDENCE: {len(unexpected)}")
    if missing:
        print("Missing:")
        for field in missing:
            print(f"  {field}")
    if unexpected:
        print("Unexpected:")
        for field in unexpected:
            print(f"  {field}")
    if missing or unexpected:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
