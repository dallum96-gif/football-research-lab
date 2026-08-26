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


def fixture_research_result(season: str, fixture_id: str) -> dict[str, Any]:
    """Return the governed fixture evidence result for a canonical fixture."""
    evidence = fixture_evidence(season, fixture_id)
    if evidence["status"] == "UNAVAILABLE":
        return evidence

    ura_rows = _ura_player_rows(season, fixture_id) if evidence.get("lineup") else {}
    lineup: list[dict[str, Any]] = []
    participation_missing = 0

    for row in evidence.get("lineup", []):
        source_id = str(row.get("player", {}).get("source_player_id") or "").strip()
        values = ura_rows.get(source_id, {})
        if values:
            participation = _participation(values)
            side = str(values.get("venue") or row.get("side") or "").strip().casefold() or None
        else:
            participation = "unknown"
            side = row.get("side")
            participation_missing += 1

        item = dict(row)
        item["side"] = side
        item["participation"] = participation
        item["minutes"] = values.get("minutesPlayed") if values else None
        item["provenance"] = {
            **dict(row.get("provenance") or {}),
            "access_layer": "FRL Universal Research Access",
            "participation_variables": list(PLAYER_MATCH_VARIABLES),
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
