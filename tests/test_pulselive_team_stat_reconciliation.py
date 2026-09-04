from __future__ import annotations

from dataclasses import dataclass

from scripts.reconcile_pulselive_team_stat_capability import reconcile_rows


@dataclass(frozen=True)
class _RegistryRow:
    source_field: str
    semantic_status: str
    frl_field: str | None = None
    notes: str = ''


def _raw(field: str, *, family: str = 'Passing') -> dict[str, object]:
    return {
        'entity_level': 'Team-match statistic',
        'resource': 'stats',
        'path': f'[].stats.{field}',
        'leaf_name': field,
        'logical_family': family,
        'snapshot_count': '3800',
        'snapshot_coverage_pct': '100.0',
        'value_types': 'integer, number',
        'sample_values': '1 | 2 | 3',
    }


def test_reconciliation_distinguishes_exposed_retained_uncatalogued_and_raw_only() -> None:
    raw_rows = [
        _raw('totalPass'),
        _raw('ground', family='Other / review'),
        _raw('knownButUncatalogued', family='Other / review'),
        _raw('snapshotOnlyMetric', family='Other / review'),
    ]
    source_catalog_rows = [
        {
            'source_field': 'totalPass',
            'registry_status': 'exposed',
            'first_seen_season': '2016-17',
            'last_seen_season': '2025-26',
            'coverage_class': 'CORE_DECADE',
            'notes': '',
        },
        {
            'source_field': 'ground',
            'registry_status': 'retained',
            'first_seen_season': '2016-17',
            'last_seen_season': '2025-26',
            'coverage_class': 'CORE_DECADE',
            'notes': '',
        },
        {
            'source_field': 'knownButUncatalogued',
            'registry_status': 'UNCATALOGUED',
            'first_seen_season': '2022-23',
            'last_seen_season': '2025-26',
            'coverage_class': 'INTERMITTENT',
            'notes': 'Discovered in approved source; semantic review pending.',
        },
    ]
    registry_rows = [
        _RegistryRow('totalPass', 'exposed'),
        _RegistryRow('ground', 'retained'),
    ]

    rows = reconcile_rows(
        raw_rows,
        source_catalog_rows=source_catalog_rows,
        registry_rows=registry_rows,
    )
    by_field = {str(row['source_field']): row for row in rows}

    assert by_field['totalPass']['reconciliation_status'] == 'EXISTING_EXPOSED'
    assert by_field['totalPass']['next_action'] == 'VERIFY_GENERIC_ACCESS'
    assert by_field['ground']['reconciliation_status'] == 'EXISTING_RETAINED'
    assert by_field['ground']['next_action'] == 'SEMANTIC_AND_AGGREGATION_REVIEW'
    assert by_field['knownButUncatalogued']['reconciliation_status'] == 'EXISTING_SOURCE_FIELD_UNCATALOGUED'
    assert by_field['snapshotOnlyMetric']['reconciliation_status'] == 'RAW_SNAPSHOT_ONLY'
    assert by_field['snapshotOnlyMetric']['next_action'] == 'DISCOVER_PACKAGED_EQUIVALENT_OR_ROUTE'


def test_reconciliation_only_includes_stats_resource_team_match_rows() -> None:
    raw_rows = [
        _raw('totalPass'),
        {
            **_raw('playerId', family='Identity & relationships'),
            'entity_level': 'Player / lineup',
            'resource': 'lineups',
            'path': 'homeTeam.players[].playerId',
        },
        {
            **_raw('minute', family='Events'),
            'entity_level': 'Event',
            'resource': 'events',
            'path': 'homeTeam.goals[].minute',
        },
    ]

    rows = reconcile_rows(
        raw_rows,
        source_catalog_rows=[{'source_field': 'totalPass'}],
        registry_rows=[_RegistryRow('totalPass', 'exposed')],
    )

    assert len(rows) == 1
    assert rows[0]['source_field'] == 'totalPass'


def test_reconciliation_is_deterministic_and_does_not_claim_canonical_equivalence() -> None:
    raw_rows = [
        _raw('zMetric', family='Shooting & scoring'),
        _raw('aMetric', family='Passing'),
    ]

    first = reconcile_rows(
        raw_rows,
        source_catalog_rows=[],
        registry_rows=[],
    )
    second = reconcile_rows(
        reversed(raw_rows),
        source_catalog_rows=[],
        registry_rows=[],
    )

    assert first == second
    assert [row['source_field'] for row in first] == ['aMetric', 'zMetric']
    assert all('does not prove canonical equivalence' in str(row['governance_note']) for row in first)
