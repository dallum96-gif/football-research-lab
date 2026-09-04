from __future__ import annotations

import pytest

import research_access
from canonical_variable_catalogue import canonical_variables
from variable_resolver import VariableUnavailableError, resolve_variable, variable_definition


PROMOTED_BATCH_V1 = {
    "accurateCrossNocorner",
    "aerialLost",
    "aerialWon",
    "backwardPass",
    "duelLost",
    "duelWon",
    "fwdPass",
    "headClearance",
    "longPassOwnToOpp",
    "longPassOwnToOppSuccess",
    "openPlayPass",
    "successfulOpenPlayPass",
    "totalCrossNocorner",
}

HELD_FOR_FURTHER_REVIEW = {
    "challengeLost",
    "effectiveHeadClearance",
    "totalContest",
    "wonContest",
}


def _team_catalogue_statuses() -> dict[str, str]:
    return {
        str(row.get("field_name") or ""): str(row.get("semantic_status") or "")
        for row in canonical_variables()
        if str(row.get("grain") or "") == "team_match"
    }


def test_promoted_batch_is_exposed_in_runtime_catalogue():
    statuses = _team_catalogue_statuses()

    assert PROMOTED_BATCH_V1 <= statuses.keys()
    assert {statuses[field] for field in PROMOTED_BATCH_V1} == {"exposed"}


def test_ambiguous_fields_remain_unpromoted_at_team_match_grain():
    statuses = _team_catalogue_statuses()

    assert HELD_FOR_FURTHER_REVIEW <= statuses.keys()
    assert {statuses[field] for field in HELD_FOR_FURTHER_REVIEW} == {"UNCATALOGUED"}


def test_resolver_definition_uses_promoted_registry_status():
    definition = variable_definition(
        "backwardPass", family="team_match", season="2024-25"
    )

    assert definition.family == "team_match"
    assert definition.source_field == "backwardPass"
    assert definition.status == "exposed"


def test_research_discovery_reflects_promoted_status():
    result = research_access.discover(family="team_match", search="backwardPass")

    assert result["count"] == 1
    assert result["results"][0]["variable"] == "backwardPass"
    assert result["results"][0]["status"] == "exposed"


def test_ambiguous_team_match_field_still_fails_closed_for_reusable_resolution():
    definition = variable_definition(
        "wonContest", family="team_match", season="2024-25"
    )
    assert definition.status == "uncatalogued"

    with pytest.raises(VariableUnavailableError):
        resolve_variable(
            "wonContest",
            family="team_match",
            season="2024-25",
            fixture_id="1",
        )
