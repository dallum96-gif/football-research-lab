"""Build complete player-season evidence from approved Premier-League-Stats CSVs.

Output grain: one row per upstream player-season source record.
Every source-native field is preserved under source_*.
No player source ID is promoted to a global FRL identity here.
"""
from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path
from player_match_stats import PL_ROOT

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "data" / "player_season_evidence.csv"
AUDIT = ROOT / "data" / "player_season_evidence_build_audit.csv"


def read_csv(path: Path):
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with path.open("r", encoding=encoding, newline="") as h:
                r = csv.DictReader(h)
                return list(r), r.fieldnames or []
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode CSV: {path}")


def source_files(season: str):
    expected = f"{season}_players_stats.csv"
    paths = []
    root = Path(PL_ROOT)
    if not root.is_dir():
        raise FileNotFoundError(f"Approved upstream source not found: {root}")
    for club in sorted(root.iterdir()):
        if not club.is_dir() or club.name.startswith("_"):
            continue
        path = club / "players_stats" / expected
        if path.is_file():
            paths.append(path)
    return tuple(paths)


def build(season: str):
    files = source_files(season)
    if not files:
        raise FileNotFoundError(f"No players_stats files found for {season}")

    evidence = []
    audit = []
    seen = set()
    source_fields = set()

    for path in files:
        rows, fields = read_csv(path)
        source_fields.update(fields)
        for row in rows:
            source_id = str(row.get("playerId", "")).strip()
            player_name = str(row.get("playerName", "")).strip()
            key = (season, source_id, player_name, str(row.get("team_id", "")).strip())
            if key in seen:
                audit.append({"status": "DUPLICATE_SOURCE_ROW", "source_file": str(path), "player_id": source_id, "reason": "Duplicate player-season source key"})
                continue
            seen.add(key)
            out = {
                "frl_season": season,
                "frl_source_player_id": source_id,
                "frl_source_team_id": str(row.get("team_id", "")).strip(),
                "frl_source_team": str(row.get("team_name", "")).strip(),
                "frl_source_file": str(path),
            }
            for field, value in row.items():
                out[f"source_{field}"] = value
            evidence.append(out)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUTPUT.with_suffix(".tmp.csv")
    tmp_audit = AUDIT.with_suffix(".tmp.csv")
    cols = list(evidence[0].keys()) if evidence else []
    for row in evidence:
        for field in row:
            if field not in cols:
                cols.append(field)
    with tmp.open("w", encoding="utf-8-sig", newline="") as h:
        writer = csv.DictWriter(h, fieldnames=cols, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(evidence)
    with tmp_audit.open("w", encoding="utf-8-sig", newline="") as h:
        writer = csv.DictWriter(h, fieldnames=["status", "source_file", "player_id", "reason"])
        writer.writeheader()
        writer.writerows(audit)
    os.replace(tmp, OUTPUT)
    os.replace(tmp_audit, AUDIT)
    issues = sum(r["status"] != "RESOLVED" for r in audit)
    return len(evidence), len(source_fields), issues


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--season", required=True)
    args = p.parse_args()
    rows, fields, issues = build(args.season)
    print(f"PLAYER-SEASON EVIDENCE: {rows} rows written")
    print(f"SOURCE NATIVE FIELDS: {fields}")
    print(f"DUPLICATE/ERROR STATES: {issues}")
    print(f"Output: {OUTPUT}")
    print(f"Audit: {AUDIT}")
    if issues:
        raise SystemExit(1)
