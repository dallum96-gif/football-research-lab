from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.reconcile_pulselive_team_stat_capability import (
    DEFAULT_RAW_CATALOGUE,
    build_reconciliation,
)
from source_field_taxonomy import classify_field

DEFAULT_OUTPUT_DIR = ROOT / 'data' / 'audits' / 'team_match_capability_queue'


P0_CATEGORIES = {
    'Shooting & Finishing',
    'Chance Creation',
    'Passing & Distribution',
    'Crossing & Set Pieces',
    'Dribbling & Carrying',
    'Possession & Ball Security',
    'Duels & Aerials',
    'Defending',
    'Goalkeeping',
    'Team Attack',
    'Team Defence',
}
P1_CATEGORIES = {
    'Discipline',
    'Physical & Tracking',
}


def _priority(category: str) -> str:
    if category in P0_CATEGORIES:
        return 'P0'
    if category in P1_CATEGORIES:
        return 'P1'
    return 'P2'


def _review_lane(status: str) -> str:
    if status == 'EXISTING_EXPOSED':
        return 'VERIFY_EXISTING_GENERIC_ACCESS'
    if status == 'EXISTING_SOURCE_FIELD_UNCATALOGUED':
        return 'SEMANTIC_PROMOTION_REVIEW'
    if status == 'RAW_SNAPSHOT_ONLY':
        return 'PACKAGED_ROUTE_DISCOVERY'
    if status == 'EXISTING_RETAINED':
        return 'RETAINED_FIELD_REVIEW'
    if status == 'EXISTING_DERIVED':
        return 'DERIVATION_ROUTE_REVIEW'
    return 'MANUAL_GOVERNANCE_REVIEW'


def _aggregation_hint(field: str, category: str, value_types: str) -> str:
    """Return a conservative review hint, never an approved aggregation rule."""
    low = field.casefold()
    types = {part.strip().casefold() for part in value_types.split(',') if part.strip()}

    if 'expected' in low or low.startswith('xg') or 'xgot' in low:
        return 'EXPECTED_METRIC_SPECIAL_ROUTE_REVIEW'
    if any(token in low for token in ('percentage', 'percent', 'pct', 'accuracy', 'rate', 'ratio')):
        return 'RATIO_OR_PERCENTAGE_REVIEW'
    if category in {'Identity & Context', 'Tactical & Match Context', 'Playing Time'}:
        return 'CONTEXT_SEMANTICS_REVIEW'
    if types & {'string', 'boolean'}:
        return 'CATEGORICAL_OR_CONTEXT_REVIEW'
    if types and types <= {'integer', 'number', 'null'}:
        return 'NUMERIC_COUNT_OR_MEASURE_REVIEW'
    return 'UNKNOWN_AGGREGATION_REVIEW'


def _semantic_confidence(status: str, category: str) -> str:
    if status == 'EXISTING_EXPOSED':
        return 'HIGH_GOVERNED'
    if category == 'Unclassified Review':
        return 'LOW'
    if category in {'Tactical & Match Context', 'Identity & Context'}:
        return 'MEDIUM_LOW'
    return 'MEDIUM'


def _candidate_tier(row: Mapping[str, object]) -> str:
    """Prioritise review effort without automatically promoting semantics."""
    status = str(row['reconciliation_status'])
    priority = str(row['product_priority'])
    coverage = str(row.get('existing_coverage_class') or '')
    category = str(row['taxonomy_category'])
    hint = str(row['aggregation_review_hint'])

    if status == 'EXISTING_EXPOSED':
        return 'ALREADY_EXPOSED'
    if status == 'EXISTING_SOURCE_FIELD_UNCATALOGUED':
        if (
            priority == 'P0'
            and coverage == 'CORE_DECADE'
            and category != 'Unclassified Review'
            and hint == 'NUMERIC_COUNT_OR_MEASURE_REVIEW'
        ):
            return 'FIRST_PROMOTION_REVIEW_BATCH'
        if priority == 'P0':
            return 'P0_PROMOTION_REVIEW'
        if priority == 'P1':
            return 'P1_PROMOTION_REVIEW'
        return 'P2_PROMOTION_REVIEW'
    if status == 'RAW_SNAPSHOT_ONLY':
        return f'{priority}_ROUTE_DISCOVERY'
    return 'MANUAL_REVIEW'


def build_queue(raw_catalogue: Path) -> dict[str, object]:
    reconciliation = build_reconciliation(raw_catalogue)
    rows: list[dict[str, object]] = []

    for source in reconciliation['rows']:
        field = str(source['source_field'])
        category, secondary = classify_field('team_match', field)
        status = str(source['reconciliation_status'])
        priority = _priority(category)
        value_types = str(source.get('raw_value_types') or '')

        row: dict[str, object] = {
            **source,
            'taxonomy_category': category,
            'taxonomy_secondary_category': secondary or '',
            'product_priority': priority,
            'review_lane': _review_lane(status),
            'aggregation_review_hint': _aggregation_hint(field, category, value_types),
            'semantic_confidence': _semantic_confidence(status, category),
            'source_native_research_access': (
                'AVAILABLE_VIA_RESEARCH_FIELD_QUERY'
                if status != 'RAW_SNAPSHOT_ONLY'
                else 'RAW_SNAPSHOT_EVIDENCE_ONLY'
            ),
        }
        row['candidate_tier'] = _candidate_tier(row)
        rows.append(row)

    tier_order = {
        'ALREADY_EXPOSED': 0,
        'FIRST_PROMOTION_REVIEW_BATCH': 1,
        'P0_PROMOTION_REVIEW': 2,
        'P1_PROMOTION_REVIEW': 3,
        'P2_PROMOTION_REVIEW': 4,
        'P0_ROUTE_DISCOVERY': 5,
        'P1_ROUTE_DISCOVERY': 6,
        'P2_ROUTE_DISCOVERY': 7,
        'MANUAL_REVIEW': 8,
    }
    rows.sort(key=lambda item: (
        tier_order.get(str(item['candidate_tier']), 99),
        str(item['taxonomy_category']).casefold(),
        str(item['source_field']).casefold(),
    ))

    return {
        'schema_version': '1.0.0',
        'raw_catalogue': str(raw_catalogue),
        'team_match_fields': len(rows),
        'status_counts': dict(sorted(Counter(str(row['reconciliation_status']) for row in rows).items())),
        'taxonomy_counts': dict(sorted(Counter(str(row['taxonomy_category']) for row in rows).items())),
        'priority_counts': dict(sorted(Counter(str(row['product_priority']) for row in rows).items())),
        'review_lane_counts': dict(sorted(Counter(str(row['review_lane']) for row in rows).items())),
        'candidate_tier_counts': dict(sorted(Counter(str(row['candidate_tier']) for row in rows).items())),
        'rows': rows,
        'interpretation': (
            'This is a review queue, not a promotion registry. Category, priority and '
            'aggregation fields are triage aids. No uncatalogued or raw-only field becomes '
            'canonical, comparable, aggregatable or product-ready because it appears here.'
        ),
    }


OUTPUT_FIELDS = (
    'source_field',
    'reconciliation_status',
    'source_native_research_access',
    'taxonomy_category',
    'taxonomy_secondary_category',
    'product_priority',
    'candidate_tier',
    'review_lane',
    'aggregation_review_hint',
    'semantic_confidence',
    'existing_first_seen_season',
    'existing_last_seen_season',
    'existing_coverage_class',
    'raw_snapshot_count',
    'raw_snapshot_coverage_pct',
    'raw_value_types',
    'raw_sample_values',
    'raw_path',
    'governance_note',
)


def write_queue(result: Mapping[str, object], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / 'team_match_capability_queue.csv'
    json_path = output_dir / 'team_match_capability_queue.json'
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
            'Prioritise the reconciled PulseLive team-match capability universe for '
            'semantic promotion or packaged-route discovery.'
        )
    )
    parser.add_argument('--raw-catalogue', type=Path, default=DEFAULT_RAW_CATALOGUE)
    parser.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    raw_catalogue = args.raw_catalogue.expanduser().resolve()
    if not raw_catalogue.is_file():
        raise SystemExit(
            f'Raw catalogue not found: {raw_catalogue}. Run the raw PulseLive catalogue first.'
        )

    result = build_queue(raw_catalogue)
    csv_path, json_path = write_queue(result, args.output_dir.expanduser().resolve())
    summary = {
        key: result[key]
        for key in (
            'team_match_fields',
            'status_counts',
            'taxonomy_counts',
            'priority_counts',
            'review_lane_counts',
            'candidate_tier_counts',
        )
    }
    summary['csv_output'] = str(csv_path)
    summary['json_output'] = str(json_path)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
