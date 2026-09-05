from __future__ import annotations

import json
from pathlib import Path

from match_stats import CORE_FIELDS
from source_field_registry import fields_for_family
from team_metric_missingness import (
    BLANK_IS_MISSING,
    normalise_team_match_observation,
    team_match_missingness_semantics,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "team_match_semantic_promotion_batch_v7.json"
EVIDENCE = ROOT / "data" / "team_match_semantic_evidence_v7.json"

PROMOTED_V7 = {
    "attFreekickPost",
    "attIboxOwnGoal",
    "attLgCentre",
    "attLgLeft",
    "attLgRight",
    "attemptsIbox",
    "attemptsObox",
    "ptsDroppedWinningPos",
    "ptsGainedLosingPos",
}

HELD_AFTER_V7 = {
    "attOboxOwnGoal",
    "expectedGoalsFreekick",
    "expectedGoalsOnTargetConceded",
    "fiftyFifty",
    "freekickTotal",
    "keeperGoals",
    "putThrough",
    "redCard",
    "subsGoals",
    "successfulFiftyFifty",
    "successfulPutThrough",
    "totalDistance",
    "winningGoal",
    "yellowCard",
}


def _team_statuses() -> dict[str, str]:
    return {
        spec.source_field: spec.semantic_status
        for spec in fields_for_family("team_match")
    }


def test_v7_manifest_records_exact_residue_batch_and_gate():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["status"] == "REGISTRY_PROMOTED_PENDING_LOCAL_MILESTONE_GATE"
    assert manifest["promotion_count"] == 9
    assert set(manifest["promoted_fields"]) == PROMOTED_V7
    assert set(manifest["explicitly_held_fields"]) == HELD_AFTER_V7
    assert manifest["expected_post_gate"]["reconciliation"] == {
        "team_match_raw_paths": 249,
        "EXISTING_EXPOSED": 176,
        "EXISTING_SOURCE_FIELD_UNCATALOGUED": 14,
        "RAW_SNAPSHOT_ONLY": 59,
    }


def test_v7_evidence_covers_every_promoted_field_and_explicitly_holds_winning_goal():
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert set(evidence["fields"]) == PROMOTED_V7
    assert "winningGoal" in evidence["explicit_non_promotion"]


def test_v7_fields_are_exposed_and_remaining_residue_is_not():
    statuses = _team_statuses()
    assert PROMOTED_V7 <= statuses.keys()
    assert {statuses[field] for field in PROMOTED_V7} == {"exposed"}
    assert all(statuses.get(field) != "exposed" for field in HELD_AFTER_V7)


def test_attempts_inside_outside_box_match_existing_governed_direct_labels():
    assert CORE_FIELDS["Shots inside box"] == "attemptsIbox"
    assert CORE_FIELDS["Shots outside box"] == "attemptsObox"
    statuses = _team_statuses()
    assert statuses["attemptsIbox"] == "exposed"
    assert statuses["attemptsObox"] == "exposed"


def test_v7_does_not_create_structural_zero_rules():
    for field in PROMOTED_V7:
        assert team_match_missingness_semantics("2025-26", field) == BLANK_IS_MISSING
        value, structural_zero = normalise_team_match_observation(
            "2025-26",
            field,
            None,
        )
        assert value is None
        assert structural_zero is False


def test_v7_preserves_competition_specific_card_overlap_and_winning_goal_holds():
    statuses = _team_statuses()
    assert statuses.get("putThrough") != "exposed"
    assert statuses.get("successfulPutThrough") != "exposed"
    assert statuses.get("redCard") != "exposed"
    assert statuses.get("yellowCard") != "exposed"
    assert statuses.get("winningGoal") != "exposed"
    assert statuses["totalRedCard"] == "exposed"
    assert statuses["totalYelCard"] == "exposed"
