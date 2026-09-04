from __future__ import annotations

from scripts.audit_team_match_promotion_v2_evidence import (
    evaluate_lost_corners_opponent_equality,
    evaluate_subset_rules,
    profile_fields,
)


def test_subset_rule_zero_violations_is_consistent():
    rows = [
        {"successfulFinalThirdPasses": 7, "totalFinalThirdPasses": 10},
        {"successfulFinalThirdPasses": 0, "totalFinalThirdPasses": 2},
    ]
    rules = ({
        "rule_id": "test",
        "child_field": "successfulFinalThirdPasses",
        "parent_field": "totalFinalThirdPasses",
        "rationale": "test",
    },)

    result = evaluate_subset_rules(rows, rules=rules)[0]

    assert result["rows_compared"] == 2
    assert result["violations"] == 0
    assert result["status"] == "EMPIRICALLY_CONSISTENT_NO_VIOLATIONS"


def test_subset_rule_reports_violations_without_reinterpreting_data():
    rows = [{"touchesInOppBox": 11, "touches": 10}]
    rules = ({
        "rule_id": "test",
        "child_field": "touchesInOppBox",
        "parent_field": "touches",
        "rationale": "test",
    },)

    result = evaluate_subset_rules(rows, rules=rules)[0]

    assert result["violations"] == 1
    assert result["status"] == "REVIEW_VIOLATIONS"


def test_lost_corners_matches_opponent_corner_taken_when_semantics_align():
    rows = [
        {"frl_fixture_id": "1", "team_id": "10", "lostCorners": 3, "cornerTaken": 5},
        {"frl_fixture_id": "1", "team_id": "20", "lostCorners": 5, "cornerTaken": 3},
    ]

    result = evaluate_lost_corners_opponent_equality(rows)

    assert result["rows_compared"] == 2
    assert result["mismatches"] == 0
    assert result["status"] == "EMPIRICALLY_IDENTICAL_NO_MISMATCHES"


def test_lost_corners_mismatch_is_not_silently_accepted():
    rows = [
        {"frl_fixture_id": "1", "team_id": "10", "lostCorners": 4, "cornerTaken": 5},
        {"frl_fixture_id": "1", "team_id": "20", "lostCorners": 5, "cornerTaken": 3},
    ]

    result = evaluate_lost_corners_opponent_equality(rows)

    assert result["mismatches"] == 1
    assert result["status"] == "REVIEW_MISMATCHES"


def test_field_profile_keeps_blank_and_zero_distinct():
    rows = [
        {"touches": 0},
        {"touches": ""},
        {"touches": 12},
    ]

    profile = profile_fields(rows)["touches"]

    assert profile["nonblank_rows"] == 2
    assert profile["numeric_rows"] == 2
    assert profile["zero_rows"] == 1
