from __future__ import annotations

from source_field_registry import fields_for_family
from team_metric_missingness import (
    BLANK_IS_MISSING,
    normalise_team_match_observation,
    team_match_missingness_semantics,
)
from variable_resolver import UnsupportedVariableError, resolve_variable


PROMOTED_V3 = {
    "blockedPass",
    "goalKicks",
    "touchesInOppBox",
}


def _team_statuses() -> dict[str, str]:
    return {
        spec.source_field: spec.semantic_status
        for spec in fields_for_family("team_match")
    }


def test_v3_fields_are_exposed_at_team_match_grain():
    statuses = _team_statuses()
    for field in PROMOTED_V3:
        assert statuses[field] == "exposed"
        definition = resolve_variable(field, family="team_match")
        assert definition.family == "team_match"
        assert definition.source_field == field
        assert definition.status == "exposed"


def test_v3_promotion_does_not_turn_blanks_into_structural_zero():
    for field in PROMOTED_V3:
        assert team_match_missingness_semantics("2025-26", field) == BLANK_IS_MISSING
        value, structural_zero = normalise_team_match_observation(
            "2025-26",
            field,
            None,
        )
        assert value is None
        assert structural_zero is False


def test_lost_corners_remains_unexposed_after_conflicting_opponent_evidence():
    statuses = _team_statuses()
    assert statuses.get("lostCorners") != "exposed"
    try:
        resolve_variable("lostCorners", family="team_match")
    except UnsupportedVariableError:
        pass
    else:
        raise AssertionError("lostCorners must remain fail-closed until semantics are governed")


def test_v3_does_not_change_existing_shot_sparse_zero_contract():
    value, structural_zero = normalise_team_match_observation(
        "2025-26",
        "Shots on target",
        None,
    )
    assert value == 0.0
    assert structural_zero is True
