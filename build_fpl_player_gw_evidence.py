"""Build complete official-FPL-derived player/gameweek evidence.

Source boundary: the local Premier-League-Stats FPL CSVs only.
Output grain: one upstream player/gameweek record.
All source-native fields are preserved under source_*.
"""
from __future__ import annotations
import argparse
import csv
import os
from pathlib import Path

UPSTREAM_ROOT = Path(r"C:\Users\dlall\football_database\Premier-League-Stats\fpl_scraper\fpl_stats")
ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "data" / "fpl_player_gw_evidence.csv"
AUDIT = ROOT / "data" / "fpl_player_gw_evidence_build_audit.csv"


def read_csv(path: Path):
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with path.open("r", encoding=encoding, newline="") as h:
                r = csv.DictReader(h)
                return list(r), r.fieldnames or []
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode CSV: {path}")


def source_file(season: str) -> Path:
    return UPSTREAM_ROOT / "_merged" / "players" / f"{season}_all_players_gw.csv"


def build(season: str):
    path = source_file(season)
    if not path.is_file():
        raise FileNotFoundError(f"Approved FPL source not found: {path}")
    rows, fields = read_csv(path)
    evidence = []
    audit = []
    seen = set()
    for row in rows:
        player = str(row.get("element", row.get("player_id", ""))).strip()
        gw = str(row.get("round", row.get("gameweek", ""))).strip()
        key = (season, player, gw, str(row.get("fixture", "")).strip())
        if key in seen:
            audit.append({"status": "DUPLICATE_SOURCE_ROW", "source_file": str(path), "player_id": player, "gameweek": gw, "reason": "Duplicate FPL player/gameweek key"})
            continue
        seen.add(key)
        out = {
            "frl_season": season,
            "frl_fpl_source_file": str(path),
            "frl_fpl_player_key": player,
            "frl_fpl_gameweek": gw,
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
        w = csv.DictWriter(h, fieldnames=cols, extrasaction="ignore")
        w.writeheader(); w.writerows(evidence)
    with tmp_audit.open("w", encoding="utf-8-sig", newline="") as h:
        w = csv.DictWriter(h, fieldnames=["status", "source_file", "player_id", "gameweek", "reason"])
        w.writeheader(); w.writerows(audit)
    os.replace(tmp, OUTPUT); os.replace(tmp_audit, AUDIT)
    issues = sum(r["status"] != "RESOLVED" for r in audit)
    return len(evidence), len(fields), issues


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--season", required=True); args = p.parse_args()
    rows, fields, issues = build(args.season)
    print(f"FPL PLAYER-GW EVIDENCE: {rows} rows written")
    print(f"SOURCE NATIVE FIELDS: {fields}")
    print(f"DUPLICATE/ERROR STATES: {issues}")
    print(f"Output: {OUTPUT}"); print(f"Audit: {AUDIT}")
    if issues: raise SystemExit(1)
