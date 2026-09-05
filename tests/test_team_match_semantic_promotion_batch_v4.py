from __future__ import annotations

import json
from pathlib import Path

import pytest

from canonical_variable_catalogue import canonical_variables
from source_field_registry import fields_for_family
from team_metric_missingness import (
    BLANK_IS_MISSING,
    normalise_team_match_observation,
    team_match_missingness_semantics,
)
from variable_resolver import VariableUnavailableError, resolve_variable, variable_definition


ROOT = Path(__file__).resolve().parents[1]
V4_MANIFEST = ROOT / "data" / "team_match_semantic_promotion_batch_v4.json"

PROMOTED_V4 = {
    "accurateChippedPass",
    "accurateCross",
    "accurateFlickOn",
    "accurateGoalKicks",
    "accurateKeeperThrows",
    "accurateLaunches",
    "accurateLayoffs",
    "accurateLongBalls",
    "blockedCross",
    "keeperThrows",
    "lostCorners",
    "totalFlickOn",
    "totalLaunches",
    "totalLayoffs",
    "totalLongBalls",
    "wonCorners",
}

HELD_AFTER_V4 = {
    "redCard",
    "subsMade",
    "accurateBackZonePass",
    "accurateFwdZonePass",
    "accurateCornersIntobox",
    "accurateKeeperSweeper",
    "accuratePullBack",
    "accurateThroughBall",
    "successfulFiftyFifty",
    "successfulPutThrough",
    "accurateThrows",
    "effectiveBlockedCross",
}


def _team_statuses() -> dict[str, str]:
    return {
        spec.source_field: spec.semantic_status
        for spec in fields_for_family("team_match")
    }


def _catalogue_statuses() -> dict[str, str]:
    return {
        str(row.get("field_name") or ""): str(row.get("semantic_status") or "")
        for row in canonical_variables()
        if str(row.get("grain") or "") == "team_match"
    }


def test_v4_manifest_records_exact_controlled_batch():
    manifest = json.loads(V4_MANIFEST.read_text(encoding="utf-8"))
    assert manifest["status"] == "REGISTRY_PROMOTED_PENDING_LOCAL_REGRESSION_GATE"
    assert set(manifest["promoted_fields"]) == PROMOTED_V4
    assert manifest["relationship_evidence"]["audit_result"] == "18/18 DECADE_EMPIRICALLY_CONSISTENT"
    assert manifest["coverage_and_missingness"]["governed_structural_zero_change"] is False


def test_v4_fields_are_exposed_in_registry_and_runtime_catalogue():
    registry = _team_statuses()
    catalogue = _catalogue_statuses()
    for field in PROMOTED_V4:
        assert registry[field] == "exposed"
        assert catalogue[field] == "exposed"
        definition = variable_definition(field, family="team_match", season="2024-25")
        assert definition.family == "team_match"
        assert definition.source_field == field
        assert definition.status == "exposed"


def test_v4_coverage_aware_fields_keep_blanks_missing():
    for field in PROMOTED_V4:
        assert team_match_missingness_semantics("2025-26", field) == BLANK_IS_MISSING
        value, structural_zero = normalise_team_match_observation(
            "2025-26",
            field,
            None,
        )
        assert value is None
        assert structural_zero is False


def test_lost_corners_is_now_exposed_without_opponent_corner_equivalence():
    definition = variable_definition(
        "lostCorners",
        family="team_match",
        season="2024-25",
    )
    assert definition.status == "exposed"
    manifest = json.loads(V4_MANIFEST.read_text(encoding="utf-8"))
    resolution = manifest["lost_corners_semantic_resolution"]
    assert resolution["decision"] == "DIRECT_CORNER_LOST_DEFINITION_SUPERSEDES_PRIOR_OPPONENT_EQUALITY_ASSUMPTION"
    assert "145" in resolution["interpretation"]
    assert "160" in resolution["interpretation"]


def test_v4_relationship_only_and_event_recon_candidates_still_fail_closed():
    for field in HELD_AFTER_V4:
        definition = variable_definition(field, family="team_match", season="2024-25")
        assert definition.status == "uncatalogued"
        with pytest.raises(VariableUnavailableError):
            resolve_variable(
                field,
                family="team_match",
                season="2024-25",
                fixture_id="1",
            )
