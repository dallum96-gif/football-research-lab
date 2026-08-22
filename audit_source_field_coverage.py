"""Audit actual source schemas against the FRL source-field registry.

The audit is read-only: it does not mutate canonical data. It reports fields
present in the source, fields in the registry but absent from a season, and
fields observed in the source but not yet catalogued.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

from player_match_stats import PL_ROOT
from source_family_adapters import team_match_source_fields, player_match_source_fields
from source_field_registry import fields_for_family


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "data" / "source_field_coverage.csv"


def _season_files(family: str, season: str) -> tuple[Path, ...]:
    expected = f"{season}_{family}.csv"
    paths: list[Path] = []
    root = Path(PL_ROOT)
    if not root.is_dir():
        return tuple()

    for club in sorted(root.iterdir()):
        if not club.is_dir() or club.name.startswith("_"):
            continue
        candidate = club / family / expected
        if candidate.is_file():
            paths.append(candidate)
    return tuple(paths)


def _csv_fields(path: Path) -> tuple[str, ...]:
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                return tuple(csv.DictReader(handle).fieldnames or ())
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode {path}")


def audit_family(family: str, season: str) -> list[dict[str, str]]:
    if family == "events_stats":
        source_family = "team_match"
        files = _season_files("events_stats", season)
        source_fields = set()
        for path in files:
            source_fields.update(_csv_fields(path))
    elif family == "players_match_stats":
        source_family = "player_match"
        files = _season_files("players_match_stats", season)
        source_fields = set()
        for path in files:
            source_fields.update(_csv_fields(path))
    elif family == "players_stats":
        source_family = "player_season"
        files = _season_files("players_stats", season)
        source_fields = set()
        for path in files:
            source_fields.update(_csv_fields(path))
    elif family == "squad":
        source_family = "squad"
        files = _season_files("squad", season)
        source_fields = set()
        for path in files:
            source_fields.update(_csv_fields(path))
    else:
        raise ValueError(f"Unknown family: {family}")

    registry = {spec.source_field: spec.semantic_status for spec in fields_for_family(source_family)}
    rows: list[dict[str, str]] = []

    for field in sorted(source_fields):
        rows.append({
            "season": season,
            "source_family": source_family,
            "source_file_family": family,
            "source_field": field,
            "registry_status": registry.get(field, "UNCATALOGUED"),
            "presence": "PRESENT",
            "source_files": str(len(files)),
        })

    for field, status in sorted(registry.items()):
        if field not in source_fields:
            rows.append({
                "season": season,
                "source_family": source_family,
                "source_file_family": family,
                "source_field": field,
                "registry_status": status,
                "presence": "ABSENT",
                "source_files": str(len(files)),
            })

    return rows


def build(seasons: tuple[str, ...], families: tuple[str, ...]) -> int:
    output_rows: list[dict[str, str]] = []
    for season in seasons:
        for family in families:
            output_rows.extend(audit_family(family, season))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    columns = [
        "season", "source_family", "source_file_family", "source_field",
        "registry_status", "presence", "source_files",
    ]
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(output_rows)
    return len(output_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", action="append", dest="seasons")
    parser.add_argument(
        "--family",
        action="append",
        dest="families",
        choices=("events_stats", "players_match_stats", "players_stats", "squad"),
    )
    args = parser.parse_args()

    seasons = tuple(args.seasons or ("2016-17", "2017-18", "2018-19", "2019-20", "2020-21", "2021-22", "2022-23", "2023-24", "2024-25", "2025-26"))
    families = tuple(args.families or ("events_stats", "players_match_stats", "players_stats", "squad"))
    rows = build(seasons, families)
    print(f"SOURCE FIELD COVERAGE: {rows} audit rows written")
    print(f"Output: {OUTPUT}")
