from __future__ import annotations

from scripts.build_team_match_promotion_v2_queue import build_v2_queue


def _row(field: str, *, tier: str, coverage: str = "100.0", priority: str = "P0"):
    return {
        "source_field": field,
        "reconciliation_status": "EXISTING_SOURCE_FIELD_UNCATALOGUED",
        "taxonomy_category": "Passing & Distribution",
        "taxonomy_secondary_category": "Passing / distribution",
        "product_priority": priority,
        "candidate_tier": tier,
        "existing_coverage_class": "CORE_DECADE",
        "raw_snapshot_coverage_pct": coverage,
        "raw_value_types": "integer",
        "raw_sample_values": "1 | 2 | 3",
    }


def test_v2_queue_excludes_already_promoted_fields():
    result = build_v2_queue(
        [
            _row("backwardPass", tier="FIRST_PROMOTION_REVIEW_BATCH"),
            _row("newClearField", tier="FIRST_PROMOTION_REVIEW_BATCH"),
        ],
        {"promoted_fields": ["backwardPass"], "explicitly_held_fields": []},
        {"fields": {}},
    )

    assert result["candidate_count"] == 1
    assert result["rows"][0]["source_field"] == "newClearField"


def test_v1_held_field_remains_direct_definition_required():
    result = build_v2_queue(
        [_row("wonContest", tier="FIRST_PROMOTION_REVIEW_BATCH")],
        {"promoted_fields": [], "explicitly_held_fields": ["wonContest"]},
        {"fields": {"wonContest": {"support_grade": "LOW_DIRECT_DEFINITION_SUPPORT"}}},
    )

    assert result["rows"][0]["v2_review_lane"] == "V1_HELD_DIRECT_DEFINITION_REQUIRED"
    assert result["rows"][0]["carried_v1_hold"] is True


def test_external_support_can_raise_clear_full_presence_field_to_evidence_stack_review():
    result = build_v2_queue(
        [_row("headedClearance", tier="FIRST_PROMOTION_REVIEW_BATCH")],
        {"promoted_fields": [], "explicitly_held_fields": []},
        {
            "fields": {
                "headedClearance": {
                    "support_grade": "HIGH_EXTERNAL_CONCEPT_SUPPORT",
                    "proposed_label": "Headed clearances",
                    "note": "Official terminology support.",
                }
            }
        },
    )

    row = result["rows"][0]
    assert row["v2_review_lane"] == "V2_EVIDENCE_STACK_REVIEW_NOW"
    assert row["external_support_grade"] == "HIGH_EXTERNAL_CONCEPT_SUPPORT"


def test_sparse_field_is_missingness_first_even_with_clear_name():
    result = build_v2_queue(
        [_row("clearNamedMetric", tier="FIRST_PROMOTION_REVIEW_BATCH", coverage="72.5")],
        {"promoted_fields": [], "explicitly_held_fields": []},
        {"fields": {}},
    )

    assert result["rows"][0]["v2_review_lane"] == "V2_MISSINGNESS_FIRST"


def test_non_packaged_or_exposed_rows_are_not_v2_candidates():
    rows = [
        {
            **_row("rawOnly", tier="P0_ROUTE_DISCOVERY"),
            "reconciliation_status": "RAW_SNAPSHOT_ONLY",
        },
        {
            **_row("alreadyExposed", tier="ALREADY_EXPOSED"),
            "reconciliation_status": "EXISTING_EXPOSED",
        },
    ]
    result = build_v2_queue(
        rows,
        {"promoted_fields": [], "explicitly_held_fields": []},
        {"fields": {}},
    )

    assert result["candidate_count"] == 0
