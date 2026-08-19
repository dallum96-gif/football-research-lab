"""Audit upstream player-match schema against FRL evidence output.

Runs against the approved local Premier-League-Stats workspace and reports
which source-native columns are present in the canonical 2016-17 source files
and whether each is preserved in the FRL evidence output.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from player_match_stats import PL_ROOT, _season_player_match_files

ROOT = Path(__file__).resolve().parent
EVIDENCE_FILE = ROOT / "data" / "player_match_evidence.csv"


def read_header(path: Path) -> list[str]:
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with path.open("r", encoding=enc, newline="") as fh:
                return csv.DictReader(fh).fieldnames or []
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode: {path}")


def audit(season: str) -> int:
    source_files = _season_player_match_files(season)
    if not source_files:
        raise FileNotFoundError(f"No canonical source files for {season} under {PL_ROOT}")
    source_fields = set()
    for path in source_files:
        source_fields.update(read_header(path))

    if not EVIDENCE_FILE.is_file():
        raise FileNotFoundError(f"Evidence output not found: {EVIDENCE_FILE}")
    evidence_fields = set(read_header(EVIDENCE_FILE))
    expected = {f"source_{field}" for field in source_fields}
    missing = sorted(expected - evidence_fields)
    unexpected_source = sorted(
        field for field in evidence_fields
        if field.startswith("source_") and field[7:] not in source_fields
    )

    print(f"SOURCE FILES: {len(source_files)}")
    print(f"SOURCE NATIVE FIELDS: {len(source_fields)}")
    print(f"FRL EVIDENCE FIELDS: {len(evidence_fields)}")
    print(f"MISSING SOURCE FIELDS IN EVIDENCE: {len(missing)}")
    for field in missing:
        print(f"MISSING {field}")
    print(f"UNEXPECTED SOURCE FIELDS IN EVIDENCE: {len(unexpected_source)}")
    for field in unexpected_source:
        print(f"UNEXPECTED {field}")

    return 0 if not missing else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", default="2016-17")
    args = parser.parse_args()
    raise SystemExit(audit(args.season))
