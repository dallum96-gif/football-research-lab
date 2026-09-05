from __future__ import annotations

import json
from pathlib import Path

from source_field_registry import fields_for_family
from team_metric_missingness import (
    BLANK_IS_MISSING,
    normalise_team_match_observation,
    team_match_missingness_semantics,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "team_match_semantic_promotion_batch_v5.json"
EVIDENCE = ROOT / "data" / "team_match_semantic_evidence_v5.json"

PROMOTED_V5 = {
    "accurateBackZonePass",
    "accurateCornersIntobox",
    "accurateFwdZonePass",
    "accurateKeeperSweeper",
    "accuratePullBack",
    "accurateThroughBall",
    "accurateThrows",
    "attAssistOpenplay",
    "attAssistSetplay",
    "attemptsConcededIbox",
    "attemptsConcededObox",
    "bigChanceScored",
    "challengeLost",
    "crosses18yard",
    "crosses18yardplus",
    "divingSave",
    "effectiveBlockedCross",
    "effectiveHeadClearance",
    "errorLeadToGoal",
    "errorLeadToShot",
    "finalThirdEntries",
    "fouledFinalThird",
    "freekickCross",
    "hitWoodwork",
    "interceptionsInBox",
    "leftsidePass",
    "outfielderBlock",
    "overrun",
    "passesLeft",
    "passesRight",
    "penAreaEntries",
    "possLostAll",
    "possWonAtt3rd",
    "possWonDef3rd",
    "possWonMid3rd",
    "rightsidePass",
    "savedIbox",
    "savedObox",
    "subsMade",
    "totalBackZonePass",
    "totalContest",
    "totalCornersIntobox",
    "totalFwdZonePass",
    "totalHighClaim",
    "totalKeeperSweeper",
    "totalPullBack",
    "totalThroughBall",
    "totalThrows",
    "wonContest",
}


def _team_statuses() -> dict[str, str]:
    return {
        spec.source_field: spec.semantic_status
        for spec in fields_for_family("team_match")
    }


def test_v5_manifest_records_bulk_batch_and_expected_gate():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["status"] == "REGISTRY_PROMOTED_PENDING_LOCAL_MILESTONE_GATE"
    assert manifest["promotion_count"] == 49
    assert set(manifest["promoted_fields"]) == PROMOTED_V5
    expected = manifest["expected_post_gate"]["reconciliation"]
    assert expected == {
        "team_match_raw_paths": 249,
        "EXISTING_EXPOSED": 113,
        "EXISTING_SOURCE_FIELD_UNCATALOGUED": 77,
        "RAW_SNAPSHOT_ONLY": 59,
    }


def test_v5_exact_reference_map_covers_every_promoted_field():
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert set(evidence["exact_key_map"]) == PROMOTED_V5


def test_v5_fields_are_exposed_in_team_registry():
    statuses = _team_statuses()
    assert PROMOTED_V5 <= statuses.keys()
    assert {statuses[field] for field in PROMOTED_V5} == {"exposed"}


def test_v5_does_not_create_structural_zero_rules():
    for field in PROMOTED_V5:
        assert team_match_missingness_semantics("2025-26", field) == BLANK_IS_MISSING
        value, structural_zero = normalise_team_match_observation(
            "2025-26",
            field,
            None,
        )
        assert value is None
        assert structural_zero is False


def test_v5_entry_fields_are_independently_exposed_without_nesting_assumption():
    statuses = _team_statuses()
    assert statuses["finalThirdEntries"] == "exposed"
    assert statuses["penAreaEntries"] == "exposed"
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    note = manifest["important_semantic_resolutions"]["finalThirdEntries_penAreaEntries"]
    assert "No parent/child nesting" in note


def test_v5_preserves_distinct_directional_pass_concepts():
    statuses = _team_statuses()
    fields = {"leftsidePass", "rightsidePass", "passesLeft", "passesRight"}
    assert {statuses[field] for field in fields} == {"exposed"}
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    mapped = {evidence["exact_key_map"][field] for field in fields}
    assert len(mapped) == 4


def test_v5_keeps_known_unresolved_fields_out_of_registry():
    statuses = _team_statuses()
    for field in {
        "redCard",
        "successfulFiftyFifty",
        "successfulPutThrough",
        "attemptsIbox",
        "attemptsObox",
    }:
        assert statuses.get(field) != "exposed"
