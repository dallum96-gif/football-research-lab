from reconcile_variable_universe import reconcile


def test_exact_family_field_grain_match_is_reconciled():
    rows = reconcile(
        [
            {
                "source_family": "player_match",
                "source_field": "successfulDribbles",
                "candidate_name": "successfulDribbles",
                "canonical_variable": "successfulDribbles",
                "natural_grain": "player_fixture",
                "semantic_status": "validated",
                "coverage": "10/10",
            }
        ],
        [
            {
                "source_family": "player_match",
                "source_field": "successfulDribbles",
                "candidate_name": "successfulDribbles",
                "canonical_variable": "successfulDribbles",
                "natural_grain": "player_fixture",
                "semantic_status": "exposed",
                "coverage": "10/10",
            }
        ],
    )
    assert len(rows) == 1
    assert rows[0].reconciliation_status == "MAPPED_VALIDATED"
    assert rows[0].baseline_present is True
    assert rows[0].broad_universe_present is True


def test_broad_only_field_is_unmapped():
    rows = reconcile(
        [],
        [
            {
                "source_family": "player_match",
                "source_field": "exampleNativeField",
                "candidate_name": "exampleNativeField",
                "canonical_variable": "",
                "natural_grain": "player_fixture",
                "semantic_status": "retained",
                "coverage": "10/10",
            }
        ],
    )
    assert rows[0].reconciliation_status == "SOURCE_NATIVE_UNMAPPED"


def test_duplicate_reconciliation_key_is_flagged():
    record = {
        "source_family": "team_match",
        "source_field": "possessionPercentage",
        "candidate_name": "possessionPercentage",
        "canonical_variable": "possession",
        "natural_grain": "team_fixture",
        "semantic_status": "exposed",
        "coverage": "10/10",
    }
    rows = reconcile([record, record], [record])
    assert rows[0].reconciliation_status == "DUPLICATE_SOURCE_FACET"
