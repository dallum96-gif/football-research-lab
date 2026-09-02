"""Governed season projection over preserved player-match evidence.

This module is deliberately additive to the existing FPL-derived player research
layer.  It joins through the audited ``pl_code`` bridge already maintained by
``player_match_stats`` and never substitutes names for player identity.

Source blanks remain unavailable unless at least one observation exists for the
player/field.  No missing rich metric is coerced into a season zero.
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


def _number(value: object) -> float:
    if value in (None, ""):
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _aggregate(records: tuple[dict, ...], season_fields: set[str]) -> dict[str, float | None]:
    output: dict[str, float | None] = {}
    for metric, source_field in RICH_PLAYER_METRICS.items():
        if source_field not in season_fields:
            output[metric] = None
            continue
        observed = [row.get(source_field) for row in records if row.get(source_field) not in (None, "")]
        output[metric] = sum(_number(value) for value in observed) if observed else None
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
