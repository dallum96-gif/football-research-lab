"""Universal research-access composition for fixture evidence."""
from __future__ import annotations

from collections import defaultdict

import research_access
from fixture_evidence import fixture_events
from source_family_adapters import (
    canonical_fixture,
    player_match_source_rows,
    resolve_source_match,
)

# These fields are already exposed by the generic player-match research family.
# Retained descriptive fields (name/position/substitute) are read from the same
# verified source rows rather than being promoted into a new GUI-specific layer.
EXPOSED_LINEUP_VARIABLES = ("playerId", "team_id", "venue", "minutesPlayed")
RETAINED_LINEUP_FIELDS = ("playerName", "substitute", "position")


def _ura_rows(season: str, fixture_id: str) -> dict[str, dict[str, object]]:
    by_player: dict[str, dict[str, object]] = defaultdict(dict)
    for variable in EXPOSED_LINEUP_VARIABLES:
        result = research_access.query(
            research_access.ResearchRequest(
                variable=variable,
                season=season,
                family="player_match",
                fixture_id=str(fixture_id),
            )
        )
        for row in result.get("results", []):
            player_id = str(row.get("source_player_id") or "").strip()
            if player_id:
                by_player[player_id][variable] = row.get("value")

    # Keep descriptive source fields attached to the same source-player row.
    for row in player_match_source_rows(season, fixture_id):
        player_id = str(row.get("playerId") or "").strip()
        if player_id:
            by_player[player_id].update({field: row.get(field) for field in RETAINED_LINEUP_FIELDS})
    return dict(by_player)


def fixture_research_result(season: str, fixture_id: str) -> dict:
    """Return the frontend/API fixture evidence result through governed access."""
    fixture = canonical_fixture(season, fixture_id)
    if fixture is None:
        raise ValueError(f"Canonical fixture not found: {season}/{fixture_id}")

    source_match = resolve_source_match(season, fixture_id)
    events = fixture_events(season, fixture_id)
    rows = _ura_rows(season, fixture_id)

    lineup = []
    for source_player_id, values in rows.items():
        substitute = str(values.get("substitute") or "").strip().casefold()
        raw_minutes = values.get("minutesPlayed")
        try:
            minutes = float(raw_minutes) if raw_minutes not in (None, "") else 0.0
        except (TypeError, ValueError):
            minutes = 0.0
        is_substitute = substitute in {"true", "1", "yes"}
        participation = (
            "starting" if not is_substitute and minutes > 0
            else "sub_in" if is_substitute and minutes > 0
            else "bench" if is_substitute and minutes == 0
            else "unknown"
        )
        venue = str(values.get("venue") or "").strip().casefold()
        side = "home" if venue == "home" else "away" if venue == "away" else None
        lineup.append({
            "player": {
                "source_player_id": source_player_id,
                "name": values.get("playerName"),
            },
            "side": side,
            "participation": participation,
            "position": values.get("position"),
            "minutes": raw_minutes,
            "provenance": {
                "season": season,
                "fixture_id": str(fixture_id),
                "source_match_id": str(source_match["source_match_id"]),
                "source_family": "player_match",
                "access_layer": "FRL Universal Research Access",
                "variables": list(EXPOSED_LINEUP_VARIABLES),
                "retained_fields": list(RETAINED_LINEUP_FIELDS),
                "transformation": "participation classification from substitute + minutesPlayed",
            },
        })

    lineup.sort(key=lambda item: (item["side"] != "home", item["participation"] != "starting", item["player"]["name"] or ""))
    status = "AVAILABLE" if lineup and events["status"] == "AVAILABLE" else "KNOWN_EXCEPTION"

    return {
        "query_type": "fixture_evidence",
        "query_version": "0.2.0",
        "parameters": {"season": season, "fixture_id": str(fixture_id)},
        "fixture": {
            "season": season,
            "fixture_id": str(fixture_id),
            "home_team_id": str(fixture.get("home_team_id") or ""),
            "away_team_id": str(fixture.get("away_team_id") or ""),
            "home_score": fixture.get("home_score"),
            "away_score": fixture.get("away_score"),
        },
        "events": events["events"],
        "lineup": lineup,
        "formation": {
            "home": {"status": "UNAVAILABLE", "value": None},
            "away": {"status": "UNAVAILABLE", "value": None},
        },
        "managers": {
            "status": "UNAVAILABLE",
            "items": [],
            "reason": "No validated historical manager-data route is exposed by the inspected FRL source universe.",
        },
        "status": status,
        "population": {"event_grain": "event", "lineup_grain": "player_fixture"},
        "coverage": {
            "event": events["coverage"],
            "lineup": {
                "player_rows": len(lineup),
                "starting_rows": sum(item["participation"] == "starting" for item in lineup),
                "bench_rows": sum(item["participation"] == "bench" for item in lineup),
                "sub_in_rows": sum(item["participation"] == "sub_in" for item in lineup),
            },
            "formation": "UNAVAILABLE",
            "managers": "UNAVAILABLE",
        },
        "temporal_context": {
            "season": season,
            "fixture_identity": [season, str(fixture_id)],
            "historical_state_and_information_availability_distinct": True,
            "information_available_as_of": None,
        },
        "provenance": {
            "access_layer": "FRL Universal Research Access",
            "fixture_relationship": "canonical_fixture_to_source_match",
            "source_match_id": str(source_match["source_match_id"]),
        },
        "limitations": events["limitations"] + [
            "Player-fixture participation is assembled from existing Player-Match research fields and the same verified source rows.",
            "Formation and tactical placement are unavailable because no independently validated historical tactical coordinates/formation field is established.",
            "Manager data is unavailable because no validated historical manager route is established.",
        ],
    }


__all__ = ["fixture_research_result"]
