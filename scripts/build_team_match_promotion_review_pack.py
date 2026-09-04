from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE = (
    ROOT / 'data' / 'audits' / 'team_match_capability_queue' / 'team_match_capability_queue.csv'
)
DEFAULT_OUTPUT_DIR = ROOT / 'data' / 'audits' / 'team_match_promotion_review'

FIRST_BATCH = 'FIRST_PROMOTION_REVIEW_BATCH'


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open('r', encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def _humanise(name: str) -> str:
    text = name.replace('_', ' ').replace('-', ' ')
    text = re.sub(r'(?<=[a-z0-9])(?=[A-Z])', ' ', text)
    text = re.sub(r'(?<=[A-Z])(?=[A-Z][a-z])', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    replacements = {
        'Att': 'Attempt',
        'Poss': 'Possession',
        'Opp': 'Opposition',
        'Fwd': 'Forward',
        'Def': 'Defensive',
        'Ibox': 'In box',
        'Obox': 'Outside box',
        'Fk': 'Free-kick',
        'Pct': '%',
    }
    words = [replacements.get(word, word) for word in text.split()]
    label = ' '.join(words)
    return label[:1].upper() + label[1:] if label else name


def _float(value: object) -> float | None:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def _semantic_name_confidence(field: str) -> str:
    low = field.casefold()
    cryptic = ('att', 'ibox', 'obox', 'poss', 'zone', 'putthrough', 'ontarget', 'fk')
    if any(token in low for token in cryptic):
        return 'MEDIUM_REQUIRES_SOURCE_DEFINITION'
    return 'HIGH_NAME_CLARITY_NOT_YET_GOVERNED'


def _missingness_lane(row: Mapping[str, object]) -> str:
    coverage = _float(row.get('raw_snapshot_coverage_pct'))
    if coverage is None:
        return 'MISSINGNESS_EVIDENCE_REQUIRED'
    if coverage >= 99.999:
        return 'FULL_RAW_PATH_PRESENCE_STILL_CONFIRM_BLANK_SEMANTICS'
    return 'SPARSE_OR_OPTIONAL_SOURCE_ENCODING_REVIEW'


def _aggregation_lane(row: Mapping[str, object]) -> str:
    hint = str(row.get('aggregation_review_hint') or '')
    if hint == 'NUMERIC_COUNT_OR_MEASURE_REVIEW':
        return 'FIXTURE_NUMERIC_REVIEW_SUM_AND_PER_MATCH_POSSIBLE_NOT_APPROVED'
    if hint == 'RATIO_OR_PERCENTAGE_REVIEW':
        return 'RATIO_WEIGHTING_OR_DENOMINATOR_REVIEW'
    if hint == 'EXPECTED_METRIC_SPECIAL_ROUTE_REVIEW':
        return 'EXPECTED_METRIC_ROUTING_REVIEW'
    return 'MANUAL_AGGREGATION_REVIEW'


def _readiness(row: Mapping[str, object]) -> str:
    if str(row.get('candidate_tier') or '') != FIRST_BATCH:
        return 'OUTSIDE_FIRST_BATCH'
    missingness = _missingness_lane(row)
    confidence = _semantic_name_confidence(str(row.get('source_field') or ''))
    if missingness.startswith('FULL_') and confidence.startswith('HIGH_'):
        return 'A_SEMANTIC_CONFIRMATION_THEN_PROMOTION_CANDIDATE'
    if missingness.startswith('FULL_'):
        return 'B_SOURCE_DEFINITION_CONFIRMATION_REQUIRED'
    return 'C_MISSINGNESS_AND_SEMANTIC_REVIEW_REQUIRED'


def _review_questions(row: Mapping[str, object]) -> str:
    questions = [
        'Confirm source definition and unit',
        'Confirm natural team-match grain',
        'Confirm valid season roll-ups',
        'Confirm blank/zero semantics',
        'Confirm decade comparability',
    ]
    if _semantic_name_confidence(str(row.get('source_field') or '')).startswith('MEDIUM_'):
        questions.insert(1, 'Confirm friendly label against source semantics')
    return '; '.join(questions)


def build_review_pack(queue_rows: Iterable[Mapping[str, object]]) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for source in queue_rows:
        if str(source.get('candidate_tier') or '') != FIRST_BATCH:
            continue
        field = str(source.get('source_field') or '').strip()
        if not field:
            continue
        rows.append({
            'source_field': field,
            'proposed_label': _humanise(field),
            'taxonomy_category': str(source.get('taxonomy_category') or ''),
            'taxonomy_secondary_category': str(source.get('taxonomy_secondary_category') or ''),
            'source_status': str(source.get('reconciliation_status') or ''),
            'source_access': str(source.get('source_native_research_access') or ''),
            'coverage_class': str(source.get('existing_coverage_class') or ''),
            'first_seen_season': str(source.get('existing_first_seen_season') or ''),
            'last_seen_season': str(source.get('existing_last_seen_season') or ''),
            'raw_snapshot_coverage_pct': str(source.get('raw_snapshot_coverage_pct') or ''),
            'raw_value_types': str(source.get('raw_value_types') or ''),
            'raw_sample_values': str(source.get('raw_sample_values') or ''),
            'semantic_name_confidence': _semantic_name_confidence(field),
            'aggregation_review': _aggregation_lane(source),
            'missingness_review': _missingness_lane(source),
            'promotion_readiness': _readiness(source),
            'review_questions': _review_questions(source),
            'governance_decision': 'UNREVIEWED',
            'governance_note': (
                'First-batch triage only. No proposed label, aggregation hint, coverage class '
                'or raw-path presence establishes semantic promotion by itself.'
            ),
        })

    readiness_order = {
        'A_SEMANTIC_CONFIRMATION_THEN_PROMOTION_CANDIDATE': 0,
        'B_SOURCE_DEFINITION_CONFIRMATION_REQUIRED': 1,
        'C_MISSINGNESS_AND_SEMANTIC_REVIEW_REQUIRED': 2,
    }
    rows.sort(key=lambda row: (
        readiness_order.get(str(row['promotion_readiness']), 99),
        str(row['taxonomy_category']).casefold(),
        str(row['source_field']).casefold(),
    ))

    return {
        'schema_version': '1.0.0',
        'review_scope': FIRST_BATCH,
        'candidate_count': len(rows),
        'taxonomy_counts': dict(sorted(Counter(str(row['taxonomy_category']) for row in rows).items())),
        'readiness_counts': dict(sorted(Counter(str(row['promotion_readiness']) for row in rows).items())),
        'missingness_review_counts': dict(sorted(Counter(str(row['missingness_review']) for row in rows).items())),
        'semantic_name_confidence_counts': dict(sorted(Counter(str(row['semantic_name_confidence']) for row in rows).items())),
        'rows': rows,
        'interpretation': (
            'This pack narrows the semantic review workload. It does not auto-promote fields. '
            'Promotion still requires explicit source-definition, aggregation, missingness and '
            'comparability decisions before source_field_registry changes.'
        ),
    }


OUTPUT_FIELDS = (
    'source_field',
    'proposed_label',
    'taxonomy_category',
    'taxonomy_secondary_category',
    'source_status',
    'source_access',
    'coverage_class',
    'first_seen_season',
    'last_seen_season',
    'raw_snapshot_coverage_pct',
    'raw_value_types',
    'raw_sample_values',
    'semantic_name_confidence',
    'aggregation_review',
    'missingness_review',
    'promotion_readiness',
    'review_questions',
    'governance_decision',
    'governance_note',
)


def write_review_pack(result: Mapping[str, object], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / 'team_match_first_promotion_review.csv'
    json_path = output_dir / 'team_match_first_promotion_review.json'
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
            'Build a conservative human-review pack for the first team-match source-field '
            'promotion tranche. No registry mutation is performed.'
        )
    )
    parser.add_argument('--queue', type=Path, default=DEFAULT_QUEUE)
    parser.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    queue_path = args.queue.expanduser().resolve()
    if not queue_path.is_file():
        raise SystemExit(
            f'Capability queue not found: {queue_path}. Run '
            'scripts/triage_team_match_capability_queue.py first.'
        )

    result = build_review_pack(_read_csv(queue_path))
    csv_path, json_path = write_review_pack(result, args.output_dir.expanduser().resolve())
    preview = [
        {
            'source_field': row['source_field'],
            'proposed_label': row['proposed_label'],
            'category': row['taxonomy_category'],
            'readiness': row['promotion_readiness'],
        }
        for row in list(result['rows'])[:20]
    ]
    summary = {
        key: result[key]
        for key in (
            'candidate_count',
            'taxonomy_counts',
            'readiness_counts',
            'missingness_review_counts',
            'semantic_name_confidence_counts',
        )
    }
    summary['first_20_candidates'] = preview
    summary['csv_output'] = str(csv_path)
    summary['json_output'] = str(json_path)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
