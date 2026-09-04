from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pulselive_fixture_evidence


MAX_SAMPLE_VALUES = 3
MAX_SAMPLE_MATCHES = 5


def _normalise_path(path: str) -> str:
    return path.replace('.[].', '[].').replace('.[]', '[]')


def _scalar_type(value: Any) -> str:
    if value is None:
        return 'null'
    if isinstance(value, bool):
        return 'boolean'
    if isinstance(value, int) and not isinstance(value, bool):
        return 'integer'
    if isinstance(value, float):
        return 'number'
    return 'string'


def _safe_sample(value: Any) -> str:
    if value is None:
        return ''
    text = str(value).replace('\n', ' ').replace('\r', ' ').strip()
    return text[:160]


def _walk_scalars(value: Any, prefix: str = '') -> Iterable[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            child_prefix = f'{prefix}.{key}' if prefix else str(key)
            yield from _walk_scalars(child, child_prefix)
        return
    if isinstance(value, list):
        child_prefix = f'{prefix}[]' if prefix else '[]'
        if not value:
            # Preserve knowledge that an array exists even when this snapshot has no rows.
            yield _normalise_path(child_prefix), None
            return
        for child in value:
            yield from _walk_scalars(child, child_prefix)
        return
    if prefix:
        yield _normalise_path(prefix), value


def _leaf_name(path: str) -> str:
    tail = path.rsplit('.', 1)[-1]
    return tail.replace('[]', '')


def _entity_level(resource: str, path: str) -> tuple[str, str]:
    low_resource = resource.casefold()
    low = path.casefold()

    if resource.startswith('__resource_meta__:') or resource == '__snapshot_meta__':
        return 'Capture metadata', 'metadata envelope'
    if resource == '__fixture_context__' or 'fixture' in low_resource:
        return 'Fixture / match', 'fixture resource or fixture context'
    if 'manager' in low:
        return 'Manager', 'manager path'
    if any(token in low for token in ('players[]', 'playerid', 'playername', 'shirt', 'substitute')) and 'stats' not in low_resource:
        return 'Player / lineup', 'player-like lineup path'
    if any(token in low for token in ('goals[]', 'cards[]', 'subs[]', 'events[]', 'commentary[]')):
        return 'Event', 'event-array path'
    if low_resource == 'stats' or 'teamstat' in low_resource or low.startswith('[].stats.'):
        return 'Team-match statistic', 'stats resource'
    if any(token in low for token in ('formation', 'lineup', 'teamcontext')):
        return 'Team / lineup', 'formation or lineup path'
    if any(token in low for token in ('hometeam', 'awayteam', 'teamid', 'teamname')):
        return 'Team / match context', 'team-side context path'
    return 'Match resource', 'resource-level fallback'


def _logical_family(path: str, entity_level: str) -> tuple[str, str]:
    low = path.casefold()
    leaf = _leaf_name(path).casefold()

    if entity_level == 'Capture metadata':
        return 'Capture & provenance', 'capture metadata'
    if any(token in low for token in ('manager', 'coach')):
        return 'Managers', 'manager/coach token'
    if any(token in low for token in ('formation', 'lineup', 'shirt', 'substitute', 'captain', 'position')):
        return 'Lineups & roles', 'lineup/role token'
    if any(token in low for token in ('kickoff', 'timestamp', 'minute', 'seconds', 'period', 'clock', 'date', 'status', 'venue', 'attendance')):
        return 'Match context & timing', 'match/timing token'
    if any(token in low for token in ('playerid', 'teamid', 'eventid', 'matchid', 'fixtureid', 'displayname', 'firstname', 'lastname', 'slug', 'code')) or leaf in {'id', 'name'}:
        return 'Identity & relationships', 'identity token'
    if any(token in low for token in ('save', 'keeper', 'goalkeeper', 'claim', 'punch', 'sweeper', 'goalkick')):
        return 'Goalkeeping', 'goalkeeping token'
    if any(token in low for token in ('yellow', 'redcard', 'cardtype', 'foul', 'offside', 'discipline')):
        return 'Discipline', 'discipline token'
    if any(token in low for token in ('assist', 'chancecreated', 'keypass', 'attassist')):
        return 'Creation & assists', 'creation/assist token'
    if any(token in low for token in ('pass', 'cross', 'through', 'chipped')):
        return 'Passing', 'passing token'
    if any(token in low for token in ('possession', 'touch', 'carry', 'progress', 'dribble', 'contest', 'dispossess')):
        return 'Possession & progression', 'possession/progression token'
    if any(token in low for token in ('tackle', 'interception', 'clearance', 'block', 'recovery', 'duel', 'aerial', 'challenge', 'errorlead')):
        return 'Defending & duels', 'defensive token'
    if any(token in low for token in ('shot', 'scoringattempt', 'woodwork', 'expectedgoal', 'bigchancemissed', 'bigchancescored')):
        return 'Shooting & scoring', 'shooting token'
    if 'goal' in low and 'goalassist' not in low and 'goalsconceded' not in low:
        return 'Shooting & scoring', 'goal/scoring token'
    if any(token in low for token in ('meter', 'distance', 'sprint', 'runningkm', 'walkingkm', 'highspeed')):
        return 'Physical output', 'physical-output token'
    if any(token in low for token in ('score', 'winner', 'result')):
        return 'Results', 'result token'
    if entity_level == 'Event':
        return 'Events', 'event fallback'
    return 'Other / review', 'no confident semantic token'


def _payload_and_meta(name: str, resource: Any) -> tuple[Any, dict[str, Any]]:
    if isinstance(resource, dict) and 'payload' in resource:
        metadata = {key: value for key, value in resource.items() if key != 'payload'}
        return resource.get('payload'), metadata
    return resource, {}


def _snapshot_id(snapshot: dict[str, Any], path: Path) -> str:
    fixture = snapshot.get('fixture')
    if isinstance(fixture, dict):
        value = fixture.get('id') or fixture.get('matchId')
        if value not in (None, ''):
            return str(value)
    value = snapshot.get('source_match_id')
    if value not in (None, ''):
        return str(value)
    parent = path.parent.name
    return parent.removeprefix('match-').removeprefix('match_')


def _snapshot_paths(root: Path) -> list[Path]:
    canonical = sorted(root.rglob('snapshot.json'))
    if canonical:
        return canonical
    return sorted(
        path for path in root.rglob('*.json')
        if path.is_file() and path.name not in {'manifest.json', 'source_manifest.json'}
    )


def catalogue_archive(root: Path, *, limit: int | None = None) -> dict[str, Any]:
    paths = _snapshot_paths(root)
    if limit is not None:
        paths = paths[:limit]

    records: dict[tuple[str, str], dict[str, Any]] = {}
    failures: list[dict[str, str]] = []
    snapshots_read = 0

    for path in paths:
        try:
            snapshot = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            failures.append({'path': str(path), 'error': str(exc)})
            continue
        if not isinstance(snapshot, dict):
            failures.append({'path': str(path), 'error': 'Snapshot root is not a JSON object'})
            continue

        snapshots_read += 1
        match_id = _snapshot_id(snapshot, path)
        resources = snapshot.get('resources')
        resources = resources if isinstance(resources, dict) else {}

        scans: list[tuple[str, Any]] = []
        fixture = snapshot.get('fixture')
        if isinstance(fixture, dict):
            scans.append(('__fixture_context__', fixture))
        snapshot_meta = {
            key: value for key, value in snapshot.items()
            if key not in {'resources', 'fixture'}
        }
        if snapshot_meta:
            scans.append(('__snapshot_meta__', snapshot_meta))

        for name, resource in resources.items():
            payload, metadata = _payload_and_meta(str(name), resource)
            scans.append((str(name), payload))
            if metadata:
                scans.append((f'__resource_meta__:{name}', metadata))

        seen_this_snapshot: set[tuple[str, str]] = set()
        for resource_name, payload in scans:
            for variable_path, value in _walk_scalars(payload):
                key = (resource_name, variable_path)
                if key not in records:
                    entity_level, entity_basis = _entity_level(resource_name, variable_path)
                    family, family_basis = _logical_family(variable_path, entity_level)
                    records[key] = {
                        'resource': resource_name,
                        'path': variable_path,
                        'leaf_name': _leaf_name(variable_path),
                        'entity_level': entity_level,
                        'entity_classification_basis': entity_basis,
                        'logical_family': family,
                        'family_classification_basis': family_basis,
                        'snapshot_count': 0,
                        'scalar_observations': 0,
                        'non_null_observations': 0,
                        'value_types': Counter(),
                        'sample_values': [],
                        'sample_match_ids': [],
                    }
                record = records[key]
                record['scalar_observations'] += 1
                value_type = _scalar_type(value)
                record['value_types'][value_type] += 1
                if value is not None:
                    record['non_null_observations'] += 1
                    sample = _safe_sample(value)
                    if sample and sample not in record['sample_values'] and len(record['sample_values']) < MAX_SAMPLE_VALUES:
                        record['sample_values'].append(sample)
                if match_id and match_id not in record['sample_match_ids'] and len(record['sample_match_ids']) < MAX_SAMPLE_MATCHES:
                    record['sample_match_ids'].append(match_id)
                if key not in seen_this_snapshot:
                    record['snapshot_count'] += 1
                    seen_this_snapshot.add(key)

    rows: list[dict[str, Any]] = []
    for record in records.values():
        rows.append({
            **{key: value for key, value in record.items() if key != 'value_types'},
            'value_types': ', '.join(sorted(record['value_types'])),
            'snapshot_coverage_pct': round(record['snapshot_count'] / snapshots_read * 100.0, 1) if snapshots_read else 0.0,
            'sample_values': ' | '.join(record['sample_values']),
            'sample_match_ids': ', '.join(record['sample_match_ids']),
        })
    rows.sort(key=lambda row: (
        row['entity_level'].casefold(),
        row['logical_family'].casefold(),
        row['resource'].casefold(),
        row['path'].casefold(),
    ))

    by_entity = Counter(row['entity_level'] for row in rows)
    by_family = Counter(row['logical_family'] for row in rows)
    by_resource = Counter(row['resource'] for row in rows)

    return {
        'archive_root': str(root),
        'snapshot_files_scanned': len(paths),
        'snapshots_read': snapshots_read,
        'distinct_variables': len(rows),
        'distinct_variables_by_entity_level': dict(sorted(by_entity.items())),
        'distinct_variables_by_logical_family': dict(sorted(by_family.items())),
        'distinct_variables_by_resource': dict(sorted(by_resource.items())),
        'rows': rows,
        'failures': failures,
        'classification_note': (
            'Entity level and logical family are deterministic first-pass classifications based on '
            'resource/path semantics. They should be human-reviewed before becoming governed FRL ontology.'
        ),
    }


CSV_FIELDS = (
    'entity_level',
    'logical_family',
    'resource',
    'path',
    'leaf_name',
    'snapshot_count',
    'snapshot_coverage_pct',
    'scalar_observations',
    'non_null_observations',
    'value_types',
    'sample_values',
    'sample_match_ids',
    'entity_classification_basis',
    'family_classification_basis',
)


def write_catalogue(result: dict[str, Any], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / 'pulselive_raw_variable_catalogue.csv'
    json_path = output_dir / 'pulselive_raw_variable_catalogue.json'

    with csv_path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in result['rows']:
            writer.writerow({field: row.get(field, '') for field in CSV_FIELDS})

    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    return csv_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            'Catalogue every scalar variable preserved in PulseLive snapshots, with '
            'resource, entity-level, semantic-family and coverage metadata.'
        )
    )
    parser.add_argument(
        '--archive-root',
        type=Path,
        help='Explicit PulseLive archive root. Defaults to FRL archive discovery.',
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=ROOT / 'data' / 'audits' / 'pulselive_raw_variables',
        help='Directory for CSV and JSON outputs.',
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Optional maximum number of snapshot files to inspect.',
    )
    args = parser.parse_args()

    root = args.archive_root.expanduser().resolve() if args.archive_root else pulselive_fixture_evidence.archive_root()
    if root is None or not root.is_dir():
        raise SystemExit(
            'No PulseLive archive root was found. Set FRL_PULSELIVE_ARCHIVE_ROOT '
            'or pass --archive-root.'
        )
    if args.limit is not None and args.limit < 1:
        raise SystemExit('--limit must be at least 1 when supplied.')

    result = catalogue_archive(root, limit=args.limit)
    csv_path, json_path = write_catalogue(result, args.output_dir.expanduser().resolve())

    summary = {
        key: result[key]
        for key in (
            'archive_root',
            'snapshot_files_scanned',
            'snapshots_read',
            'distinct_variables',
            'distinct_variables_by_entity_level',
            'distinct_variables_by_logical_family',
            'distinct_variables_by_resource',
        )
    }
    summary['csv_output'] = str(csv_path)
    summary['json_output'] = str(json_path)
    summary['failures'] = len(result['failures'])
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
