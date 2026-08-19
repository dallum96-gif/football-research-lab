"""Build the FRL fixture/player evidence layer from approved upstream CSVs.

The builder keeps source-native player-match fields intact and adds only FRL
relationship/provenance columns around them. It is deliberately fail-closed:
unresolved or ambiguous fixtures are reported and are not fabricated.

The documented 2019-20 Manchester City v Arsenal correction is represented as
a known exception rather than invented into a player-match mapping.
"""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path

from player_match_stats import (
    PL_ROOT,
    classify_participation,
    fixture_player_match_rows,
    player_match_id_for_fixture,
    source_player_id,
)

ROOT = Path(__file__).resolve().parent
FIXTURE_FILE = ROOT / "fixtures_master_corrected.csv"
OUTPUT_FILE = ROOT / "data" / "player_match_evidence.csv"
AUDIT_FILE = ROOT / "data" / "player_match_evidence_build_audit.csv"
KNOWN_EXCEPTIONS = {
    ("2019-20", "275"): "Documented Manchester City v Arsenal fixture correction case",
}


def read_csv(path: Path) -> tuple[list[dict], list[str]]:
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                reader = csv.DictReader(handle)
                return list(reader), reader.fieldnames or []
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode CSV: {path}")


def load_fixtures() -> list[dict]:
    rows, fields = read_csv(FIXTURE_FILE)
    required = {
        "season", "fixture_id", "fixture_code", "kickoff_time", "gameweek",
        "home_team_id", "away_team_id", "home_score", "away_score",
    }
    missing = sorted(required - set(fields))
    if missing:
        raise ValueError("Fixture master missing: " + ", ".join(missing))
    return rows


def build(season_filter: str | None = None) -> tuple[int, int, int]:
    if not PL_ROOT.is_dir():
        raise FileNotFoundError(f"Approved upstream source not found: {PL_ROOT}")

    fixtures = load_fixtures()
    if season_filter:
        fixtures = [row for row in fixtures if row["season"] == season_filter]
        if not fixtures:
            raise ValueError(f"No canonical fixtures found for season {season_filter}")

    evidence: list[dict] = []
    audit: list[dict] = []
    duplicate_keys: set[tuple[str, str, str, str]] = set()

    for fixture in fixtures:
        season = fixture["season"]
        fixture_id = fixture["fixture_id"]
        known_reason = KNOWN_EXCEPTIONS.get((season, fixture_id))

        try:
            match_id = player_match_id_for_fixture(fixture)
            if match_id is None:
                status = "KNOWN_EXCEPTION" if known_reason else "UNRESOLVED"
                audit.append({
                    "season": season,
                    "fixture_id": fixture_id,
                    "status": status,
                    "source_match_id": "",
                    "player_rows": "0",
                    "reason": known_reason or "No verified player-match source fixture",
                })
                continue

            rows = fixture_player_match_rows(fixture)
            if not rows:
                status = "KNOWN_EXCEPTION" if known_reason else "NO_PLAYER_ROWS"
                audit.append({
                    "season": season,
                    "fixture_id": fixture_id,
                    "status": status,
                    "source_match_id": match_id,
                    "player_rows": "0",
                    "reason": known_reason or "Source fixture resolved but returned no player rows",
                })
                continue

            row_count = 0
            for row in rows:
                source_id = source_player_id(row) or ""
                source_team_id = str(row.get("team_id") or "").strip()
                participation = classify_participation(row)
                dedupe_key = (season, fixture_id, source_id, match_id)

                if dedupe_key in duplicate_keys:
                    audit.append({
                        "season": season,
                        "fixture_id": fixture_id,
                        "status": "DUPLICATE_SOURCE_ROW",
                        "source_match_id": match_id,
                        "player_rows": "0",
                        "reason": f"Duplicate source player key {source_id}",
                    })
                    continue
                duplicate_keys.add(dedupe_key)

                output = {
                    "frl_season": season,
                    "frl_fixture_id": fixture_id,
                    "frl_fixture_code": fixture.get("fixture_code", ""),
                    "frl_kickoff_time": fixture.get("kickoff_time", ""),
                    "frl_gameweek": fixture.get("gameweek", ""),
                    "frl_home_team_id": fixture.get("home_team_id", ""),
                    "frl_away_team_id": fixture.get("away_team_id", ""),
                    "frl_source_match_id": match_id,
                    "frl_source_player_id": source_id,
                    "frl_source_team_id": source_team_id,
                    "frl_participation_status": participation,
                    "frl_source_file": row.get("_source_file", ""),
                }

                for key, value in row.items():
                    if key == "_source_file":
                        continue
                    output.setdefault(f"source_{key}", value)

                evidence.append(output)
                row_count += 1

            audit.append({
                "season": season,
                "fixture_id": fixture_id,
                "status": "RESOLVED",
                "source_match_id": match_id,
                "player_rows": str(row_count),
                "reason": "",
            })

        except (ValueError, KeyError) as exc:
            status = "KNOWN_EXCEPTION" if known_reason else "ERROR"
            audit.append({
                "season": season,
                "fixture_id": fixture_id,
                "status": status,
                "source_match_id": "",
                "player_rows": "0",
                "reason": known_reason or str(exc),
            })

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp_output = OUTPUT_FILE.with_suffix(".tmp.csv")
    temp_audit = AUDIT_FILE.with_suffix(".tmp.csv")

    if evidence:
        columns = list(evidence[0].keys())
        for row in evidence[1:]:
            for key in row:
                if key not in columns:
                    columns.append(key)
        with temp_output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(evidence)
    else:
        temp_output.write_text("", encoding="utf-8")

    audit_columns = [
        "season", "fixture_id", "status", "source_match_id", "player_rows", "reason",
    ]
    with temp_audit.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=audit_columns)
        writer.writeheader()
        writer.writerows(audit)

    os.replace(temp_output, OUTPUT_FILE)
    os.replace(temp_audit, AUDIT_FILE)

    unresolved = sum(
        row["status"] in {"UNRESOLVED", "ERROR", "NO_PLAYER_ROWS", "DUPLICATE_SOURCE_ROW"}
        for row in audit
    )
    known = sum(row["status"] == "KNOWN_EXCEPTION" for row in audit)
    return len(evidence), unresolved, known


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", help="Build one canonical season only")
    args = parser.parse_args()

    row_count, unresolved, known = build(args.season)
    print(f"PLAYER-MATCH EVIDENCE: {row_count} player-match rows written")
    print(f"KNOWN EXCEPTIONS: {known}")
    print(f"UNRESOLVED/ERROR STATES: {unresolved}")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Audit: {AUDIT_FILE}")

    if unresolved:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
