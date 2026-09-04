from __future__ import annotations

from scripts.build_team_match_promotion_review_pack import build_review_pack


def _row(**overrides):
    row = {
        'source_field': 'accurateBackZonePass',
        'candidate_tier': 'FIRST_PROMOTION_REVIEW_BATCH',
        'taxonomy_category': 'Passing & Distribution',
        'taxonomy_secondary_category': '',
        'reconciliation_status': 'EXISTING_SOURCE_FIELD_UNCATALOGUED',
        'source_native_research_access': 'AVAILABLE_VIA_RESEARCH_FIELD_QUERY',
        'existing_coverage_class': 'CORE_DECADE',
        'existing_first_seen_season': '2016-17',
        'existing_last_seen_season': '2025-26',
        'raw_snapshot_coverage_pct': '100.0',
        'raw_value_types': 'integer',
        'raw_sample_values': '42',
        'aggregation_review_hint': 'NUMERIC_COUNT_OR_MEASURE_REVIEW',
    }
    row.update(overrides)
    return row


def test_review_pack_only_includes_first_batch_candidates():
    result = build_review_pack([
        _row(),
        _row(source_field='otherField', candidate_tier='P0_PROMOTION_REVIEW'),
    ])

    assert result['candidate_count'] == 1
    assert result['rows'][0]['source_field'] == 'accurateBackZonePass'
    assert result['rows'][0]['governance_decision'] == 'UNREVIEWED'


def test_full_presence_clear_name_gets_semantic_confirmation_lane():
    result = build_review_pack([
        _row(source_field='forwardPass', raw_snapshot_coverage_pct='100.0')
    ])
    row = result['rows'][0]

    assert row['proposed_label'] == 'Forward Pass'
    assert row['promotion_readiness'] == 'A_SEMANTIC_CONFIRMATION_THEN_PROMOTION_CANDIDATE'
    assert row['missingness_review'].startswith('FULL_RAW_PATH_PRESENCE')


def test_cryptic_or_sparse_field_stays_review_gated():
    result = build_review_pack([
        _row(source_field='attIbox', raw_snapshot_coverage_pct='61.2')
    ])
    row = result['rows'][0]

    assert row['semantic_name_confidence'] == 'MEDIUM_REQUIRES_SOURCE_DEFINITION'
    assert row['promotion_readiness'] == 'C_MISSINGNESS_AND_SEMANTIC_REVIEW_REQUIRED'
    assert 'Confirm friendly label against source semantics' in row['review_questions']
