"""Pinned same-representation Player-Season evidence for Player Profile.

Player Profile uses one Player-Season representation for descriptive
participation and position-specific comparison axes. Per-90 metrics use that
same representation's ``timePlayed`` denominator; ratios use only source-native
fields from the same Player-Season row. Missing source fields stay unavailable.
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

PROFILE_SOURCE_FIELDS = (
    "expected_goals",
    "expected_assists",
    "goals",
    "accurate_opposition_half_passes",
    "forward_passes",
    "recoveries",
    "tackles_won",
    "total_tackles",
    "interceptions",
    "total_clearances",
    "aerial_duels",
    "aerial_duels_won",
    "total_shots",
    "total_touches_in_opposition_box",
    "successful_dribbles",
    "expected_goals_on_target_conceded",
    "goals_conceded",
    "saves_made",
    "catches",
    "punches",
    "goalkeeper_smothers",
    "gk_successful_distribution",
    "gk_unsuccessful_distribution",
)

POSITION_PROFILE_METRICS = {
    "GKP": (
        {"key": "goals_prevented_per_90", "label": "Shot stopping", "metric_label": "xGOT prevented / 90", "unit": "goals", "calculation": "difference_per_90", "positive_key": "expected_goals_on_target_conceded", "negative_key": "goals_conceded", "denominator": "timePlayed", "higher_is_better": True},
        {"key": "save_percentage", "label": "Save rate", "metric_label": "Save percentage", "unit": "%", "calculation": "share_pct", "numerator_key": "saves_made", "denominator_keys": ("saves_made", "goals_conceded"), "denominator": "savesMade + goalsConceded", "higher_is_better": True},
        {"key": "saves_per_90", "label": "Save volume", "metric_label": "Saves / 90", "unit": "saves", "calculation": "per_90", "source_key": "saves_made", "denominator": "timePlayed", "higher_is_better": True},
        {"key": "claims_per_90", "label": "Claiming", "metric_label": "Catches + punches / 90", "unit": "claims", "calculation": "sum_per_90", "source_keys": ("catches", "punches"), "denominator": "timePlayed", "higher_is_better": True},
        {"key": "smothers_per_90", "label": "Smothering", "metric_label": "Goalkeeper smothers / 90", "unit": "smothers", "calculation": "per_90", "source_key": "goalkeeper_smothers", "denominator": "timePlayed", "higher_is_better": True},
        {"key": "distribution_success_pct", "label": "Distribution", "metric_label": "Goalkeeper distribution success", "unit": "%", "calculation": "share_pct", "numerator_key": "gk_successful_distribution", "denominator_keys": ("gk_successful_distribution", "gk_unsuccessful_distribution"), "denominator": "successful + unsuccessful goalkeeper distribution", "higher_is_better": True},
    ),
    "DEF": (
        {"key": "aerial_duel_win_pct", "label": "Aerial duels", "metric_label": "Aerial duel win percentage", "unit": "%", "calculation": "ratio_pct", "numerator_key": "aerial_duels_won", "denominator_key": "aerial_duels", "denominator": "aerialDuels", "higher_is_better": True},
        {"key": "tackle_success_pct", "label": "Tackling", "metric_label": "Tackle success percentage", "unit": "%", "calculation": "ratio_pct", "numerator_key": "tackles_won", "denominator_key": "total_tackles", "denominator": "totalTackles", "higher_is_better": True},
        {"key": "interceptions_per_90", "label": "Interceptions", "metric_label": "Interceptions / 90", "unit": "interceptions", "calculation": "per_90", "source_key": "interceptions", "denominator": "timePlayed", "higher_is_better": True},
        {"key": "clearances_per_90", "label": "Clearances", "metric_label": "Clearances / 90", "unit": "clearances", "calculation": "per_90", "source_key": "total_clearances", "denominator": "timePlayed", "higher_is_better": True},
        {"key": "recoveries_per_90", "label": "Recoveries", "metric_label": "Recoveries / 90", "unit": "recoveries", "calculation": "per_90", "source_key": "recoveries", "denominator": "timePlayed", "higher_is_better": True},
        {"key": "forward_passes_per_90", "label": "Progression", "metric_label": "Forward passes / 90", "unit": "passes", "calculation": "per_90", "source_key": "forward_passes", "denominator": "timePlayed", "higher_is_better": True},
    ),
    "MID": (
        {"key": "xg_per_90", "label": "Goal threat", "metric_label": "Expected goals / 90", "unit": "xG", "calculation": "per_90", "source_key": "expected_goals", "denominator": "timePlayed", "higher_is_better": True},
        {"key": "xa_per_90", "label": "Chance creation", "metric_label": "Expected assists / 90", "unit": "xA", "calculation": "per_90", "source_key": "expected_assists", "denominator": "timePlayed", "higher_is_better": True},
        {"key": "accurate_opposition_half_passes_per_90", "label": "Advanced passing", "metric_label": "Accurate opposition-half passes / 90", "unit": "passes", "calculation": "per_90", "source_key": "accurate_opposition_half_passes", "denominator": "timePlayed", "higher_is_better": True},
        {"key": "forward_passes_per_90", "label": "Forward passing", "metric_label": "Forward passes / 90", "unit": "passes", "calculation": "per_90", "source_key": "forward_passes", "denominator": "timePlayed", "higher_is_better": True},
        {"key": "recoveries_per_90", "label": "Recoveries", "metric_label": "Recoveries / 90", "unit": "recoveries", "calculation": "per_90", "source_key": "recoveries", "denominator": "timePlayed", "higher_is_better": True},
        {"key": "tackles_won_per_90", "label": "Ball winning", "metric_label": "Tackles won / 90", "unit": "tackles", "calculation": "per_90", "source_key": "tackles_won", "denominator": "timePlayed", "higher_is_better": True},
    ),
    "FWD": (
        {"key": "xg_per_90", "label": "Goal threat", "metric_label": "Expected goals / 90", "unit": "xG", "calculation": "per_90", "source_key": "expected_goals", "denominator": "timePlayed", "higher_is_better": True},
        {"key": "goals_per_90", "label": "Scoring", "metric_label": "Goals / 90", "unit": "goals", "calculation": "per_90", "source_key": "goals", "denominator": "timePlayed", "higher_is_better": True},
        {"key": "xa_per_90", "label": "Chance creation", "metric_label": "Expected assists / 90", "unit": "xA", "calculation": "per_90", "source_key": "expected_assists", "denominator": "timePlayed", "higher_is_better": True},
        {"key": "shots_per_90", "label": "Shot volume", "metric_label": "Shots / 90", "unit": "shots", "calculation": "per_90", "source_key": "total_shots", "denominator": "timePlayed", "higher_is_better": True},
        {"key": "box_touches_per_90", "label": "Box presence", "metric_label": "Touches in opposition box / 90", "unit": "touches", "calculation": "per_90", "source_key": "total_touches_in_opposition_box", "denominator": "timePlayed", "higher_is_better": True},
        {"key": "successful_dribbles_per_90", "label": "1v1 threat", "metric_label": "Successful dribbles / 90", "unit": "dribbles", "calculation": "per_90", "source_key": "successful_dribbles", "denominator": "timePlayed", "higher_is_better": True},
    ),
}

PROFILE_METRICS = POSITION_PROFILE_METRICS["MID"]


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
            **{field: _number(row.get(field)) for field in PARTICIPATION_FIELDS},
            **{field: _number(row.get(field)) for field in PROFILE_SOURCE_FIELDS},
        }
    return output


def per_90(row: dict, source_key: str) -> float | None:
    numerator = _number(row.get(source_key))
    minutes = _number(row.get("source_minutes"))
    if numerator is None or minutes in (None, 0):
        return None
    return numerator / minutes * 90.0


def metric_value(row: dict, definition: dict) -> float | None:
    calculation = str(definition.get("calculation") or "")
    if calculation == "per_90":
        return per_90(row, str(definition["source_key"]))
    if calculation == "sum_per_90":
        values = [_number(row.get(key)) for key in definition["source_keys"]]
        minutes = _number(row.get("source_minutes"))
        if any(value is None for value in values) or minutes in (None, 0):
            return None
        return sum(float(value) for value in values if value is not None) / minutes * 90.0
    if calculation == "difference_per_90":
        positive = _number(row.get(definition["positive_key"]))
        negative = _number(row.get(definition["negative_key"]))
        minutes = _number(row.get("source_minutes"))
        if positive is None or negative is None or minutes in (None, 0):
            return None
        return (positive - negative) / minutes * 90.0
    if calculation == "ratio_pct":
        numerator = _number(row.get(definition["numerator_key"]))
        denominator = _number(row.get(definition["denominator_key"]))
        if numerator is None or denominator in (None, 0):
            return None
        return numerator / denominator * 100.0
    if calculation == "share_pct":
        numerator = _number(row.get(definition["numerator_key"]))
        denominator_values = [_number(row.get(key)) for key in definition["denominator_keys"]]
        if numerator is None or any(value is None for value in denominator_values):
            return None
        denominator = sum(float(value) for value in denominator_values if value is not None)
        if denominator == 0:
            return None
        return numerator / denominator * 100.0
    raise ValueError(f"Unsupported Player Profile metric calculation: {calculation}")


def profile_metrics_for_position(position: str) -> tuple[dict, ...]:
    return POSITION_PROFILE_METRICS.get(str(position or "").upper(), tuple())


def complete_participation(row: dict | None) -> dict[str, int] | None:
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
    "POSITION_PROFILE_METRICS",
    "PROFILE_METRICS",
    "PROFILE_SOURCE_FIELDS",
    "clear_caches",
    "complete_participation",
    "metadata",
    "metric_value",
    "per_90",
    "profile_metrics_for_position",
    "season_rows",
]
