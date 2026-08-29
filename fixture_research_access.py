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


def _formation_line_counts(value: Any) -> tuple[int, ...] | None:
    """Parse a source-backed formation only when it describes ten outfield players."""
    text = str(value or "").strip()
    parts = text.split("-")
    if not parts or any(not part.isdigit() for part in parts):
        return None
    counts = tuple(int(part) for part in parts)
    if any(count <= 0 for count in counts) or sum(counts) != 10:
        return None
    return counts


def _presentation_coordinates(
    *,
    line_index: int,
    slot_index: int,
    line_size: int,
    outfield_line_count: int,
) -> tuple[float, float]:
    """Return deterministic diagram coordinates, not source tactical evidence."""
    if line_size == 1:
        x = 50.0
    else:
        span = min(64.0, 24.0 * (line_size - 1))
        x = 50.0 - span / 2.0 + span * slot_index / (line_size - 1)
    y = 8.0 if line_index == 0 else 8.0 + 83.0 * line_index / outfield_line_count
    return round(x, 2), round(y, 2)


def _derived_side_placements(
    side: str,
    rows: list[dict[str, Any]],
    formation_value: Any,
) -> dict[str, dict[str, Any]]:
    """Derive a layout only from a complete verified XI and exact source order."""
    starting = [row for row in rows if row.get("participation") == "starting"]
    if len(starting) != 11:
        return {}

    line_counts = _formation_line_counts(formation_value)
    if line_counts is None:
        return {}
    expected_line_sizes = (1, *line_counts)

    by_line: dict[int, list[tuple[int, dict[str, Any]]]] = {}
    source_player_ids: set[str] = set()
    for row in starting:
        source_player_id = str((row.get("player") or {}).get("source_player_id") or "").strip()
        order = row.get("source_formation_order")
        if not source_player_id or not isinstance(order, dict):
            return {}
        try:
            line_index = int(order["line_index"])
            slot_index = int(order["slot_index"])
            line_size = int(order["line_size"])
        except (KeyError, TypeError, ValueError):
            return {}
        if source_player_id in source_player_ids:
            return {}
        source_player_ids.add(source_player_id)
        if not 0 <= line_index < len(expected_line_sizes):
            return {}
        if line_size != expected_line_sizes[line_index] or not 0 <= slot_index < line_size:
            return {}
        by_line.setdefault(line_index, []).append((slot_index, row))

    if set(by_line) != set(range(len(expected_line_sizes))):
        return {}
    for line_index, expected_size in enumerate(expected_line_sizes):
        slots = sorted(slot for slot, _ in by_line[line_index])
        if slots != list(range(expected_size)):
            return {}

    goalkeeper = by_line[0][0][1]
    goalkeeper_position = str(goalkeeper.get("position") or "").strip().casefold()
    if goalkeeper_position not in {"goalkeeper", "gk"}:
        return {}
    if any(
        str(row.get("position") or "").strip().casefold() in {"goalkeeper", "gk"}
        for line_index, line in by_line.items()
        if line_index != 0
        for _, row in line
    ):
        return {}

    placements: dict[str, dict[str, Any]] = {}
    for line_index in range(len(expected_line_sizes)):
        for slot_index, row in by_line[line_index]:
            source_player_id = str((row.get("player") or {}).get("source_player_id"))
            x, y = _presentation_coordinates(
                line_index=line_index,
                slot_index=slot_index,
                line_size=expected_line_sizes[line_index],
                outfield_line_count=len(line_counts),
            )
            placements[source_player_id] = {
                "source_player_id": source_player_id,
                "x": x,
                "y": y,
                "status": "DERIVED_FORMATION_LAYOUT",
                "provenance": {
                    "classification": "PRESENTATION_ONLY",
                    "explicit_source_coordinates": False,
                    "source_formation": str(formation_value),
                    "source_formation_field": "pulselive_match.lineups.formation.formation",
                    "source_order_field": "pulselive_match.lineups.formation.lineup",
                    "source_line_index": line_index,
                    "source_slot_index": slot_index,
                    "source_line_size": expected_line_sizes[line_index],
                    "starting_xi_status": "VERIFIED_PLAYER_MATCH_PARTICIPATION",
                    "side": side,
                },
            }
    return placements


def _apply_presentation_placements(
    lineup: list[dict[str, Any]],
    formation: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    output = [dict(row) for row in lineup]
    coverage: dict[str, dict[str, Any]] = {}

    for side in ("home", "away"):
        indexed = [(index, row) for index, row in enumerate(output) if row.get("side") == side]
        starting = [(index, row) for index, row in indexed if row.get("participation") == "starting"]
        explicit_count = sum(
            (row.get("placement") or {}).get("status") == "SOURCE_EXPLICIT"
            for _, row in starting
        )
        if explicit_count:
            coverage[side] = {
                "status": "SOURCE_EXPLICIT" if explicit_count == len(starting) == 11 else "PARTIAL_SOURCE_EXPLICIT",
                "count": explicit_count,
            }
            continue

        formation_side = formation.get(side) if isinstance(formation, dict) else None
        formation_value = (
            formation_side.get("value")
            if isinstance(formation_side, dict) and formation_side.get("status") == "AVAILABLE"
            else None
        )
        placements = _derived_side_placements(side, [row for _, row in indexed], formation_value)
        if not placements:
            coverage[side] = {"status": "UNAVAILABLE", "count": 0}
            continue

        for index, row in starting:
            source_player_id = str((row.get("player") or {}).get("source_player_id") or "").strip()
            if source_player_id in placements:
                output[index] = {**row, "placement": placements[source_player_id]}
        coverage[side] = {"status": "DERIVED_FORMATION_LAYOUT", "count": len(placements)}

    return output, coverage


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

    lineup, placement_coverage = _apply_presentation_placements(
        lineup,
        dict(evidence.get("formation") or {}),
    )
    derived_layout = any(
        item.get("status") == "DERIVED_FORMATION_LAYOUT"
        for item in placement_coverage.values()
    )

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
            "placement": placement_coverage,
        },
        # Unknown participation is a partial-evidence condition, not itself a
        # known exception. The individual row remains explicitly "unknown".
        "status": evidence["status"],
        "limitations": list(evidence.get("limitations") or []) + (
            [f"{participation_missing} lineup players lacked a reusable Player-Match participation observation; participation remains unknown."]
            if participation_missing else []
        ) + (
            ["Tactical x/y coordinates marked DERIVED_FORMATION_LAYOUT are presentation-only geometry based on the verified starting XI, source formation and source formation-line order; they are not explicit source coordinates."]
            if derived_layout else []
        ),
        "provenance": {
            **dict(evidence.get("provenance") or {}),
            "access_layer": "FRL Universal Research Access",
            "player_match_access": True,
            "tactical_placement": {
                "classification": "PRESENTATION_ONLY" if derived_layout else "SOURCE_OR_UNAVAILABLE",
                "coverage": placement_coverage,
                "derivation_status": "DERIVED_FORMATION_LAYOUT" if derived_layout else "NOT_DERIVED",
            },
        },
    }


__all__ = ["fixture_research_result"]
