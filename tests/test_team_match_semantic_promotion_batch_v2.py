from __future__ import annotations

import json
from pathlib import Path

import pytest

import research_access
from canonical_variable_catalogue import canonical_variables
from variable_resolver import (
    UnsupportedContextError,
    VariableUnavailableError,
    resolve_variable,
    variable_definition,
)


ROOT = Path(__file__).resolve().parents[1]

PROMOTED_BATCH_V2 = {
    "ballRecovery",
    "successfulFinalThirdPasses",
    "totalChippedPass",
    "totalFinalThirdPasses",
    "touches",
    "unsuccessfulTouch",
}

# Historical V2 decision: these fields were held at that checkpoint. Later
# governance may legitimately promote a subset, so runtime tests must not freeze
# the historical hold set forever.
HISTORICALLY_HELD_AFTER_V2 = {
    "blockedPass",
    "touchesInOppBox",
    "goalKicks",
    "lostCorners",
    "finalThirdEntries",
    "penAreaEntries",
}

# Current fail-closed set after V3 promoted the first three fields above as
# coverage-aware source-native variables while preserving blanks as missing.
STILL_HELD_AFTER_V3 = {
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


def test_v2_historical_hold_set_is_preserved_in_manifest():
    manifest = json.loads(
        (ROOT / "data" / "team_match_semantic_promotion_batch_v2.json").read_text(
            encoding="utf-8"
        )
    )
    assert HISTORICALLY_HELD_AFTER_V2 <= set(manifest["explicitly_held_fields"])


def test_current_post_v3_held_fields_remain_unpromoted():
    statuses = _team_catalogue_statuses()
    assert STILL_HELD_AFTER_V3 <= statuses.keys()
    assert {statuses[field] for field in STILL_HELD_AFTER_V3} == {"UNCATALOGUED"}


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


def test_current_semantically_unresolved_fields_still_fail_closed():
    for field in STILL_HELD_AFTER_V3:
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
