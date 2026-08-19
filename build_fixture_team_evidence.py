"""Build complete canonical fixture/team evidence from approved PL events CSVs.

Output grain: one row per (season, fixture_id, venue).
Every upstream source-native events_stats field is preserved under source_*.
The existing curated fixture_match_stats.csv remains untouched for compatibility.
"""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path

from match_stats import PL_ROOT, fixture_source_match
from query_lab import load_identity_registry

ROOT = Path(__file__).resolve().parent
FIXTURE_FILE = ROOT / "fixtures_master_corrected.csv"
OUTPUT_FILE = ROOT / "data" / "fixture_team_evidence.csv"
AUDIT_FILE = ROOT / "data" / "fixture_team_evidence_build_audit.csv"

FIXTURE_FIELDS = (
    "season", "fixture_id", "fixture_code", "kickoff_time", "gameweek",
    "home_team_id", "away_team_id", "home_score", "away_score",
)


def read_csv(path: Path):
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                reader = csv.DictReader(handle)
                return list(reader), reader.fieldnames or []
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode CSV: {path}")


def load_fixtures():
    rows, fields = read_csv(FIXTURE_FILE)
    missing = sorted(set(FIXTURE_FIELDS) - set(fields))
    if missing:
        raise ValueError("Fixture master missing: " + ", ".join(missing))
    return rows


def load_identity():
    return load_identity_registry()


def build(season_filter: str | None = None):
    if not PL_ROOT.is_dir():
        raise FileNotFoundError(f"Approved upstream source not found: {PL_ROOT}")

    fixtures = load_fixtures()
    if season_filter:
        fixtures = [r for r in fixtures if r["season"] == season_filter]
        if not fixtures:
            raise ValueError(f"No canonical fixtures found for season {season_filter}")

    identities = load_identity()
    evidence = []
    audit = []
    seen = set()
    source_fields = set()

    for fixture in fixtures:
        season = fixture["season"]
        fixture_id = fixture["fixture_id"]
        key = (season, fixture_id)
        try:
            resolved = fixture_source_match(fixture, identities)
            if resolved is None:
                audit.append({"season": season, "fixture_id": fixture_id, "status": "UNRESOLVED", "source_match_id": "", "reason": "No verified events_stats fixture"})
                continue

            match_id, home_row, away_row = resolved
            for venue, row in (("home", home_row), ("away", away_row)):
                row_key = (season, fixture_id, venue)
                if row_key in seen:
                    raise ValueError(f"Duplicate fixture/team evidence key: {row_key}")
                seen.add(row_key)
                for field in row:
                    if field not in {"_source_file"}:
                        source_fields.add(field)

                output = {
                    "frl_season": season,
                    "frl_fixture_id": fixture_id,
                    "frl_fixture_code": fixture.get("fixture_code", ""),
                    "frl_kickoff_time": fixture.get("kickoff_time", ""),
                    "frl_gameweek": fixture.get("gameweek", ""),
                    "frl_home_team_id": fixture.get("home_team_id", ""),
                    "frl_away_team_id": fixture.get("away_team_id", ""),
                    "frl_venue": venue,
                    "frl_source_match_id": match_id,
                    "frl_source_file": row.get("_source_file", ""),
                }
                for field, value in row.items():
                    if field == "_source_file":
                        continue
                    output[f"source_{field}"] = value
                evidence.append(output)

            audit.append({"season": season, "fixture_id": fixture_id, "status": "RESOLVED", "source_match_id": match_id, "reason": ""})
        except (ValueError, KeyError) as exc:
            audit.append({"season": season, "fixture_id": fixture_id, "status": "ERROR", "source_match_id": "", "reason": str(exc)})

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp_output = OUTPUT_FILE.with_suffix(".tmp.csv")
    tmp_audit = AUDIT_FILE.with_suffix(".tmp.csv")

    if evidence:
        columns = list(evidence[0].keys())
        for row in evidence[1:]:
            for field in row:
                if field not in columns:
                    columns.append(field)
        with tmp_output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(evidence)
    else:
        tmp_output.write_text("", encoding="utf-8")

    with tmp_audit.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["season", "fixture_id", "status", "source_match_id", "reason"])
        writer.writeheader()
        writer.writerows(audit)

    os.replace(tmp_output, OUTPUT_FILE)
    os.replace(tmp_audit, AUDIT_FILE)

    unresolved = sum(r["status"] != "RESOLVED" for r in audit)
    return len(evidence), len(source_fields), unresolved


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--season")
    args = parser.parse_args()
    rows, fields, issues = build(args.season)
    print(f"FIXTURE-TEAM EVIDENCE: {rows} team-match rows written")
    print(f"SOURCE NATIVE FIELDS: {fields}")
    print(f"UNRESOLVED/ERROR STATES: {issues}")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Audit: {AUDIT_FILE}")
    if issues:
        raise SystemExit(1)
