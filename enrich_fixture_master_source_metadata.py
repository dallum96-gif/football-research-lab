"""Add verified source metadata columns to the canonical fixture master.

The existing fixture identity columns remain unchanged. The new fields are
source-backed convenience columns so future consumers can use stadium,
attendance and half-time state without rebuilding the source bridge.
Unresolved fixtures are left blank and reported in a sidecar audit.
"""
from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path

from match_stats import fixture_source_match
from query_lab import load_identity_registry

ROOT = Path(__file__).resolve().parent
FIXTURE_FILE = ROOT / "fixtures_master_corrected.csv"
AUDIT_FILE = ROOT / "identity" / "data_quality" / "fixture_source_metadata_audit.csv"

NEW_FIELDS = (
    "source_match_id",
    "stadium",
    "attendance",
    "half_time_home_score",
    "half_time_away_score",
    "source_home_result",
    "source_away_result",
    "source_kickoff",
    "source_metadata_status",
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


def _same_or_blank(left: str | None, right: str | None) -> bool:
    return left in (None, "") or right in (None, "") or str(left).strip() == str(right).strip()


def enrich(season_filter: str | None = None) -> tuple[int, int]:
    rows, columns = read_csv(FIXTURE_FILE)
    identities = load_identity_registry()

    for field in NEW_FIELDS:
        if field not in columns:
            columns.append(field)

    audit = []
    enriched = 0

    for row in rows:
        if season_filter and row.get("season") != season_filter:
            continue

        season = row["season"]
        fixture_id = row["fixture_id"]
        status = "UNRESOLVED"
        reason = ""
        source_match_id = ""

        try:
            resolved = fixture_source_match(row, identities)
            if resolved is None:
                reason = "No verified events_stats source match"
            else:
                source_match_id, home, away = resolved
                ground = home.get("ground") or away.get("ground") or ""
                attendance = home.get("attendance") or away.get("attendance") or ""

                if not _same_or_blank(home.get("ground"), away.get("ground")):
                    raise ValueError("Home/away source rows disagree on ground")
                if not _same_or_blank(home.get("attendance"), away.get("attendance")):
                    raise ValueError("Home/away source rows disagree on attendance")

                row["source_match_id"] = str(source_match_id)
                row["stadium"] = ground
                row["attendance"] = attendance
                row["half_time_home_score"] = home.get("halfTimeFor", "")
                row["half_time_away_score"] = away.get("halfTimeFor", "")
                row["source_home_result"] = home.get("result", "")
                row["source_away_result"] = away.get("result", "")
                row["source_kickoff"] = home.get("kickoff", "") or away.get("kickoff", "")
                row["source_metadata_status"] = "VERIFIED"
                enriched += 1
                status = "VERIFIED"
        except (KeyError, ValueError) as exc:
            reason = str(exc)

        if status != "VERIFIED":
            for field in NEW_FIELDS:
                if field != "source_metadata_status":
                    row[field] = row.get(field, "")
            row["source_metadata_status"] = status

        audit.append({
            "season": season,
            "fixture_id": fixture_id,
            "status": status,
            "source_match_id": source_match_id,
            "reason": reason,
        })

    tmp = FIXTURE_FILE.with_suffix(".metadata.tmp.csv")
    with tmp.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(tmp, FIXTURE_FILE)

    AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp_audit = AUDIT_FILE.with_suffix(".tmp.csv")
    with tmp_audit.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["season", "fixture_id", "status", "source_match_id", "reason"])
        writer.writeheader()
        writer.writerows(audit)
    os.replace(tmp_audit, AUDIT_FILE)

    return enriched, len(audit) - enriched


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--season")
    args = parser.parse_args()
    verified, unresolved = enrich(args.season)
    print(f"FIXTURE SOURCE METADATA: {verified} verified fixtures enriched")
    print(f"UNRESOLVED: {unresolved}")
    print(f"Audit: {AUDIT_FILE}")
    if unresolved:
        raise SystemExit(1)
