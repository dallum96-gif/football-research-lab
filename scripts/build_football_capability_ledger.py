from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW_CATALOGUE = (
    ROOT / 'data' / 'audits' / 'pulselive_raw_variables' / 'pulselive_raw_variable_catalogue.csv'
)
DEFAULT_OUTPUT_DIR = ROOT / 'data' / 'audits' / 'football_capability_ledger'


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open('r', encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def _is_capture(row: Mapping[str, object]) -> bool:
    return (
        str(row.get('logical_family') or '') == 'Capture & provenance'
        or str(row.get('entity_level') or '') == 'Capture metadata'
    )


def _workstream(row: Mapping[str, object]) -> str:
    entity = str(row.get('entity_level') or '')
    resource = str(row.get('resource') or '')

    if entity == 'Team-match statistic' and resource == 'stats':
        return 'TEAM_MATCH_STATISTICS'
    if entity == 'Event':
        return 'EVENTS'
    if entity == 'Player / lineup':
        return 'PLAYER_LINEUP_CONTEXT'
    if entity == 'Team / lineup':
        return 'TEAM_LINEUP_CONTEXT'
    if entity == 'Manager':
        return 'MANAGERS'
    if entity == 'Team / match context':
        return 'TEAM_MATCH_CONTEXT'
    if entity == 'Match resource':
        return 'MATCH_CONTEXT'
    return 'FOOTBALL_CONTEXT_REVIEW'


def _capability_role(row: Mapping[str, object], workstream: str) -> str:
    family = str(row.get('logical_family') or '')

    if workstream == 'TEAM_MATCH_STATISTICS':
        return 'ANALYTICAL_METRIC_CANDIDATE'
    if workstream == 'EVENTS':
        return 'EVENT_EVIDENCE'
    if 'Lineup' in workstream:
        return 'SELECTION_ROLE_FORMATION_EVIDENCE'
    if workstream == 'MANAGERS':
        return 'MANAGER_CONTEXT'
    if family in {'Match context & timing', 'Results'}:
        return 'FIXTURE_CONTEXT'
    if family == 'Identity & relationships':
        return 'IDENTITY_RELATIONSHIP_CONTEXT'
    return 'FOOTBALL_CONTEXT'


def build_ledger(raw_rows: Iterable[Mapping[str, object]]) -> dict[str, object]:
    source_rows = [dict(row) for row in raw_rows]
    football_rows = [row for row in source_rows if not _is_capture(row)]
    capture_rows = [row for row in source_rows if _is_capture(row)]

    rows: list[dict[str, object]] = []
    for raw in football_rows:
        workstream = _workstream(raw)
        rows.append({
            'resource': str(raw.get('resource') or ''),
            'path': str(raw.get('path') or ''),
            'leaf_name': str(raw.get('leaf_name') or ''),
            'entity_level': str(raw.get('entity_level') or ''),
            'logical_family': str(raw.get('logical_family') or ''),
            'workstream': workstream,
            'capability_role': _capability_role(raw, workstream),
            'snapshot_count': str(raw.get('snapshot_count') or ''),
            'snapshot_coverage_pct': str(raw.get('snapshot_coverage_pct') or ''),
            'value_types': str(raw.get('value_types') or ''),
            'sample_values': str(raw.get('sample_values') or ''),
            'example_match_ids': str(raw.get('example_match_ids') or ''),
            'source_universe_status': 'FOOTBALL_MATCH_SUBSET_OF_553',
        })

    rows.sort(key=lambda row: (
        str(row['workstream']),
        str(row['logical_family']).casefold(),
        str(row['path']).casefold(),
    ))

    workstreams = Counter(str(row['workstream']) for row in rows)
    entities = Counter(str(row['entity_level']) for row in rows)
    families = Counter(str(row['logical_family']) for row in rows)
    team_stats = sum(row['workstream'] == 'TEAM_MATCH_STATISTICS' for row in rows)
    non_team_stats = len(rows) - team_stats

    return {
        'schema_version': '1.1.0',
        'master_snapshotted_source_paths': len(source_rows),
        'capture_provenance_paths': len(capture_rows),
        'football_match_paths': len(rows),
        'team_match_statistical_paths': team_stats,
        'remaining_football_paths': non_team_stats,
        'workstream_counts': dict(sorted(workstreams.items())),
        'entity_level_counts': dict(sorted(entities.items())),
        'logical_family_counts': dict(sorted(families.items())),
        'rows': rows,
        'interpretation': (
            'The full raw-source master universe is every snapshotted scalar path. '
            'Within that universe, capture/provenance paths are evidence infrastructure '
            'and the non-capture football/match paths are the analytical/context subset. '
            'The 249 team-match statistics are Phase 1 because they share one coherent '
            'analytical grain; the remaining event, lineup, manager and match-context '
            'paths remain explicitly in scope for later phases. Raw-path inclusion does '
            'not itself establish canonical semantics or product readiness.'
        ),
    }


OUTPUT_FIELDS = (
    'resource',
    'path',
    'leaf_name',
    'entity_level',
    'logical_family',
    'workstream',
    'capability_role',
    'snapshot_count',
    'snapshot_coverage_pct',
    'value_types',
    'sample_values',
    'example_match_ids',
    'source_universe_status',
)


def write_ledger(result: Mapping[str, object], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / 'football_capability_ledger.csv'
    json_path = output_dir / 'football_capability_ledger.json'
    rows = list(result.get('rows') or [])

    with csv_path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, '') for field in OUTPUT_FIELDS})

    json_path.write_text(json.dumps(dict(result), indent=2, ensure_ascii=False), encoding='utf-8')
    return csv_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            'Build the explicit source-capability hierarchy: full snapshotted source '
            'universe, capture/provenance subset, football/match subset, and the '
            'team-match-statistics Phase 1 workstream.'
        )
    )
    parser.add_argument('--raw-catalogue', type=Path, default=DEFAULT_RAW_CATALOGUE)
    parser.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    raw_catalogue = args.raw_catalogue.expanduser().resolve()
    if not raw_catalogue.is_file():
        raise SystemExit(
            f'Raw catalogue not found: {raw_catalogue}. Run the PulseLive raw catalogue first.'
        )

    result = build_ledger(_read_csv(raw_catalogue))
    csv_path, json_path = write_ledger(result, args.output_dir.expanduser().resolve())

    summary = {
        key: result[key]
        for key in (
            'master_snapshotted_source_paths',
            'capture_provenance_paths',
            'football_match_paths',
            'team_match_statistical_paths',
            'remaining_football_paths',
            'workstream_counts',
            'entity_level_counts',
        )
    }
    summary['csv_output'] = str(csv_path)
    summary['json_output'] = str(json_path)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
