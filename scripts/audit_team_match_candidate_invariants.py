from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from source_field_catalog import SEASONS
from source_family_adapters import team_match_source_rows_for_season

DEFAULT_OUTPUT_DIR = ROOT / 'data' / 'audits' / 'team_match_candidate_invariants'

# These are empirical consistency checks, not definitions. Passing one can
# support semantic review; it cannot by itself prove source semantics.
INVARIANTS: tuple[dict[str, str], ...] = (
    {
        'rule_id': 'won_contest_lte_total_contest',
        'child_field': 'wonContest',
        'parent_field': 'totalContest',
        'rationale': 'Won contests should be a subset of total contests.',
    },
    {
        'rule_id': 'effective_head_clearance_lte_head_clearance',
        'child_field': 'effectiveHeadClearance',
        'parent_field': 'headClearance',
        'rationale': 'Effective headed clearances should be a subset of headed clearances.',
    },
    {
        'rule_id': 'successful_long_own_to_opp_lte_total',
        'child_field': 'longPassOwnToOppSuccess',
        'parent_field': 'longPassOwnToOpp',
        'rationale': 'Successful own-half-to-opposition-half long passes should not exceed attempts.',
    },
    {
        'rule_id': 'successful_open_play_pass_lte_open_play_pass',
        'child_field': 'successfulOpenPlayPass',
        'parent_field': 'openPlayPass',
        'rationale': 'Successful open-play passes should not exceed open-play pass attempts.',
    },
    {
        'rule_id': 'accurate_noncorner_cross_lte_total_noncorner_cross',
        'child_field': 'accurateCrossNocorner',
        'parent_field': 'totalCrossNocorner',
        'rationale': 'Accurate non-corner crosses should not exceed non-corner cross attempts.',
    },
    {
        'rule_id': 'aerial_won_lte_duel_won',
        'child_field': 'aerialWon',
        'parent_field': 'duelWon',
        'rationale': 'If duelWon is all duels won, aerial wins should be a subset.',
    },
    {
        'rule_id': 'aerial_lost_lte_duel_lost',
        'child_field': 'aerialLost',
        'parent_field': 'duelLost',
        'rationale': 'If duelLost is all duels lost, aerial losses should be a subset.',
    },
)


def _number(value: object) -> float | None:
    if value in (None, '', 'null', 'None'):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def evaluate_invariants(
    rows: Iterable[Mapping[str, object]],
    *,
    season: str = '',
    rules: Sequence[Mapping[str, str]] = INVARIANTS,
) -> tuple[dict[str, object], ...]:
    materialised = tuple(rows)
    results: list[dict[str, object]] = []

    for rule in rules:
        child = str(rule['child_field'])
        parent = str(rule['parent_field'])
        compared = 0
        violations = 0
        negative_values = 0
        max_excess = 0.0
        examples: list[dict[str, object]] = []

        for row in materialised:
            child_value = _number(row.get(child))
            parent_value = _number(row.get(parent))
            if child_value is None or parent_value is None:
                continue
            compared += 1
            if child_value < 0 or parent_value < 0:
                negative_values += 1
            excess = child_value - parent_value
            if excess > 1e-9:
                violations += 1
                max_excess = max(max_excess, excess)
                if len(examples) < 5:
                    examples.append({
                        'fixture_id': str(row.get('frl_fixture_id') or row.get('matchId') or ''),
                        'team': str(row.get('team') or row.get('team_id') or ''),
                        'child_value': child_value,
                        'parent_value': parent_value,
                    })

        if compared == 0:
            status = 'NO_COMPARABLE_OBSERVATIONS'
        elif violations == 0 and negative_values == 0:
            status = 'EMPIRICALLY_CONSISTENT_NO_VIOLATIONS'
        else:
            status = 'REVIEW_VIOLATIONS'

        results.append({
            'season': season,
            'rule_id': str(rule['rule_id']),
            'child_field': child,
            'parent_field': parent,
            'rationale': str(rule['rationale']),
            'rows_available': len(materialised),
            'rows_compared': compared,
            'violations': violations,
            'negative_value_rows': negative_values,
            'max_child_minus_parent': round(max_excess, 6),
            'status': status,
            'example_violations': examples,
            'governance_note': (
                'Empirical consistency is supporting evidence only. A zero-violation result '
                'does not by itself prove the source definition or approve aggregation, '
                'missingness, comparability or product exposure.'
            ),
        })

    return tuple(results)


def build_audit(seasons: Sequence[str] = SEASONS) -> dict[str, object]:
    season_results: list[dict[str, object]] = []
    season_row_counts: dict[str, int] = {}

    for season in seasons:
        rows = team_match_source_rows_for_season(season)
        season_row_counts[season] = len(rows)
        season_results.extend(evaluate_invariants(rows, season=season))

    rule_summaries: list[dict[str, object]] = []
    for rule in INVARIANTS:
        rule_id = rule['rule_id']
        items = [row for row in season_results if row['rule_id'] == rule_id]
        compared = sum(int(row['rows_compared']) for row in items)
        violations = sum(int(row['violations']) for row in items)
        negative = sum(int(row['negative_value_rows']) for row in items)
        seasons_compared = sum(int(row['rows_compared']) > 0 for row in items)
        if compared == 0:
            status = 'NO_COMPARABLE_OBSERVATIONS'
        elif violations == 0 and negative == 0:
            status = 'DECADE_EMPIRICALLY_CONSISTENT'
        else:
            status = 'DECADE_REVIEW_REQUIRED'
        rule_summaries.append({
            'rule_id': rule_id,
            'child_field': rule['child_field'],
            'parent_field': rule['parent_field'],
            'seasons_compared': seasons_compared,
            'rows_compared': compared,
            'violations': violations,
            'negative_value_rows': negative,
            'status': status,
        })

    return {
        'schema_version': '1.0.0',
        'seasons': list(seasons),
        'season_row_counts': season_row_counts,
        'rule_count': len(INVARIANTS),
        'summary_status_counts': dict(sorted(Counter(str(row['status']) for row in rule_summaries).items())),
        'rule_summaries': rule_summaries,
        'season_results': season_results,
        'interpretation': (
            'This audit tests conservative subset/count relationships among first-batch '
            'team-match promotion candidates. It supplies empirical semantic evidence but '
            'does not automatically promote any source field.'
        ),
    }


SUMMARY_FIELDS = (
    'rule_id', 'child_field', 'parent_field', 'seasons_compared', 'rows_compared',
    'violations', 'negative_value_rows', 'status',
)


def write_audit(result: Mapping[str, object], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / 'team_match_candidate_invariant_summary.csv'
    json_path = output_dir / 'team_match_candidate_invariants.json'

    with csv_path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        for row in result['rule_summaries']:
            writer.writerow({field: row.get(field, '') for field in SUMMARY_FIELDS})

    json_path.write_text(json.dumps(dict(result), indent=2, ensure_ascii=False), encoding='utf-8')
    return csv_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Audit empirical subset/count invariants for first-batch team-match candidates.'
    )
    parser.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    result = build_audit()
    csv_path, json_path = write_audit(result, args.output_dir.expanduser().resolve())
    print(json.dumps({
        'seasons': result['seasons'],
        'season_row_counts': result['season_row_counts'],
        'rule_count': result['rule_count'],
        'summary_status_counts': result['summary_status_counts'],
        'rule_summaries': result['rule_summaries'],
        'csv_output': str(csv_path),
        'json_output': str(json_path),
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
