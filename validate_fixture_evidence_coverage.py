"""Audit fixture-evidence coverage across the canonical fixture universe.

This is a read-only validation gate. It requires the preserved PulseLive
archive configured by FRL_PULSELIVE_ARCHIVE_ROOT (or the documented local
fallback) and never mutates canonical data.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Any

import query_api

ROOT = Path(__file__).resolve().parent
FIXTURE_FILE = ROOT / "fixtures_master_corrected.csv"


def _load_fixtures() -> list[dict[str, str]]:
    with FIXTURE_FILE.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _coverage_status(value: Any) -> str | None:
    """Read the status from either a scalar status or an object envelope."""
    if isinstance(value, dict):
        status = value.get("status")
        return str(status) if status is not None else None
    if value is None:
        return None
    return str(value)


def _formation_status(value: Any, side: str) -> str | None:
    if not isinstance(value, dict):
        return None
    side_value = value.get(side)
    if isinstance(side_value, dict):
        return _coverage_status(side_value)
    return _coverage_status(side_value)


def validate() -> dict[str, int]:
    fixtures = _load_fixtures()
    counts = Counter()

    for fixture in fixtures:
        season = str(fixture["season"])
        fixture_id = str(fixture["fixture_id"])
        counts["fixtures_examined"] += 1
        try:
            result = query_api.fixture_evidence(season, fixture_id)
        except Exception:
            counts["fixture_resolution_or_evidence_failures"] += 1
            continue

        counts[f"status:{result.get('status', 'UNKNOWN')}"] += 1
        coverage = result.get("coverage", {})
        if _coverage_status(coverage.get("events")) == "AVAILABLE":
            counts["fixtures_with_event_evidence"] += 1
        else:
            counts["fixtures_without_event_evidence"] += 1

        if _coverage_status(coverage.get("lineup")) == "AVAILABLE":
            counts["fixtures_with_lineup_evidence"] += 1
        else:
            counts["fixtures_without_lineup_evidence"] += 1

        if all(_formation_status(coverage.get("formation"), side) == "AVAILABLE" for side in ("home", "away")):
            counts["fixtures_with_both_formations"] += 1
        else:
            counts["fixtures_without_both_formations"] += 1

        if _coverage_status(coverage.get("managers")) == "AVAILABLE":
            counts["fixtures_with_managers"] += 1
        else:
            counts["fixtures_without_managers"] += 1

        for event in result.get("events", []):
            for player_key in ("primary_player", "secondary_player"):
                player = event.get(player_key) or {}
                if player.get("identity_status") in {"AMBIGUOUS", "CONTRADICTORY", "UNRESOLVED"}:
                    counts["event_identity_failures"] += 1

        for player in result.get("lineup", []):
            identity_status = (player.get("player") or {}).get("identity_status")
            if identity_status in {"AMBIGUOUS", "CONTRADICTORY", "UNRESOLVED"}:
                counts["lineup_identity_failures"] += 1

    return dict(counts)


if __name__ == "__main__":
    import json
    print(json.dumps(validate(), indent=2, sort_keys=True))
