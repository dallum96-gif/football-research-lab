"""Governed fixture evidence composition for frontend/research consumers.

Raw event/lineup/formation/manager evidence is supplied by the preserved
PulseLive adapter. Player participation is enriched through the established
Universal Research Access player-match seam rather than a second statistics
reader.
"""
from __future__ import annotations

from typing import Any

import research_access
from fixture_evidence import fixture_evidence
from source_family_adapters import resolve_pulselive_player_identity

PLAYER_MATCH_VARIABLES = ("minutesPlayed", "substitute", "venue")


def _ura_player_rows(season: str, fixture_id: str) -> dict[str, dict[str, Any]]:
    by_player: dict[str, dict[str, Any]] = {}
    for variable in PLAYER_MATCH_VARIABLES:
        result = research_access.query(
            research_access.ResearchRequest(
                variable=variable,
                season=season,
                family="player_match",
                fixture_id=str(fixture_id),
            )
        )
        for row in result.get("results", []):
            source_id = str(row.get("source_player_id") or "").strip()
            if source_id:
                by_player.setdefault(source_id, {})[variable] = row.get("value")
    return by_player


def _participation(values: dict[str, Any]) -> str:
    substitute = str(values.get("substitute") or "").strip().casefold()
    raw_minutes = values.get("minutesPlayed")
    try:
        minutes = float(raw_minutes) if raw_minutes not in (None, "") else 0.0
    except (TypeError, ValueError):
        minutes = 0.0
    is_substitute = substitute in {"true", "1", "yes"}
    if not is_substitute and minutes > 0:
        return "starting"
    if is_substitute and minutes > 0:
        return "sub_in"
    if is_substitute and minutes == 0:
        return "bench"
    return "unknown"


def _player_match_lookup_identity(
    season: str,
    fixture_id: str,
    row: dict[str, Any],
) -> tuple[str, dict[str, Any] | None]:
    """Return the governed Player-Match ID used for the URA lookup."""
    player = row.get("player") or {}
    source_family = str((row.get("provenance") or {}).get("source_family") or "").strip()
    source_id = str(player.get("source_player_id") or "").strip()

    if source_family == "pulselive_match_lineups":
        bridge = resolve_pulselive_player_identity(season, fixture_id, source_id)
        if bridge.get("relationship_status") != "VERIFIED":
            return "", bridge
        player_match_source_id = str(
            bridge.get("player_match_source_player_id") or ""
        ).strip()
        return player_match_source_id, bridge

    # Player-Match fallback rows already use the established source_player_id
    # namespace and therefore do not pass through the PulseLive bridge.
    player_match_source_id = str(
        player.get("player_match_source_player_id") or source_id
    ).strip()
    return player_match_source_id, None


def fixture_research_result(season: str, fixture_id: str) -> dict[str, Any]:
    """Return the governed fixture evidence result for a canonical fixture."""
    evidence = fixture_evidence(season, fixture_id)
    if evidence["status"] == "UNAVAILABLE":
        return evidence

    ura_rows = _ura_player_rows(season, fixture_id) if evidence.get("lineup") else {}
    lineup: list[dict[str, Any]] = []
    participation_missing = 0

    for row in evidence.get("lineup", []):
        player_match_source_id, bridge = _player_match_lookup_identity(
            season,
            str(fixture_id),
            row,
        )
        values = ura_rows.get(player_match_source_id, {})
        if values:
            participation = _participation(values)
            side = str(values.get("venue") or row.get("side") or "").strip().casefold() or None
        else:
            participation = "unknown"
            side = row.get("side")
            participation_missing += 1

        item = dict(row)
        item["player"] = {
            **dict(row.get("player") or {}),
            "player_match_source_player_id": player_match_source_id or None,
            "player_match_source_player_id_namespace": (
                bridge.get("player_match_source_player_id_namespace")
                if bridge is not None
                else (row.get("player") or {}).get(
                    "player_match_source_player_id_namespace"
                )
            ),
            **({"identity_bridge": bridge} if bridge is not None else {}),
        }
        item["side"] = side
        item["participation"] = participation
        item["minutes"] = values.get("minutesPlayed") if values else None
        item["provenance"] = {
            **dict(row.get("provenance") or {}),
            "access_layer": "FRL Universal Research Access",
            "participation_variables": list(PLAYER_MATCH_VARIABLES),
            "participation_lookup_source_player_id": player_match_source_id or None,
            "participation_lookup_source_player_id_namespace": (
                bridge.get("player_match_source_player_id_namespace")
                if bridge is not None
                else "player_match_stats.source_player_id()"
            ),
            **(
                {
                    "identity_bridge_route": bridge["identity_route"],
                    "identity_bridge_contract": bridge["relationship_contract"],
                    "identity_bridge_status": bridge["relationship_status"],
                }
                if bridge is not None
                else {}
            ),
        }
        lineup.append(item)

    return {
        **evidence,
        "lineup": lineup,
        "coverage": {
            **dict(evidence.get("coverage") or {}),
            "lineup": {
                **dict(evidence.get("coverage", {}).get("lineup") or {}),
                "starting": sum(item["participation"] == "starting" for item in lineup),
                "sub_in": sum(item["participation"] == "sub_in" for item in lineup),
                "bench": sum(item["participation"] == "bench" for item in lineup),
                "unknown": sum(item["participation"] == "unknown" for item in lineup),
            },
        },
        # Unknown participation is a partial-evidence condition, not itself a
        # known exception. The individual row remains explicitly "unknown".
        "status": evidence["status"],
        "limitations": list(evidence.get("limitations") or []) + (
            [f"{participation_missing} lineup players lacked a reusable Player-Match participation observation; participation remains unknown."]
            if participation_missing else []
        ),
        "provenance": {
            **dict(evidence.get("provenance") or {}),
            "access_layer": "FRL Universal Research Access",
            "player_match_access": True,
        },
    }


__all__ = ["fixture_research_result"]
