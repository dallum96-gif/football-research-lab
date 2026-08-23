"""Assure the frozen V1 variable/entity attachment materialisation.

Checks the additive V1 output only. It does not alter data, perform identity
resolution, or promote any source identity into canonical identity.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data" / "entity_attachments_v1"

EXPECTED_ROWS = {
    "variable.csv": 447,
    "team_match_observation.csv": 7598,
    "player_match_observation.csv": 145571,
    "player_season_observation.csv": 3963,
    "squad_observation.csv": 42,
}

ALLOWED = {"VERIFIED", "REVIEW", "UNRESOLVED", "NOT_APPLICABLE"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> None:
    print("FRL VARIABLE -> ENTITY ATTACHMENT SCHEMA V1 ASSURANCE")
    print("=" * 88)

    total_failures = 0
    rows_by_file: dict[str, list[dict[str, str]]] = {}

    for filename, expected in EXPECTED_ROWS.items():
        path = OUT / filename
        if not path.exists():
            print(f"FAIL  {filename}: missing")
            total_failures += 1
            continue
        rows = read(path)
        rows_by_file[filename] = rows
        status = "PASS" if len(rows) == expected else "FAIL"
        print(f"{status}  {filename}: rows={len(rows):,} expected={expected:,}")
        if status == "FAIL":
            total_failures += 1

    # V1 attachment status vocabulary.
    for filename in (
        "team_match_observation.csv",
        "player_match_observation.csv",
        "player_season_observation.csv",
        "squad_observation.csv",
    ):
        for row in rows_by_file.get(filename, []):
            for key, value in row.items():
                if key.endswith("_attachment_status") and value not in ALLOWED:
                    print(f"FAIL  {filename}: invalid {key}={value!r}")
                    total_failures += 1

    # Player-Match invariants established during discovery.
    pm = rows_by_file.get("player_match_observation.csv", [])
    fixture_verified = sum(r.get("fixture_attachment_status") == "VERIFIED" for r in pm)
    home_verified = sum(r.get("home_team_attachment_status") == "VERIFIED" for r in pm)
    away_verified = sum(r.get("away_team_attachment_status") == "VERIFIED" for r in pm)
    source_player_verified = sum(r.get("source_player_identity_status") == "VERIFIED" for r in pm)
    fully_attached = sum(
        r.get("fixture_attachment_status") == "VERIFIED"
        and r.get("home_team_attachment_status") == "VERIFIED"
        and r.get("away_team_attachment_status") == "VERIFIED"
        and r.get("player_attachment_status") == "VERIFIED"
        for r in pm
    )

    print()
    print("PLAYER-MATCH INVARIANTS")
    print(f"  fixture verified:       {fixture_verified:,} / {len(pm):,}")
    print(f"  home team verified:     {home_verified:,} / {len(pm):,}")
    print(f"  away team verified:     {away_verified:,} / {len(pm):,}")
    print(f"  source player verified:  {source_player_verified:,} / {len(pm):,}")
    print(f"  fully attached:          {fully_attached:,} / {len(pm):,}")

    if pm and not (fixture_verified == home_verified == away_verified == source_player_verified == len(pm)):
        print("FAIL  Player-Match independently verified fixture/team/source-player edges lost")
        total_failures += 1

    # A canonical Player attachment may only exist with VERIFIED status.
    bad_player_entity = sum(
        bool(r.get("player_entity_id")) and r.get("player_attachment_status") != "VERIFIED"
        for rows in rows_by_file.values()
        for r in rows
        if "player_attachment_status" in r
    )
    print(f"  non-verified rows carrying canonical player entity id: {bad_player_entity}")
    if bad_player_entity:
        print("FAIL  canonical player entity appears without VERIFIED attachment status")
        total_failures += bad_player_entity

    print()
    if total_failures:
        print(f"ASSURANCE RESULT: FAIL ({total_failures} issues)")
        raise SystemExit(1)
    print("ASSURANCE RESULT: PASS")
    print("Frozen V1 schema preserved; no identity promotion performed.")


if __name__ == "__main__":
    main()
