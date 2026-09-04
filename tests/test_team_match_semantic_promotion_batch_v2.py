from __future__ import annotations

import pytest

import research_access
from canonical_variable_catalogue import canonical_variables
from variable_resolver import (
    UnsupportedContextError,
    VariableUnavailableError,
    resolve_variable,
    variable_definition,
)


PROMOTED_BATCH_V2 = {
    "ballRecovery",
    "successfulFinalThirdPasses",
    "totalChippedPass",
    "totalFinalThirdPasses",
    "touches",
    "unsuccessfulTouch",
}

HELD_AFTER_V2 = {
    "blockedPass",
    "touchesInOppBox",
    "goalKicks",
    "lostCorners",
    "finalThirdEntries",
    "penAreaEntries",
}


def _team_catalogue_statuses() -> dict[str, str]:
    return {
        str(row.get("field_name") or ""): str(row.get("semantic_status") or "")
        for row in canonical_variables()
        if str(row.get("grain") or "") == "team_match"
    }


def test_v2_promoted_batch_is_exposed_in_runtime_catalogue():
    statuses = _team_catalogue_statuses()
    assert PROMOTED_BATCH_V2 <= statuses.keys()
    assert {statuses[field] for field in PROMOTED_BATCH_V2} == {"exposed"}


def test_v2_held_fields_remain_unpromoted():
    statuses = _team_catalogue_statuses()
    assert HELD_AFTER_V2 <= statuses.keys()
    assert {statuses[field] for field in HELD_AFTER_V2} == {"UNCATALOGUED"}


def test_v2_definition_uses_team_match_registry_status():
    definition = variable_definition(
        "ballRecovery", family="team_match", season="2024-25"
    )
    assert definition.family == "team_match"
    assert definition.source_field == "ballRecovery"
    assert definition.status == "exposed"


def test_v2_discovery_reflects_promoted_status():
    result = research_access.discover(
        family="team_match", search="successfulFinalThirdPasses"
    )
    assert result["count"] == 1
    assert result["results"][0]["variable"] == "successfulFinalThirdPasses"
    assert result["results"][0]["status"] == "exposed"


def test_explicit_team_family_disambiguates_touches_from_player_match():
    team_definition = variable_definition(
        "touches", family="team_match", season="2024-25"
    )
    player_definition = variable_definition(
        "touches", family="player_match", season="2024-25"
    )
    assert team_definition.family == "team_match"
    assert team_definition.status == "exposed"
    assert player_definition.family == "player_match"
    assert player_definition.status == "exposed"

    with pytest.raises(UnsupportedContextError):
        variable_definition("touches", season="2024-25")


def test_sparse_or_semantically_unresolved_v2_fields_still_fail_closed():
    for field in HELD_AFTER_V2:
        definition = variable_definition(
            field, family="team_match", season="2024-25"
        )
        assert definition.status == "uncatalogued"
        with pytest.raises(VariableUnavailableError):
            resolve_variable(
                field,
                family="team_match",
                season="2024-25",
                fixture_id="1",
            )
