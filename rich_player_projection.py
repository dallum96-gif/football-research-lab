"""Governed packaged player-season projection for Product/analysis use.

Runtime code reads only the tracked/materialised FRL projection under ``data``.
The preserved provider folders are touched only by the dedicated materialiser.
Identity is the audited PulseLive/FPL ``pl_code`` bridge, never player name.

Source blanks remain unavailable unless their zero semantics have been audited.
xGOT follows FRL's existing trigger rule: a blank xGOT is safe as zero only
when the shot-on-target trigger is zero; a positive-trigger blank makes the
season aggregate unavailable.
"""
from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACKAGED = ROOT / "data" / "rich_player_season_stats.csv"

RICH_PLAYER_METRICS = {
    # Shooting / territory
    "shots": "totalShots",
    "shots_on_target": "onTargetScoringAttempt",
    "shots_off_target": "shotOffTarget",
    "blocked_shots": "blockedScoringAttempt",
    "xgot": "expectedGoalsOnTarget",
    "touches": "touches",
    "hit_woodwork": "hitWoodwork",
    # Passing / creation
    "passes": "totalPass",
    "accurate_passes": "accuratePass",
    "accurate_opposition_half_passes": "accurateOppositionHalfPasses",
    "long_balls": "totalLongBalls",
    "accurate_long_balls": "accurateLongBalls",
    "successful_crosses": "accurateCross",
    "key_passes_rich": "keyPass",
    "big_chances_created_rich": "bigChanceCreated",
    # Possession / carrying. Player-Match take-ons are represented by
    # totalContest (attempted) and wonContest (successful).
    "successful_dribbles": "wonContest",
    "unsuccessful_dribbles": "totalContest",
    "ball_carries": "ballCarriesCount",
    "progressive_carries": "progressiveBallCarriesCount",
    "progressive_carry_distance": "totalProgressiveBallCarriesDistance",
    "total_progression": "totalProgression",
    "possession_lost": "possessionLostCtrl",
    # Defending / duels
    "tackles_rich": "totalTackle",
    "tackles_won": "wonTackle",
    "interceptions_won": "interceptionWon",
    "clearances": "totalClearance",
    "aerial_duels_won": "aerialWon",
    "aerial_duels_lost": "aerialLost",
    "duels_won": "duelWon",
    "duels_lost": "duelLost",
    "contests_won": "wonContest",
    "blocks": "outfielderBlock",
    "recoveries_rich": "ballRecovery",
    "errors_leading_to_shot": "errorLeadToAShot",
    "errors_leading_to_goal": "errorLeadToAGoal",
    # Discipline
    "fouls_conceded": "fouls",
    "fouls_won": "wasFouled",
    "penalties_won": "penaltyWon",
    "penalties_conceded": "penaltyConceded",
    # Goalkeeping
    "saves_rich": "saves",
    "saves_inside_box": "savedShotsFromInsideTheBox",
    "high_claims": "goodHighClaim",
    "keeper_sweeper_actions": "totalKeeperSweeper",
    "accurate_keeper_sweeper_actions": "accurateKeeperSweeper",
    "penalties_faced": "penaltyFaced",
}


def _number_or_none(value: object) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _sum_observed(records: tuple[dict, ...], source_field: str) -> float | None:
    observed = [
        value
        for row in records
        if (value := _number_or_none(row.get(source_field))) is not None
    ]
    return sum(observed) if observed else None


def _aggregate_xgot(records: tuple[dict, ...], season_fields: set[str]) -> float | None:
    source_field = "expectedGoalsOnTarget"
    trigger_field = "onTargetScoringAttempt"
    if source_field not in season_fields or trigger_field not in season_fields:
        return None

    total = 0.0
    observed_any = False
    for row in records:
        value = _number_or_none(row.get(source_field))
        if value is not None:
            total += value
            observed_any = True
            continue
        trigger = _number_or_none(row.get(trigger_field))
        if trigger is not None and trigger > 0:
            return None
    return total if observed_any else None


def _aggregate_unsuccessful_dribbles(records: tuple[dict, ...], season_fields: set[str]) -> float | None:
    if not {"totalContest", "wonContest"} <= season_fields:
        return None
    attempted = _sum_observed(records, "totalContest")
    successful = _sum_observed(records, "wonContest")
    if attempted is None or successful is None or successful > attempted:
        return None
    return attempted - successful


def aggregate_source_records(
    records: tuple[dict, ...],
    season_fields: set[str],
) -> dict[str, float | None]:
    """Materialisation helper: aggregate one player's source match rows."""
    output: dict[str, float | None] = {}
    for metric, source_field in RICH_PLAYER_METRICS.items():
        if metric == "xgot":
            output[metric] = _aggregate_xgot(records, season_fields)
            continue
        if metric == "unsuccessful_dribbles":
            output[metric] = _aggregate_unsuccessful_dribbles(records, season_fields)
            continue
        if source_field not in season_fields:
            output[metric] = None
            continue
        output[metric] = _sum_observed(records, source_field)
    return output


@lru_cache(maxsize=1)
def _packaged_rows() -> tuple[dict[str, str], ...]:
    if not PACKAGED.is_file():
        return tuple()
    with PACKAGED.open("r", encoding="utf-8-sig", newline="") as handle:
        return tuple(dict(row) for row in csv.DictReader(handle))


@lru_cache(maxsize=20)
def season_totals_by_pulselive_code(season: str) -> dict[str, dict[str, float | None]]:
    """Return packaged rich totals keyed by audited PulseLive/FPL code."""
    output: dict[str, dict[str, float | None]] = {}
    for row in _packaged_rows():
        if str(row.get("season") or "").strip() != season:
            continue
        code = str(row.get("player_code") or "").strip()
        if not code:
            continue
        output[code] = {
            metric: _number_or_none(row.get(metric))
            for metric in RICH_PLAYER_METRICS
        }
    return output


def enrich_player(player: dict, season: str) -> dict:
    """Add packaged rich source-backed metrics to one player research record."""
    enriched = dict(player)
    code = str(player.get("player_code") or "").strip()
    rich = season_totals_by_pulselive_code(season).get(code)
    if rich is None:
        for metric in RICH_PLAYER_METRICS:
            enriched.setdefault(metric, None)
        enriched["_rich_player_projection"] = "UNAVAILABLE"
        return enriched

    enriched.update(rich)
    enriched["_rich_player_projection"] = "RICH_PLAYER_SEASON_STATS_V1"
    return enriched


def clear_caches() -> None:
    _packaged_rows.cache_clear()
    season_totals_by_pulselive_code.cache_clear()


__all__ = [
    "PACKAGED",
    "RICH_PLAYER_METRICS",
    "aggregate_source_records",
    "clear_caches",
    "enrich_player",
    "season_totals_by_pulselive_code",
]
