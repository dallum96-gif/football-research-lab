"""Contract-enforced player relationship accessors.

This layer wraps the existing source-family adapters and applies the shared
relationship contracts without creating a second source loader or identity
registry. It distinguishes identity relationships from player-match
observations: absence of an observation is not evidence that the identity is
wrong.
"""
from __future__ import annotations

from functools import lru_cache

from player_identity_registry import build_registry as build_player_identity_registry
from relationship_enforcement import (
    classify_observation,
    decision_dict,
    evaluate_identity,
)
from source_family_adapters import (
    player_match_source_rows,
    player_season_source_rows,
    resolve_source_match,
)
from player_match_stats import source_player_id


@lru_cache(maxsize=1)
def _identity_rows() -> tuple[dict[str, str], ...]:
    return tuple(build_player_identity_registry())


def resolve_fpl_player_identity(season: str, fpl_element: str) -> dict:
    """Resolve a seasonal FPL element only when its verified registry row is unique."""
    registry = _identity_rows()
    season_context_available = any(row.get("season") == season for row in registry)
    candidates = [
        row for row in registry
        if row.get("season") == season
        and str(row.get("fpl_element", "")).strip() == str(fpl_element).strip()
    ]

    decision = evaluate_identity(
        "fpl_player_to_frl_player_identity",
        source_context_available=season_context_available,
        candidates=candidates,
    )
    result = {
        "season": season,
        "fpl_element": str(fpl_element),
        **decision_dict(decision),
    }
    if decision.verified:
        row = dict(candidates[0])
        result.update(row)
        result["frl_player_source_id"] = row.get("source_player_id", "")
    return result


def source_player_season_identity(season: str, source_player_id_value: str) -> dict:
    """Resolve a source player ID to exactly one player-season record."""
    candidates = [
        row for row in player_season_source_rows(season)
        if str(row.get("playerId", "")).strip() == str(source_player_id_value).strip()
    ]
    decision = evaluate_identity(
        "source_player_identity_to_player_season",
        source_context_available=True,
        candidates=candidates,
    )
    result = {
        "season": season,
        "source_player_id": str(source_player_id_value),
        **decision_dict(decision),
    }
    if decision.verified:
        result["player_season"] = dict(candidates[0])
    return result


def player_match_observation_status(
    season: str,
    fixture_id: str,
    source_player_id_value: str,
    *,
    player_identity_verified: bool = True,
) -> dict:
    """Classify an observation without treating a missing row as identity failure."""
    resolve_source_match(season, fixture_id)
    rows = [
        row for row in player_match_source_rows(season, fixture_id)
        if str(source_player_id(row) or "").strip() == str(source_player_id_value).strip()
    ]
    status = classify_observation(
        identity_verified=player_identity_verified,
        fixture_verified=True,
        observation_present=bool(rows),
    )
    return {
        "season": season,
        "fixture_id": str(fixture_id),
        "source_player_id": str(source_player_id_value),
        "relationship_contract": "player_identity_to_player_match_observations",
        "relationship_status": status,
        "observation_present": bool(rows),
    }
