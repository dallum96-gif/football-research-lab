"""Reusable access to the upstream PL/PulseLive squad metadata family.

This is source evidence only. It does not promote a source player ID or
metadata value into the canonical FRL player identity registry automatically.
"""
from __future__ import annotations

import csv
from pathlib import Path

from player_match_stats import PL_ROOT


def _read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                reader = csv.DictReader(handle)
                return list(reader), reader.fieldnames or []
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode CSV: {path}")


def _files(season: str) -> tuple[Path, ...]:
    root = Path(PL_ROOT)
    if not root.is_dir():
        raise FileNotFoundError(f"Approved upstream source not found: {root}")
    expected = f"{season}_squad.csv"
    paths = []
    for club_dir in sorted(root.iterdir()):
        if not club_dir.is_dir() or club_dir.name.startswith("_"):
            continue
        path = club_dir / "squad" / expected
        if path.is_file():
            paths.append(path)
    return tuple(paths)


def source_rows(season: str) -> tuple[dict, ...]:
    records = []
    for path in _files(season):
        rows, _ = _read_csv(path)
        for row in rows:
            item = dict(row)
            item["_source_file"] = str(path)
            records.append(item)
    return tuple(records)


def source_fields(season: str) -> tuple[str, ...]:
    fields: set[str] = set()
    for row in source_rows(season):
        fields.update(key for key in row if key != "_source_file")
    return tuple(sorted(fields))


def players_by_source_id(season: str) -> dict[str, tuple[dict, ...]]:
    grouped: dict[str, list[dict]] = {}
    for row in source_rows(season):
        source_id = str(row.get("playerId", "")).strip()
        if not source_id:
            continue
        grouped.setdefault(source_id, []).append(row)
    return {key: tuple(value) for key, value in grouped.items()}
