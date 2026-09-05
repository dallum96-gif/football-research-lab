"""Source-native research access for the complete PulseLive team-stat payload.

This is deliberately broader than the canonical scalar registry. It gives FRL a
single governed pathway to any of the 249 audited team-match raw fields while
preserving the raw representation and missingness. A routed raw field is not
thereby declared semantically equivalent to a canonical FRL variable.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from pulselive_fixture_evidence import load_snapshot, resource_meta, resource_payload
from source_family_adapters import canonical_fixture, resolve_source_match

ROOT = Path(__file__).resolve().parent
FIELD_INDEX = ROOT / "data" / "pulselive_team_stat_raw_field_index.json"


class RawTeamStatUnavailableError(ValueError):
    pass


@lru_cache(maxsize=1)
def raw_field_paths() -> dict[str, str]:
    payload = json.loads(FIELD_INDEX.read_text(encoding="utf-8"))
    fields = {str(k): str(v) for k, v in dict(payload.get("field_paths") or {}).items()}
    expected = int(payload.get("team_match_raw_field_count") or 0)
    if expected != 249 or len(fields) != 249:
        raise RuntimeError(f"Expected exhaustive 249-field raw team index; found {len(fields)}")
    return fields


def raw_team_stat_fields() -> tuple[str, ...]:
    return tuple(sorted(raw_field_paths()))


def _rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        for key in ("content", "items", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return [row for row in value if isinstance(row, dict)]
    return []


def _value_at_path(row: dict[str, Any], raw_path: str) -> tuple[bool, Any]:
    path = raw_path
    if path.startswith("[]."):
        path = path[3:]
    current: Any = row
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return False, None
        current = current[part]
    return True, current


def fixture_raw_team_stat_values(
    season: str,
    fixture_id: str,
    field: str,
    *,
    team_id: str | None = None,
) -> dict[str, Any]:
    paths = raw_field_paths()
    if field not in paths:
        raise RawTeamStatUnavailableError(f"Unknown audited PulseLive team-stat field: {field}")

    fixture = canonical_fixture(season, fixture_id)
    if fixture is None:
        raise RawTeamStatUnavailableError(f"Canonical fixture not found: {season}/{fixture_id}")
    resolved = resolve_source_match(season, fixture_id)
    source_match_id = str(resolved["source_match_id"])
    snapshot, snapshot_path = load_snapshot(source_match_id)
    if snapshot is None or snapshot_path is None:
        raise RawTeamStatUnavailableError(
            f"Preserved PulseLive snapshot unavailable for source match {source_match_id}."
        )

    payload = resource_payload(snapshot, "stats")
    results: list[dict[str, Any]] = []
    for row in _rows(payload):
        side = str(row.get("side") or "").strip().lower()
        frl_team_id = (
            str(fixture.get("home_team_id") or "").strip()
            if side == "home"
            else str(fixture.get("away_team_id") or "").strip()
            if side == "away"
            else ""
        )
        if team_id is not None and frl_team_id != str(team_id).strip():
            continue
        present, value = _value_at_path(row, paths[field])
        results.append({
            "season": season,
            "fixture_id": str(fixture_id),
            "source_match_id": source_match_id,
            "side": side or None,
            "frl_team_id": frl_team_id or None,
            "source_team_id": str(row.get("teamId") or "").strip() or None,
            "source_field": field,
            "raw_path": paths[field],
            "field_present": present,
            "value": value if present else None,
        })

    return {
        "query_type": "raw_team_stat_evidence",
        "family": "team_match_raw",
        "season": season,
        "fixture_id": str(fixture_id),
        "field": field,
        "source_rows": len(results),
        "results": results,
        "provenance": {
            "source_family": "PulseLive preserved match-centre snapshot",
            "resource": "stats",
            "snapshot_path": str(snapshot_path),
            "resource_meta": resource_meta(snapshot, "stats"),
            "fixture_relationship_status": resolved.get("relationship_status"),
            "fixture_resolution_basis": resolved.get("resolution_basis"),
        },
        "limitations": [
            "This is source-native raw evidence, not automatic canonical-variable promotion.",
            "A field absent from a snapshot remains absent; absence is never converted to zero here.",
            "Seasonal/partial coverage is allowed and remains visible rather than excluding the field.",
        ],
    }


__all__ = [
    "RawTeamStatUnavailableError",
    "fixture_raw_team_stat_values",
    "raw_field_paths",
    "raw_team_stat_fields",
]
