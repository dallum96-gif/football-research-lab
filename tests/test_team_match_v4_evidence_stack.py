from __future__ import annotations

from scripts.audit_team_match_v4_evidence_stack import (
    build_audit,
    evaluate_relationships,
    relationship_rules,
)


def test_relationship_rules_include_matrix_counterparts_and_explicit_keeper_pair():
    matrix = [
        {
            "source_field": "accurateLongBalls",
            "relationship_counterpart": "totalLongBalls",
            "post_v3_review_lane": "CLEAR_COMPLETE_SOURCE_FIELD_REVIEW",
        },
        {
            "source_field": "accurateKeeperThrows",
            "relationship_counterpart": "",
            "post_v3_review_lane": "COVERAGE_AWARE_CLEAR_FIELD_REVIEW",
        },
        {
            "source_field": "keeperThrows",
            "relationship_counterpart": "",
            "post_v3_review_lane": "COVERAGE_AWARE_CLEAR_FIELD_REVIEW",
        },
    ]
    rules = relationship_rules(matrix, evidence_fields={"accurateKeeperThrows"})
    pairs = {(row["child_field"], row["parent_field"]) for row in rules}
    assert ("accurateLongBalls", "totalLongBalls") in pairs
    assert ("accurateKeeperThrows", "keeperThrows") in pairs


def test_relationship_evaluation_is_fail_closed_on_violations_and_skips_blanks():
    rules = (
        {
            "rule_id": "accurateLongBalls_lte_totalLongBalls",
            "child_field": "accurateLongBalls",
            "parent_field": "totalLongBalls",
            "rationale": "test",
        },
    )
    rows = [
        {"accurateLongBalls": 5, "totalLongBalls": 10},
        {"accurateLongBalls": "", "totalLongBalls": 8},
        {"accurateLongBalls": 12, "totalLongBalls": 10},
    ]
    result = evaluate_relationships(rows, rules=rules, season="2025-26")[0]
    assert result["rows_compared"] == 2
    assert result["violations"] == 1
    assert result["status"] == "REVIEW_VIOLATIONS"


def test_build_audit_combines_external_support_and_consistent_relationship(monkeypatch):
    matrix = [
        {
            "source_field": "accurateLongBalls",
            "relationship_counterpart": "totalLongBalls",
            "post_v3_review_lane": "CLEAR_COMPLETE_SOURCE_FIELD_REVIEW",
            "coverage_shape": "COMPLETE",
            "external_support_grade": "NO_EXTERNAL_EVIDENCE_RECORDED",
            "external_proposed_label": "",
        },
        {
            "source_field": "totalLongBalls",
            "relationship_counterpart": "",
            "post_v3_review_lane": "CLEAR_COMPLETE_SOURCE_FIELD_REVIEW",
            "coverage_shape": "COMPLETE",
            "external_support_grade": "NO_EXTERNAL_EVIDENCE_RECORDED",
            "external_proposed_label": "",
        },
    ]
    evidence = {
        "fields": {
            "accurateLongBalls": {
                "support_grade": "MEDIUM_EXTERNAL_CONCEPT_SUPPORT",
                "proposed_label": "Accurate long balls",
            },
            "totalLongBalls": {
                "support_grade": "HIGH_EXTERNAL_CONCEPT_SUPPORT",
                "proposed_label": "Long balls",
            },
        }
    }

    import scripts.audit_team_match_v4_evidence_stack as module

    monkeypatch.setattr(
        module,
        "team_match_source_rows_for_season",
        lambda season: [
            {
                "frl_fixture_id": "1",
                "team_id": "A",
                "accurateLongBalls": 7,
                "totalLongBalls": 12,
            }
        ],
    )
    result = build_audit(matrix, evidence, seasons=("2025-26",))
    by_field = {row["source_field"]: row for row in result["candidates"]}
    assert by_field["accurateLongBalls"]["evidence_status"] == "EXTERNAL_SUPPORT_PLUS_CONSISTENT_RELATIONSHIP"
    assert by_field["accurateLongBalls"]["profile"]["nonblank_rows"] == 1
    assert result["relationship_status_counts"] == {"DECADE_EMPIRICALLY_CONSISTENT": 1}


def test_lost_corners_external_definition_does_not_create_opponent_equality_rule(monkeypatch):
    matrix = [
        {
            "source_field": "lostCorners",
            "relationship_counterpart": "",
            "post_v3_review_lane": "HARD_HOLD_CONFLICT_OR_FALSIFIED_ASSUMPTION",
            "coverage_shape": "HIGH_PARTIAL",
            "external_support_grade": "NO_EXTERNAL_EVIDENCE_RECORDED",
            "external_proposed_label": "",
        }
    ]
    evidence = {
        "fields": {
            "lostCorners": {
                "support_grade": "HIGH_DIRECT_DEFINITION_SUPPORT",
                "proposed_label": "Corners lost / conceded",
            }
        }
    }

    import scripts.audit_team_match_v4_evidence_stack as module

    monkeypatch.setattr(
        module,
        "team_match_source_rows_for_season",
        lambda season: [{"lostCorners": ""}],
    )
    result = build_audit(matrix, evidence, seasons=("2025-26",))
    row = next(item for item in result["candidates"] if item["source_field"] == "lostCorners")
    assert row["relationship"] is None
    assert row["profile"]["blank_rows"] == 1
    assert row["evidence_status"] == "EXTERNAL_SUPPORT_PROFILE_REVIEW"
