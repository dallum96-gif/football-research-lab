from __future__ import annotations

from scripts.build_team_match_post_v3_evidence_matrix import build_matrix


def _row(field: str, *, coverage: str = "100", priority: str = "P0", category: str = "Passing & Distribution") -> dict[str, str]:
    return {
        "source_field": field,
        "reconciliation_status": "EXISTING_SOURCE_FIELD_UNCATALOGUED",
        "taxonomy_category": category,
        "product_priority": priority,
        "candidate_tier": "FIRST_PROMOTION_REVIEW_BATCH",
        "raw_snapshot_coverage_pct": coverage,
    }


def test_matrix_only_contains_packaged_uncatalogued_fields():
    rows = [
        _row("candidateA"),
        {**_row("alreadyExposed"), "reconciliation_status": "EXISTING_EXPOSED"},
        {**_row("rawOnly"), "reconciliation_status": "RAW_SNAPSHOT_ONLY"},
    ]
    result = build_matrix(rows, manifests=({},), evidence_docs=({},))
    assert result["candidate_count"] == 1
    assert result["rows"][0]["source_field"] == "candidateA"


def test_external_semantic_support_outranks_coverage_heuristics():
    evidence = {
        "fields": {
            "supportedField": {
                "support_grade": "HIGH_DIRECT_DEFINITION_SUPPORT",
                "proposed_label": "Supported field",
                "note": "Direct definition.",
            }
        }
    }
    result = build_matrix(
        [_row("supportedField", coverage="95.0")],
        manifests=({},),
        evidence_docs=(evidence,),
    )
    row = result["rows"][0]
    assert row["post_v3_review_lane"] == "EXTERNAL_SEMANTIC_SUPPORT_REVIEW"
    assert row["coverage_shape"] == "HIGH_PARTIAL"


def test_near_complete_clear_field_is_coverage_aware_not_rejected():
    result = build_matrix(
        [_row("clearMetric", coverage="99.5")],
        manifests=({},),
        evidence_docs=({},),
    )
    row = result["rows"][0]
    assert row["coverage_shape"] == "NEAR_COMPLETE"
    assert row["post_v3_review_lane"] == "COVERAGE_AWARE_CLEAR_FIELD_REVIEW"


def test_prior_direct_definition_hold_is_preserved():
    manifest = {"explicitly_held_fields": ["totalContest"]}
    result = build_matrix(
        [_row("totalContest")],
        manifests=(manifest,),
        evidence_docs=({},),
    )
    row = result["rows"][0]
    assert row["prior_hold"] is True
    assert row["post_v3_review_lane"] == "DIRECT_DEFINITION_HOLD"


def test_conflicted_or_falsified_hold_stays_hard_hold():
    manifest = {
        "explicitly_held_fields": {
            "lostCorners": "Opponent route produced 145 mismatches.",
            "penAreaEntries": "Proposed nesting was falsified by 35 violations.",
        }
    }
    result = build_matrix(
        [_row("lostCorners"), _row("penAreaEntries")],
        manifests=(manifest,),
        evidence_docs=({},),
    )
    assert {row["post_v3_review_lane"] for row in result["rows"]} == {
        "HARD_HOLD_CONFLICT_OR_FALSIFIED_ASSUMPTION"
    }


def test_relationship_opportunity_detects_success_counterpart():
    rows = [_row("longBall"), _row("longBallSuccess")]
    result = build_matrix(rows, manifests=({},), evidence_docs=({},))
    by_field = {row["source_field"]: row for row in result["rows"]}
    assert by_field["longBallSuccess"]["relationship_hint"] == "POTENTIAL_EMPIRICAL_RELATIONSHIP"
    assert by_field["longBallSuccess"]["relationship_counterpart"] == "longBall"


def test_cryptic_qualifier_does_not_enter_clear_name_lane():
    result = build_matrix(
        [_row("attObxLeft")],
        manifests=({},),
        evidence_docs=({},),
    )
    row = result["rows"][0]
    assert row["name_clarity"] == "LOW_OR_MEDIUM_DIRECT_DEFINITION_REQUIRED"
    assert row["post_v3_review_lane"] == "QUALIFIER_OR_CRYPTIC_DEFINITION_REVIEW"
