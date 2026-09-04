from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from source_field_catalog import SEASONS
from source_family_adapters import team_match_source_rows_for_season

DEFAULT_OUTPUT = ROOT / "data" / "audits" / "team_match_promotion_v2" / "team_match_v2_evidence_audit.json"

# Supporting empirical checks only. Zero violations do not prove definitions.
SUBSET_RULES: tuple[dict[str, str], ...] = (
    {
        "rule_id": "successful_final_third_passes_lte_total",
        "child_field": "successfulFinalThirdPasses",
        "parent_field": "totalFinalThirdPasses",
        "rationale": "Successful final-third passes should not exceed total final-third passes.",
    },
    {
        "rule_id": "chipped_passes_lte_total_passes",
        "child_field": "totalChippedPass",
        "parent_field": "totalPass",
        "rationale": "Chipped passes should be a subset of all passes.",
    },
    {
        "rule_id": "touches_in_opposition_box_lte_touches",
        "child_field": "touchesInOppBox",
        "parent_field": "touches",
        "rationale": "Touches in the opposition box should not exceed all touches.",
    },
    {
        "rule_id": "unsuccessful_touch_lte_touches",
        "child_field": "unsuccessfulTouch",
        "parent_field": "touches",
        "rationale": "Unsuccessful touches should not exceed all touches if the fields share the expected event basis.",
    },
    {
        "rule_id": "penalty_area_entries_lte_final_third_entries",
        "child_field": "penAreaEntries",
        "parent_field": "finalThirdEntries",
        "rationale": "Penalty-area entries should not exceed final-third entries if both are nested entry counts.",
    },
    {
        "rule_id": "ball_recoveries_lte_touches",
        "child_field": "ballRecovery",
        "parent_field": "touches",
        "rationale": "Ball recoveries should not exceed all touches if recovery events are represented within the same touch-event population.",
    },
)

PROFILE_FIELDS = (
    "blockedPass",
    "successfulFinalThirdPasses",
    "totalChippedPass",
    "totalFinalThirdPasses",
    "ballRecovery",
    "touches",
    "touchesInOppBox",
    "unsuccessfulTouch",
    "goalKicks",
    "finalThirdEntries",
    "penAreaEntries",
    "lostCorners",
)


def _number(value: object) -> float | None:
    if value in (None, "", "null", "None"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _fixture_id(row: Mapping[str, object]) -> str:
    return str(row.get("frl_fixture_id") or row.get("matchId") or "").strip()


def _team_id(row: Mapping[str, object]) -> str:
    return str(row.get("team_id") or "").strip()


def evaluate_subset_rules(
    rows: Iterable[Mapping[str, object]],
    *,
    rules: Sequence[Mapping[str, str]] = SUBSET_RULES,
) -> tuple[dict[str, object], ...]:
    materialised = tuple(rows)
    results: list[dict[str, object]] = []
    for rule in rules:
        child = str(rule["child_field"])
        parent = str(rule["parent_field"])
        compared = violations = negative = 0
        examples: list[dict[str, object]] = []
        for row in materialised:
            c = _number(row.get(child))
            p = _number(row.get(parent))
            if c is None or p is None:
                continue
            compared += 1
            if c < 0 or p < 0:
                negative += 1
            if c > p + 1e-9:
                violations += 1
                if len(examples) < 5:
                    examples.append({
                        "fixture_id": _fixture_id(row),
                        "team_id": _team_id(row),
                        "child": c,
                        "parent": p,
                    })
        status = (
            "NO_COMPARABLE_OBSERVATIONS" if compared == 0
            else "EMPIRICALLY_CONSISTENT_NO_VIOLATIONS" if violations == 0 and negative == 0
            else "REVIEW_VIOLATIONS"
        )
        results.append({
            "rule_id": rule["rule_id"],
            "child_field": child,
            "parent_field": parent,
            "rows_compared": compared,
            "violations": violations,
            "negative_value_rows": negative,
            "status": status,
            "example_violations": examples,
            "rationale": rule["rationale"],
        })
    return tuple(results)


def evaluate_lost_corners_opponent_equality(
    rows: Iterable[Mapping[str, object]],
) -> dict[str, object]:
    by_fixture: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in rows:
        fid = _fixture_id(row)
        if fid:
            by_fixture[fid].append(row)

    compared = mismatches = 0
    examples: list[dict[str, object]] = []
    for fid, fixture_rows in by_fixture.items():
        if len(fixture_rows) != 2:
            continue
        first, second = fixture_rows
        for subject, opponent in ((first, second), (second, first)):
            lost = _number(subject.get("lostCorners"))
            opponent_corners = _number(opponent.get("cornerTaken"))
            if lost is None or opponent_corners is None:
                continue
            compared += 1
            if abs(lost - opponent_corners) > 1e-9:
                mismatches += 1
                if len(examples) < 5:
                    examples.append({
                        "fixture_id": fid,
                        "team_id": _team_id(subject),
                        "lostCorners": lost,
                        "opponent_cornerTaken": opponent_corners,
                    })

    status = (
        "NO_COMPARABLE_OBSERVATIONS" if compared == 0
        else "EMPIRICALLY_IDENTICAL_NO_MISMATCHES" if mismatches == 0
        else "REVIEW_MISMATCHES"
    )
    return {
        "rule_id": "lost_corners_equals_opponent_corner_taken",
        "field": "lostCorners",
        "opponent_field": "cornerTaken",
        "rows_compared": compared,
        "mismatches": mismatches,
        "status": status,
        "example_mismatches": examples,
        "rationale": "If lostCorners represents corners conceded, it should equal the opponent's corners taken for the same fixture.",
    }


def profile_fields(rows: Iterable[Mapping[str, object]]) -> dict[str, dict[str, object]]:
    materialised = tuple(rows)
    result: dict[str, dict[str, object]] = {}
    for field in PROFILE_FIELDS:
        numeric: list[float] = []
        present = 0
        zero = 0
        for row in materialised:
            raw = row.get(field)
            if raw not in (None, "", "null", "None"):
                present += 1
            value = _number(raw)
            if value is not None:
                numeric.append(value)
                if abs(value) <= 1e-12:
                    zero += 1
        result[field] = {
            "rows": len(materialised),
            "nonblank_rows": present,
            "nonblank_pct": round(present / len(materialised) * 100.0, 3) if materialised else 0.0,
            "numeric_rows": len(numeric),
            "zero_rows": zero,
            "zero_pct_of_numeric": round(zero / len(numeric) * 100.0, 3) if numeric else 0.0,
            "minimum": min(numeric) if numeric else None,
            "maximum": max(numeric) if numeric else None,
            "negative_rows": sum(value < 0 for value in numeric),
            "missingness_note": "Blank and zero remain distinct; this profile does not infer that absent values mean zero.",
        }
    return result


def build_audit(seasons: Sequence[str] = SEASONS) -> dict[str, object]:
    all_rows: list[Mapping[str, object]] = []
    season_counts: dict[str, int] = {}
    season_subset_results: dict[str, list[dict[str, object]]] = {}
    season_corner_results: dict[str, dict[str, object]] = {}

    for season in seasons:
        rows = tuple(team_match_source_rows_for_season(season))
        season_counts[season] = len(rows)
        all_rows.extend(rows)
        season_subset_results[season] = list(evaluate_subset_rules(rows))
        season_corner_results[season] = evaluate_lost_corners_opponent_equality(rows)

    aggregate_subset = list(evaluate_subset_rules(all_rows))
    aggregate_corner = evaluate_lost_corners_opponent_equality(all_rows)
    statuses = Counter(str(row["status"]) for row in aggregate_subset)
    statuses[str(aggregate_corner["status"])] += 1

    return {
        "schema_version": "1.0.0",
        "seasons": list(seasons),
        "season_row_counts": season_counts,
        "total_team_match_rows": len(all_rows),
        "profile_fields": profile_fields(all_rows),
        "aggregate_subset_rules": aggregate_subset,
        "aggregate_cross_team_rules": [aggregate_corner],
        "aggregate_status_counts": dict(sorted(statuses.items())),
        "season_subset_rules": season_subset_results,
        "season_cross_team_rules": season_corner_results,
        "interpretation": (
            "This audit supplies empirical review evidence for V2 team-match candidates. "
            "Subset/equality consistency can falsify proposed interpretations but cannot alone prove semantics or approve promotion."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit empirical evidence for V2 team-match promotion candidates.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    result = build_audit()
    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps({
        "seasons": result["seasons"],
        "total_team_match_rows": result["total_team_match_rows"],
        "aggregate_status_counts": result["aggregate_status_counts"],
        "aggregate_subset_rules": result["aggregate_subset_rules"],
        "aggregate_cross_team_rules": result["aggregate_cross_team_rules"],
        "field_profiles": result["profile_fields"],
        "json_output": str(output),
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
