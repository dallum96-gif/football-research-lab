from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from source_field_catalog import build_catalog
from source_field_registry import fields_for_family

DEFAULT_RAW_CATALOGUE = (
    ROOT / 'data' / 'audits' / 'pulselive_raw_variables' / 'pulselive_raw_variable_catalogue.csv'
)
DEFAULT_OUTPUT_DIR = ROOT / 'data' / 'audits' / 'pulselive_team_stat_reconciliation'


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open('r', encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def _normalise_source_catalog(rows: Iterable[Mapping[str, object]]) -> dict[str, dict[str, object]]:
    return {
        str(row.get('source_field') or '').strip(): dict(row)
        for row in rows
        if str(row.get('source_field') or '').strip()
    }


def _normalise_registry(rows: Iterable[object]) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for row in rows:
        if isinstance(row, Mapping):
            field = str(row.get('source_field') or '').strip()
            status = str(row.get('semantic_status') or '').strip()
            frl_field = row.get('frl_field')
            notes = str(row.get('notes') or '')
        else:
            field = str(getattr(row, 'source_field', '') or '').strip()
            status = str(getattr(row, 'semantic_status', '') or '').strip()
            frl_field = getattr(row, 'frl_field', None)
            notes = str(getattr(row, 'notes', '') or '')
        if field:
            result[field] = {
                'source_field': field,
                'semantic_status': status,
                'frl_field': frl_field,
                'notes': notes,
            }
    return result


def _reconciliation_status(
    *,
    source_catalog_row: Mapping[str, object] | None,
    registry_row: Mapping[str, object] | None,
) -> tuple[str, str]:
    if registry_row is not None:
        semantic_status = str(registry_row.get('semantic_status') or 'unknown').strip().lower()
        if semantic_status == 'exposed':
            return 'EXISTING_EXPOSED', 'VERIFY_GENERIC_ACCESS'
        if semantic_status == 'derived':
            return 'EXISTING_DERIVED', 'VERIFY_DERIVATION_ROUTE'
        if semantic_status == 'retained':
            return 'EXISTING_RETAINED', 'SEMANTIC_AND_AGGREGATION_REVIEW'
        if semantic_status == 'restricted':
            return 'EXISTING_RESTRICTED', 'RESOLVE_RESTRICTION'
        return 'EXISTING_REGISTRY_UNKNOWN', 'SEMANTIC_REVIEW'
    if source_catalog_row is not None:
        return 'EXISTING_SOURCE_FIELD_UNCATALOGUED', 'SEMANTIC_AND_AGGREGATION_REVIEW'
    return 'RAW_SNAPSHOT_ONLY', 'DISCOVER_PACKAGED_EQUIVALENT_OR_ROUTE'


def reconcile_rows(
    raw_rows: Iterable[Mapping[str, object]],
    *,
    source_catalog_rows: Iterable[Mapping[str, object]],
    registry_rows: Iterable[object],
) -> tuple[dict[str, object], ...]:
    """Reconcile raw PulseLive team-match paths with existing FRL source machinery.

    This is an audit layer only. A raw-path or field-name match does not promote a
    variable to canonical/governed/product-ready status.
    """
    source_catalog = _normalise_source_catalog(source_catalog_rows)
    registry = _normalise_registry(registry_rows)

    reconciled: list[dict[str, object]] = []
    for raw in raw_rows:
        if str(raw.get('entity_level') or '') != 'Team-match statistic':
            continue
        if str(raw.get('resource') or '') != 'stats':
            continue

        leaf = str(raw.get('leaf_name') or '').strip()
        if not leaf:
            path = str(raw.get('path') or '').strip()
            leaf = path.rsplit('.', 1)[-1].replace('[]', '') if path else ''
        if not leaf:
            continue

        source_row = source_catalog.get(leaf)
        registry_row = registry.get(leaf)
        status, next_action = _reconciliation_status(
            source_catalog_row=source_row,
            registry_row=registry_row,
        )

        reconciled.append({
            'raw_resource': str(raw.get('resource') or ''),
            'raw_path': str(raw.get('path') or ''),
            'source_field': leaf,
            'raw_logical_family': str(raw.get('logical_family') or ''),
            'raw_snapshot_count': str(raw.get('snapshot_count') or ''),
            'raw_snapshot_coverage_pct': str(raw.get('snapshot_coverage_pct') or ''),
            'raw_value_types': str(raw.get('value_types') or ''),
            'raw_sample_values': str(raw.get('sample_values') or ''),
            'reconciliation_status': status,
            'next_action': next_action,
            'existing_registry_status': (
                str(registry_row.get('semantic_status') or '') if registry_row else ''
            ),
            'existing_frl_field': (
                str(registry_row.get('frl_field') or '') if registry_row else ''
            ),
            'existing_first_seen_season': (
                str(source_row.get('first_seen_season') or '') if source_row else ''
            ),
            'existing_last_seen_season': (
                str(source_row.get('last_seen_season') or '') if source_row else ''
            ),
            'existing_coverage_class': (
                str(source_row.get('coverage_class') or '') if source_row else ''
            ),
            'existing_notes': (
                str(registry_row.get('notes') or '')
                if registry_row and registry_row.get('notes')
                else str(source_row.get('notes') or '') if source_row else ''
            ),
            'governance_note': (
                'Audit match only. Field-name/source presence does not prove canonical '
                'equivalence, aggregation semantics, sparse-zero semantics, comparability '
                'or product readiness.'
            ),
        })

    reconciled.sort(key=lambda row: (
        str(row['reconciliation_status']),
        str(row['raw_logical_family']).casefold(),
        str(row['source_field']).casefold(),
        str(row['raw_path']).casefold(),
    ))
    return tuple(reconciled)


OUTPUT_FIELDS = (
    'raw_resource',
    'raw_path',
    'source_field',
    'raw_logical_family',
    'raw_snapshot_count',
    'raw_snapshot_coverage_pct',
    'raw_value_types',
    'raw_sample_values',
    'reconciliation_status',
    'next_action',
    'existing_registry_status',
    'existing_frl_field',
    'existing_first_seen_season',
    'existing_last_seen_season',
    'existing_coverage_class',
    'existing_notes',
    'governance_note',
)


def build_reconciliation(raw_catalogue: Path) -> dict[str, object]:
    raw_rows = _read_csv(raw_catalogue)
    source_catalog_rows = build_catalog(families=('team_match',))
    registry_rows = fields_for_family('team_match')
    rows = reconcile_rows(
        raw_rows,
        source_catalog_rows=source_catalog_rows,
        registry_rows=registry_rows,
    )
    statuses = Counter(str(row['reconciliation_status']) for row in rows)
    actions = Counter(str(row['next_action']) for row in rows)
    families = Counter(str(row['raw_logical_family']) for row in rows)
    return {
        'schema_version': '1.0.0',
        'raw_catalogue': str(raw_catalogue),
        'team_match_raw_paths': len(rows),
        'status_counts': dict(sorted(statuses.items())),
        'next_action_counts': dict(sorted(actions.items())),
        'raw_family_counts': dict(sorted(families.items())),
        'rows': list(rows),
        'interpretation': (
            'This audit reconciles raw PulseLive team-match paths against the existing '
            'FRL source-field catalogue/registry. It is not a canonical-variable promotion '
            'and must not be used as evidence of semantic equivalence by field name alone.'
        ),
    }


def write_reconciliation(result: Mapping[str, object], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / 'pulselive_team_stat_reconciliation.csv'
    json_path = output_dir / 'pulselive_team_stat_reconciliation.json'

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
            'Reconcile the raw PulseLive team-match-statistic inventory with FRL source '
            'catalogue/registry status without promoting semantics by field-name match.'
        )
    )
    parser.add_argument(
        '--raw-catalogue',
        type=Path,
        default=DEFAULT_RAW_CATALOGUE,
        help='CSV produced by catalogue_pulselive_snapshot_variables.py.',
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help='Output directory for reconciliation CSV/JSON.',
    )
    args = parser.parse_args()

    raw_catalogue = args.raw_catalogue.expanduser().resolve()
    if not raw_catalogue.is_file():
        raise SystemExit(
            f'Raw catalogue not found: {raw_catalogue}. Run '
            'scripts/catalogue_pulselive_snapshot_variables.py first.'
        )

    result = build_reconciliation(raw_catalogue)
    csv_path, json_path = write_reconciliation(result, args.output_dir.expanduser().resolve())

    summary = {
        key: result[key]
        for key in ('team_match_raw_paths', 'status_counts', 'next_action_counts', 'raw_family_counts')
    }
    summary['csv_output'] = str(csv_path)
    summary['json_output'] = str(json_path)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
