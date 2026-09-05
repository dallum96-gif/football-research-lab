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
MANIFEST = ROOT / "data" / "team_match_semantic_promotion_batch_v6.json"
EVIDENCE = ROOT / "data" / "team_match_semantic_evidence_v6.json"

PROMOTED_V6 = {
    "accurateFreekickCross", "attCorner", "attFastbreak", "attFreekickGoal",
    "attFreekickMiss", "attFreekickTarget", "attFreekickTotal", "attObxdLeft",
    "attObxdRight", "attOneOnOne", "attOpenplay", "attPenGoal", "attPenMiss",
    "attPenPost", "attPenTarget", "attPostHigh", "attPostLeft", "attPostRight",
    "attSetpiece", "attemptedTackleFoul", "clearanceOffLine", "contentiousDecision",
    "defenderGoals", "dispossessed", "forwardGoals", "foulThrowIn", "goalAssist",
    "goalAssistDeadball", "goalAssistIntentional", "goalAssistOpenplay",
    "goalAssistSetplay", "goalFastbreak", "goalsOpenplay", "goodHighClaim",
    "handBall", "midfielderGoals", "offtargetAttAssist", "ontargetAttAssist",
    "ownGoals", "penGoalsConceded", "penaltyConceded", "penaltyFaced",
    "penaltySave", "penaltyWon", "possLostCtrl", "postScoringAtt", "punches",
    "rescindedRedCard", "secondYellow", "shieldBallOop", "shotFastbreak",
    "sixYardBlock", "totalAttAssist", "totalFastbreak",
}

HISTORICALLY_HELD_AFTER_V6 = {
    "attFreekickPost", "attIboxOwnGoal", "attLgCentre", "attLgLeft", "attLgRight",
    "attOboxOwnGoal", "attemptsIbox", "attemptsObox", "expectedGoalsFreekick",
    "expectedGoalsOnTargetConceded", "fiftyFifty", "freekickTotal", "keeperGoals",
    "ptsDroppedWinningPos", "ptsGainedLosingPos", "putThrough", "redCard",
    "subsGoals", "successfulFiftyFifty", "successfulPutThrough", "totalDistance",
    "winningGoal", "yellowCard",
}

STILL_HELD_AFTER_V7 = {
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


def test_v6_manifest_records_verified_bulk_batch_and_expected_gate():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["status"] == "VERIFIED_GENERIC_ACCESS"
    assert manifest["promotion_count"] == 54
    assert set(manifest["promoted_fields"]) == PROMOTED_V6
    assert set(manifest["explicitly_held_fields"]) == HISTORICALLY_HELD_AFTER_V6
    expected = manifest["expected_post_gate"]["reconciliation"]
    assert expected == {
        "team_match_raw_paths": 249,
        "EXISTING_EXPOSED": 167,
        "EXISTING_SOURCE_FIELD_UNCATALOGUED": 23,
        "RAW_SNAPSHOT_ONLY": 59,
    }


def test_v6_exact_reference_map_covers_every_promoted_field():
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert set(evidence["exact_key_map"]) == PROMOTED_V6


def test_v6_fields_are_exposed_in_team_registry():
    statuses = _team_statuses()
    assert PROMOTED_V6 <= statuses.keys()
    assert {statuses[field] for field in PROMOTED_V6} == {"exposed"}


def test_v6_historical_hold_set_can_be_superseded_by_v7_without_rewriting_history():
    statuses = _team_statuses()
    promoted_later = HISTORICALLY_HELD_AFTER_V6 - STILL_HELD_AFTER_V7
    assert {statuses[field] for field in promoted_later} == {"exposed"}
    assert all(statuses.get(field) != "exposed" for field in STILL_HELD_AFTER_V7)


def test_v6_does_not_create_structural_zero_rules():
    for field in PROMOTED_V6:
        assert team_match_missingness_semantics("2025-26", field) == BLANK_IS_MISSING
        value, structural_zero = normalise_team_match_observation(
            "2025-26",
            field,
            None,
        )
        assert value is None
        assert structural_zero is False


def test_v6_keeps_card_event_counts_distinct_from_existing_team_totals():
    statuses = _team_statuses()
    assert statuses["totalRedCard"] == "exposed"
    assert statuses["totalYelCard"] == "exposed"
    assert statuses.get("redCard") != "exposed"
    assert statuses.get("yellowCard") != "exposed"
    assert statuses["secondYellow"] == "exposed"
    assert statuses["rescindedRedCard"] == "exposed"


def test_v6_rejects_competition_specific_put_through_fields():
    statuses = _team_statuses()
    assert statuses.get("putThrough") != "exposed"
    assert statuses.get("successfulPutThrough") != "exposed"
