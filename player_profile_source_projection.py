"""Pinned same-representation Player-Season evidence for Player Profile.

Player Profile uses one Player-Season representation for descriptive
participation and for all six MID V1 comparison axes. Per-90 metrics use that
same representation's ``timePlayed`` denominator, preventing source-native
numerators from being divided by a different product's participation minutes.
"""
from __future__ import annotations

import csv
import json
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACKAGED = ROOT / "data" / "player_profile_source_stats_v1.csv"
METADATA = ROOT / "data" / "player_profile_source_stats_v1.metadata.json"

PARTICIPATION_FIELDS = (
    "source_appearances",
    "source_starts",
    "source_minutes",
)

PROFILE_METRICS = (
    {
        "key": "xg_per_90",
        "source_key": "expected_goals",
        "label": "Goal threat",
        "metric_label": "Expected goals / 90",
        "unit": "xG",
    },
    {
        "key": "xa_per_90",
        "source_key": "expected_assists",
        "label": "Chance creation",
        "metric_label": "Expected assists / 90",
        "unit": "xA",
    },
    {
        "key": "accurate_opposition_half_passes_per_90",
        "source_key": "accurate_opposition_half_passes",
        "label": "Advanced passing",
        "metric_label": "Accurate opposition-half passes / 90",
        "unit": "passes",
    },
    {
        "key": "forward_passes_per_90",
        "source_key": "forward_passes",
        "label": "Forward passing",
        "metric_label": "Forward passes / 90",
        "unit": "passes",
    },
    {
        "key": "recoveries_per_90",
        "source_key": "recoveries",
        "label": "Recoveries",
        "metric_label": "Recoveries / 90",
        "unit": "recoveries",
    },
    {
        "key": "tackles_won_per_90",
        "source_key": "tackles_won",
        "label": "Ball winning",
        "metric_label": "Tackles won / 90",
        "unit": "tackles",
    },
)


def _number(value: object) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


@lru_cache(maxsize=1)
def _rows() -> tuple[dict[str, str], ...]:
    if not PACKAGED.is_file():
        return tuple()
    with PACKAGED.open("r", encoding="utf-8-sig", newline="") as handle:
        return tuple(dict(row) for row in csv.DictReader(handle))


@lru_cache(maxsize=1)
def metadata() -> dict:
    if not METADATA.is_file():
        return {}
    return json.loads(METADATA.read_text(encoding="utf-8"))


@lru_cache(maxsize=20)
def season_rows(season: str) -> dict[str, dict]:
    output: dict[str, dict] = {}
    for row in _rows():
        if str(row.get("season") or "").strip() != season:
            continue
        source_player_id = str(row.get("source_player_id") or "").strip()
        if not source_player_id:
            continue
        output[source_player_id] = {
            "source_player_id": source_player_id,
            "source_player_name": str(row.get("source_player_name") or "").strip() or None,
            "source_position": str(row.get("source_position") or "").strip() or None,
            **{
                field: _number(row.get(field))
                for field in PARTICIPATION_FIELDS
            },
            **{
                definition["source_key"]: _number(row.get(definition["source_key"]))
                for definition in PROFILE_METRICS
            },
        }
    return output


def per_90(row: dict, source_key: str) -> float | None:
    numerator = _number(row.get(source_key))
    minutes = _number(row.get("source_minutes"))
    if numerator is None or minutes in (None, 0):
        return None
    return numerator / minutes * 90.0


def complete_participation(row: dict | None) -> dict[str, int] | None:
    """Return source-native participation only when all three fields exist."""
    if row is None:
        return None
    values = {field: _number(row.get(field)) for field in PARTICIPATION_FIELDS}
    if any(value is None for value in values.values()):
        return None
    return {
        "appearances": int(float(values["source_appearances"] or 0)),
        "starts": int(float(values["source_starts"] or 0)),
        "minutes": int(float(values["source_minutes"] or 0)),
    }


def clear_caches() -> None:
    _rows.cache_clear()
    metadata.cache_clear()
    season_rows.cache_clear()


__all__ = [
    "METADATA",
    "PACKAGED",
    "PARTICIPATION_FIELDS",
    "PROFILE_METRICS",
    "clear_caches",
    "complete_participation",
    "metadata",
    "per_90",
    "season_rows",
]
