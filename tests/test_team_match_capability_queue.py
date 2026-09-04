from __future__ import annotations

from scripts.triage_team_match_capability_queue import build_queue


def test_queue_prioritises_core_decade_uncatalogued_numeric_p0_field(monkeypatch, tmp_path):
    raw = tmp_path / "raw.csv"
    raw.write_text("placeholder", encoding="utf-8")

    monkeypatch.setattr(
        "scripts.triage_team_match_capability_queue.build_reconciliation",
        lambda path: {
            "rows": [
                {
                    "source_field": "forwardPass",
                    "reconciliation_status": "EXISTING_SOURCE_FIELD_UNCATALOGUED",
                    "existing_coverage_class": "CORE_DECADE",
                    "raw_value_types": "integer",
                    "raw_snapshot_count": "3800",
                    "raw_snapshot_coverage_pct": "100.0",
                    "raw_sample_values": "200",
                    "raw_path": "[].stats.forwardPass",
                    "governance_note": "audit only",
                }
            ]
        },
    )

    result = build_queue(raw)
    row = result["rows"][0]

    assert row["taxonomy_category"] == "Passing & Distribution"
    assert row["product_priority"] == "P0"
    assert row["source_native_research_access"] == "AVAILABLE_VIA_RESEARCH_FIELD_QUERY"
    assert row["candidate_tier"] == "FIRST_PROMOTION_REVIEW_BATCH"
    assert row["aggregation_review_hint"] == "NUMERIC_COUNT_OR_MEASURE_REVIEW"


def test_raw_snapshot_only_field_stays_route_discovery(monkeypatch, tmp_path):
    raw = tmp_path / "raw.csv"
    raw.write_text("placeholder", encoding="utf-8")

    monkeypatch.setattr(
        "scripts.triage_team_match_capability_queue.build_reconciliation",
        lambda path: {
            "rows": [
                {
                    "source_field": "newCrossingMetric",
                    "reconciliation_status": "RAW_SNAPSHOT_ONLY",
                    "existing_coverage_class": "",
                    "raw_value_types": "integer",
                    "raw_snapshot_count": "500",
                    "raw_snapshot_coverage_pct": "13.2",
                    "raw_sample_values": "4",
                    "raw_path": "[].stats.newCrossingMetric",
                    "governance_note": "audit only",
                }
            ]
        },
    )

    result = build_queue(raw)
    row = result["rows"][0]

    assert row["reconciliation_status"] == "RAW_SNAPSHOT_ONLY"
    assert row["source_native_research_access"] == "RAW_SNAPSHOT_EVIDENCE_ONLY"
    assert row["candidate_tier"].endswith("_ROUTE_DISCOVERY")


def test_existing_exposed_field_is_not_repromoted(monkeypatch, tmp_path):
    raw = tmp_path / "raw.csv"
    raw.write_text("placeholder", encoding="utf-8")

    monkeypatch.setattr(
        "scripts.triage_team_match_capability_queue.build_reconciliation",
        lambda path: {
            "rows": [
                {
                    "source_field": "totalPass",
                    "reconciliation_status": "EXISTING_EXPOSED",
                    "existing_coverage_class": "CORE_DECADE",
                    "raw_value_types": "integer",
                    "raw_snapshot_count": "3800",
                    "raw_snapshot_coverage_pct": "100.0",
                    "raw_sample_values": "500",
                    "raw_path": "[].stats.totalPass",
                    "governance_note": "audit only",
                }
            ]
        },
    )

    result = build_queue(raw)
    row = result["rows"][0]

    assert row["candidate_tier"] == "ALREADY_EXPOSED"
    assert row["review_lane"] == "VERIFY_EXISTING_GENERIC_ACCESS"
