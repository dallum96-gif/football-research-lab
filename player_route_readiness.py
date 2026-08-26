"""Fail-closed readiness checks for routed player variable families.

This module reuses the existing verified player registry and relationship
contracts. It never infers a new player identity and never promotes a
relationship record.
"""
from __future__ import annotations

from player_identity_registry import build_registry
from relationship_contracts import get_relationship_contract


def verified_registry_rows() -> tuple[dict[str, str], ...]:
    rows = build_registry()
    return tuple(
        row for row in rows
        if row.get("identity_status") == "VERIFIED"
        and row.get("confidence") == "VERIFIED"
    )


def registry_is_contract_compliant() -> bool:
    """Return True only when every promoted player registry row satisfies its contract inputs."""
    get_relationship_contract("fpl_player_to_frl_player_identity")
    for row in verified_registry_rows():
        if not row.get("season") or not row.get("fpl_element"):
            return False
        if not row.get("source_player_id"):
            return False
        if row.get("match_method") != "EXACT_NAME_TEAM":
            return False
    return True


def player_season_route_status() -> str:
    """Describe readiness of the source-player -> player-season route without promotion."""
    get_relationship_contract("source_player_identity_to_player_season")
    return "READY_FOR_VERIFICATION" if registry_is_contract_compliant() else "BLOCKED"


def player_match_route_status() -> str:
    """Describe readiness of player-match attachment; identity remains a prerequisite."""
    get_relationship_contract("player_identity_to_player_match_observations")
    return "REQUIRES_VERIFIED_PLAYER_IDENTITY"
