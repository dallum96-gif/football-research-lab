from __future__ import annotations

import json
from pathlib import Path

import research_access
from canonical_variable_catalogue import canonical_variables
from variable_resolver import variable_definition


ROOT = Path(__file__).resolve().parents[1]

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

HISTORICALLY_HELD_AFTER_V1 = {
    "challengeLost",
    "effectiveHeadClearance",
    "totalContest",
    "wonContest",
    "leftsidePass",
    "rightsidePass",
    "passesLeft",
    "passesRight",
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


def test_v1_historical_hold_set_is_preserved_in_manifest():
    manifest = json.loads(
        (ROOT / "data" / "team_match_semantic_promotion_batch_v1.json").read_text(
            encoding="utf-8"
        )
    )
    assert HISTORICALLY_HELD_AFTER_V1 <= set(manifest["explicitly_held_fields"])


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


def test_later_governance_can_supersede_v1_holds_without_rewriting_history():
    statuses = _team_catalogue_statuses()
    assert {statuses[field] for field in HISTORICALLY_HELD_AFTER_V1} == {"exposed"}
