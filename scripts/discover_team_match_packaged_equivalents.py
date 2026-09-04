from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
from typing import Iterable, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in __import__('sys').path:
    __import__('sys').path.insert(0, str(ROOT))

from source_field_catalog import build_catalog
from source_field_taxonomy import classify_field

DEFAULT_QUEUE = (
    ROOT / 'data' / 'audits' / 'team_match_capability_queue' / 'team_match_capability_queue.csv'
)
DEFAULT_OUTPUT_DIR = ROOT / 'data' / 'audits' / 'team_match_route_discovery'


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open('r', encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def _tokens(name: str) -> tuple[str, ...]:
    spaced = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', name)
    spaced = re.sub(r'[^A-Za-z0-9]+', ' ', spaced).lower()
    aliases = {
        'att': 'attempt', 'atts': 'attempt', 'poss': 'possession', 'fwd': 'forward',
        'opp': 'opposition', 'def': 'defensive', 'ibox': 'insidebox', 'inbox': 'insidebox',
        'obox': 'outsidebox', 'obx': 'outsidebox', 'obxd': 'outsidebox',
        'fk': 'freekick', 'pct': 'percentage', 'acc': 'accurate',
        'hd': 'header', 'head': 'header', 'headed': 'header',
        'lf': 'leftfoot', 'rf': 'rightfoot', 'pen': 'penalty',
        'goals': 'goal', 'shots': 'shot',
    }
    return tuple(aliases.get(token, token) for token in spaced.split() if token)


def _normalised(name: str) -> str:
    return ''.join(_tokens(name))


def _semantic_signature(name: str) -> dict[str, str | bool]:
    """Extract high-risk qualifiers that must agree for equivalence review.

    This is deliberately conservative. It is not a semantic parser; it only
    blocks obvious false friends such as generic goals vs penalty goals or
    headed attempts vs penalty attempts from receiving a high similarity lane.
    """
    tokens = set(_tokens(name))

    if 'header' in tokens:
        body_part = 'HEADER'
    elif 'leftfoot' in tokens:
        body_part = 'LEFT_FOOT'
    elif 'rightfoot' in tokens:
        body_part = 'RIGHT_FOOT'
    else:
        body_part = ''

    if 'insidebox' in tokens:
        box_location = 'INSIDE_BOX'
    elif 'outsidebox' in tokens:
        box_location = 'OUTSIDE_BOX'
    elif 'box' in tokens:
        box_location = 'BOX_UNSPECIFIED'
    else:
        box_location = ''

    if 'target' in tokens:
        outcome = 'TARGET'
    elif 'miss' in tokens:
        outcome = 'MISS'
    elif 'post' in tokens or 'woodwork' in tokens:
        outcome = 'POST_OR_WOODWORK'
    elif 'goal' in tokens:
        outcome = 'GOAL'
    else:
        outcome = ''

    if 'right' in tokens:
        direction = 'RIGHT'
    elif 'left' in tokens:
        direction = 'LEFT'
    elif 'centre' in tokens or 'center' in tokens:
        direction = 'CENTRE'
    else:
        direction = ''

    return {
        'penalty': 'penalty' in tokens,
        'freekick': 'freekick' in tokens,
        'own_goal': 'own' in tokens and 'goal' in tokens,
        'body_part': body_part,
        'box_location': box_location,
        'outcome': outcome,
        'direction': direction,
    }


def _semantic_conflicts(raw_field: str, candidate: str) -> tuple[str, ...]:
    raw = _semantic_signature(raw_field)
    cand = _semantic_signature(candidate)
    conflicts: list[str] = []

    for key in ('penalty', 'freekick', 'own_goal'):
        if bool(raw[key]) != bool(cand[key]):
            conflicts.append(key)

    for key in ('body_part', 'box_location', 'outcome', 'direction'):
        if str(raw[key]) != str(cand[key]) and (raw[key] or cand[key]):
            conflicts.append(key)

    return tuple(conflicts)


def _score(raw_field: str, candidate: str) -> tuple[float, float, float]:
    raw_tokens = set(_tokens(raw_field))
    cand_tokens = set(_tokens(candidate))
    union = raw_tokens | cand_tokens
    jaccard = (len(raw_tokens & cand_tokens) / len(union)) if union else 0.0
    sequence = SequenceMatcher(None, _normalised(raw_field), _normalised(candidate)).ratio()
    raw_cat, _ = classify_field('team_match', raw_field)
    cand_cat, _ = classify_field('team_match', candidate)
    taxonomy = 1.0 if raw_cat == cand_cat else 0.0
    combined = 0.55 * sequence + 0.30 * jaccard + 0.15 * taxonomy
    return round(combined, 4), round(sequence, 4), round(jaccard, 4)


def suggest_equivalents(
    raw_rows: Iterable[Mapping[str, object]],
    packaged_fields: Iterable[str],
    *,
    top_n: int = 5,
) -> tuple[dict[str, object], ...]:
    candidates = tuple(sorted({str(field).strip() for field in packaged_fields if str(field).strip()}))
    rows: list[dict[str, object]] = []

    for raw in raw_rows:
        if str(raw.get('reconciliation_status') or '') != 'RAW_SNAPSHOT_ONLY':
            continue
        raw_field = str(raw.get('source_field') or '').strip()
        if not raw_field:
            continue

        scored = []
        rejected: list[tuple[str, tuple[str, ...]]] = []
        for candidate in candidates:
            conflicts = _semantic_conflicts(raw_field, candidate)
            if conflicts:
                rejected.append((candidate, conflicts))
                continue
            combined, sequence, jaccard = _score(raw_field, candidate)
            scored.append((combined, sequence, jaccard, candidate))
        scored.sort(key=lambda item: (-item[0], item[3].casefold()))
        top = scored[:top_n]
        best = top[0] if top else (0.0, 0.0, 0.0, '')

        if best[0] >= 0.82:
            lane = 'STRONG_NAME_SIMILARITY_REVIEW'
        elif best[0] >= 0.64:
            lane = 'POSSIBLE_PACKAGED_EQUIVALENT_REVIEW'
        else:
            lane = 'NO_STRONG_PACKAGED_EQUIVALENT_BY_NAME'

        row: dict[str, object] = {
            'raw_source_field': raw_field,
            'taxonomy_category': str(raw.get('taxonomy_category') or classify_field('team_match', raw_field)[0]),
            'raw_snapshot_coverage_pct': str(raw.get('raw_snapshot_coverage_pct') or ''),
            'raw_sample_values': str(raw.get('raw_sample_values') or ''),
            'route_discovery_lane': lane,
            'semantic_guard_status': 'QUALIFIER_GUARD_APPLIED',
            'semantic_conflict_candidates_rejected': len(rejected),
            'best_candidate': best[3],
            'best_score': best[0],
            'governance_note': (
                'Similarity is a discovery aid only. Candidates with incompatible penalty, '
                'set-piece, own-goal, body-part, box-location, outcome or direction qualifiers '
                'are rejected before scoring. Surviving similarity still does not establish '
                'semantic equivalence, source routing, identity compatibility or comparability.'
            ),
        }
        for index, item in enumerate(top, start=1):
            row[f'candidate_{index}'] = item[3]
            row[f'candidate_{index}_score'] = item[0]
        rows.append(row)

    rows.sort(key=lambda row: (
        {'STRONG_NAME_SIMILARITY_REVIEW': 0, 'POSSIBLE_PACKAGED_EQUIVALENT_REVIEW': 1,
         'NO_STRONG_PACKAGED_EQUIVALENT_BY_NAME': 2}.get(str(row['route_discovery_lane']), 9),
        -float(row['best_score']),
        str(row['raw_source_field']).casefold(),
    ))
    return tuple(rows)


def build_discovery(queue_rows: Iterable[Mapping[str, object]]) -> dict[str, object]:
    catalog = build_catalog(families=('team_match',))
    packaged_fields = tuple(str(row['source_field']) for row in catalog)
    rows = suggest_equivalents(queue_rows, packaged_fields)
    return {
        'schema_version': '1.1.0',
        'raw_snapshot_only_fields': len(rows),
        'route_discovery_lane_counts': dict(sorted(Counter(str(row['route_discovery_lane']) for row in rows).items())),
        'semantic_conflict_candidates_rejected': sum(int(row['semantic_conflict_candidates_rejected']) for row in rows),
        'rows': list(rows),
        'interpretation': (
            'This is a guarded discovery aid for the raw-snapshot-only team-match fields. '
            'High-risk qualifier conflicts are rejected before similarity scoring. Surviving '
            'suggestions remain review evidence only and must never be treated as semantic '
            'equivalence without source-level validation.'
        ),
    }


OUTPUT_FIELDS = (
    'raw_source_field', 'taxonomy_category', 'raw_snapshot_coverage_pct', 'raw_sample_values',
    'route_discovery_lane', 'semantic_guard_status', 'semantic_conflict_candidates_rejected',
    'best_candidate', 'best_score',
    'candidate_1', 'candidate_1_score', 'candidate_2', 'candidate_2_score',
    'candidate_3', 'candidate_3_score', 'candidate_4', 'candidate_4_score',
    'candidate_5', 'candidate_5_score', 'governance_note',
)


def write_discovery(result: Mapping[str, object], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / 'team_match_packaged_equivalent_suggestions.csv'
    json_path = output_dir / 'team_match_packaged_equivalent_suggestions.json'
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
        description='Suggest guarded possible packaged equivalents for raw-snapshot-only team-match fields.'
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
    result = build_discovery(_read_csv(queue_path))
    csv_path, json_path = write_discovery(result, args.output_dir.expanduser().resolve())
    preview = [
        {
            'raw_source_field': row['raw_source_field'],
            'lane': row['route_discovery_lane'],
            'best_candidate': row['best_candidate'],
            'best_score': row['best_score'],
            'semantic_conflict_candidates_rejected': row['semantic_conflict_candidates_rejected'],
        }
        for row in list(result['rows'])[:20]
    ]
    print(json.dumps({
        'raw_snapshot_only_fields': result['raw_snapshot_only_fields'],
        'route_discovery_lane_counts': result['route_discovery_lane_counts'],
        'semantic_conflict_candidates_rejected': result['semantic_conflict_candidates_rejected'],
        'first_20_suggestions': preview,
        'csv_output': str(csv_path),
        'json_output': str(json_path),
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
