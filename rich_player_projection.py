"""Governed season projection over preserved player-match evidence.

This module is deliberately additive to the existing FPL-derived player research
layer. It joins through the audited ``pl_code`` bridge already maintained by
``player_match_stats`` and never substitutes names for player identity.

Source blanks remain unavailable unless their zero semantics have been audited.
In particular, xGOT follows FRL's existing trigger rule: a blank xGOT is safe as
zero only when the player's shot-on-target trigger is zero; a positive-trigger
blank makes the season xGOT aggregate unavailable.
"""
from __future__ import annotations

from functools import lru_cache

import player_match_stats


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
    # Possession / carrying
    "successful_dribbles": "successfulDribbles",
    "unsuccessful_dribbles": "unsuccessfulDribbles",
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


def _aggregate(records: tuple[dict, ...], season_fields: set[str]) -> dict[str, float | None]:
    output: dict[str, float | None] = {}
    for metric, source_field in RICH_PLAYER_METRICS.items():
        if metric == "xgot":
            output[metric] = _aggregate_xgot(records, season_fields)
            continue
        if source_field not in season_fields:
            output[metric] = None
            continue
        output[metric] = _sum_observed(records, source_field)
    return output


@lru_cache(maxsize=20)
def season_totals_by_pulselive_code(season: str) -> dict[str, dict[str, float | None]]:
    """Return rich player-season totals keyed by the audited PulseLive/FPL code."""
    fields = set(player_match_stats.source_fields(season))
    bridge = player_match_stats.pulselive_player_bridge_index(season)
    output: dict[str, dict[str, float | None]] = {}

    for pulselive_code, identity in bridge.items():
        player_id = str(identity.get("player_id") or "").strip()
        if not player_id:
            continue
        records = player_match_stats.player_match_records_for_player(player_id, season)
        if not records:
            continue
        output[str(pulselive_code)] = _aggregate(records, fields)

    return output


def enrich_player(player: dict, season: str) -> dict:
    """Add rich source-backed metrics to one existing player research record."""
    enriched = dict(player)
    code = str(player.get("player_code") or "").strip()
    rich = season_totals_by_pulselive_code(season).get(code)
    if rich is None:
        for metric in RICH_PLAYER_METRICS:
            enriched.setdefault(metric, None)
        enriched["_rich_player_projection"] = "UNAVAILABLE"
        return enriched

    enriched.update(rich)
    enriched["_rich_player_projection"] = "PLAYERS_MATCH_STATS_V1"
    return enriched


__all__ = ["RICH_PLAYER_METRICS", "enrich_player", "season_totals_by_pulselive_code"]
