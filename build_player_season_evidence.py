"""Build complete player-season evidence from approved Premier-League-Stats CSVs.

Output grain: one row per upstream player-season source record.
Every source-native field is preserved under source_*.
No player source ID is promoted to a global FRL identity here.
Source rows are never silently discarded when source keys collide; collisions
are retained and explicitly audited.
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
    seen = {}
    source_fields = set()

    for path in files:
        rows, fields = read_csv(path)
        source_fields.update(fields)

        for row_number, row in enumerate(rows, start=2):
            source_id = str(row.get("playerId", "")).strip()
            player_name = str(row.get("playerName", "")).strip()
            source_team_id = str(row.get("team_id", "")).strip()
            source_team = str(row.get("team_name", "")).strip()

            source_key = (
                season,
                source_id,
                player_name,
                source_team_id,
            )
            record_id = f"{path}::row-{row_number}"

            collision_status = "RESOLVED"
            collision_reason = ""
            previous_records = seen.setdefault(source_key, [])
            if previous_records:
                collision_status = "DUPLICATE_SOURCE_KEY_PRESERVED"
                collision_reason = (
                    "Same season/player/name/source-team key appeared in another "
                    "upstream source record; row retained verbatim."
                )

            previous_records.append(record_id)

            out = {
                "frl_season": season,
                "frl_source_record_id": record_id,
                "frl_source_row_number": row_number,
                "frl_source_player_id": source_id,
                "frl_source_team_id": source_team_id,
                "frl_source_team": source_team,
                "frl_source_context_status": collision_status,
                "frl_source_file": str(path),
            }
            for field, value in row.items():
                out[f"source_{field}"] = value
            evidence.append(out)

            audit.append(
                {
                    "status": collision_status,
                    "source_file": str(path),
                    "player_id": source_id,
                    "source_team_id": source_team_id,
                    "source_team": source_team,
                    "source_row_number": row_number,
                    "reason": collision_reason,
                }
            )

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

    audit_fields = [
        "status",
        "source_file",
        "player_id",
        "source_team_id",
        "source_team",
        "source_row_number",
        "reason",
    ]
    with tmp_audit.open("w", encoding="utf-8-sig", newline="") as h:
        writer = csv.DictWriter(h, fieldnames=audit_fields)
        writer.writeheader()
        writer.writerows(audit)

    os.replace(tmp, OUTPUT)
    os.replace(tmp_audit, AUDIT)

    collisions = sum(
        r["status"] == "DUPLICATE_SOURCE_KEY_PRESERVED"
        for r in audit
    )
    return len(evidence), len(source_fields), collisions


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--season", required=True)
    args = p.parse_args()
    rows, fields, collisions = build(args.season)
    print(f"PLAYER-SEASON EVIDENCE: {rows} rows written")
    print(f"SOURCE NATIVE FIELDS: {fields}")
    print(f"PRESERVED SOURCE-KEY COLLISIONS: {collisions}")
    print(f"Output: {OUTPUT}")
    print(f"Audit: {AUDIT}")
