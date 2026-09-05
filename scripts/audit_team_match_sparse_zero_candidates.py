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
from source_family_adapters import (
    player_match_source_rows_for_season,
    team_match_source_rows_for_season,
)

DEFAULT_OUTPUT = (
    ROOT
    / "data"
    / "audits"
    / "team_match_sparse_zero_candidates"
    / "team_match_sparse_zero_candidate_audit.json"
)

CANDIDATE_FIELDS: tuple[str, ...] = (
    "blockedPass",
    "touchesInOppBox",
    "goalKicks",
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
    return str(row.get("team_id") or row.get("teamId") or "").strip()


def _season(row: Mapping[str, object], fallback: str = "") -> str:
    return str(row.get("frl_season") or row.get("season") or fallback).strip()


def _key(row: Mapping[str, object], *, season: str = "") -> tuple[str, str, str]:
    return (_season(row, season), _fixture_id(row), _team_id(row))


def _player_field_sums(
    rows: Iterable[Mapping[str, object]],
    field: str,
    *,
    season: str,
) -> dict[tuple[str, str, str], dict[str, object]]:
    """Aggregate only explicit numeric player observations for one exact source field.

    A team key with no numeric player observations is deliberately omitted. This
    prevents a collection of player blanks from being silently converted into a
    corroborating zero.
    """
    grouped: defaultdict[tuple[str, str, str], list[float]] = defaultdict(list)
    for row in rows:
        value = _number(row.get(field))
        if value is None:
            continue
        key = _key(row, season=season)
        if not all(key):
            continue
        grouped[key].append(value)

    return {
        key: {
            "sum": sum(values),
            "numeric_player_rows": len(values),
            "negative_player_rows": sum(value < 0 for value in values),
        }
        for key, values in grouped.items()
    }


def evaluate_player_sum_corroboration(
    team_rows: Iterable[Mapping[str, object]],
    player_rows: Iterable[Mapping[str, object]],
    field: str,
    *,
    season: str,
) -> dict[str, object]:
    """Compare one team field against the exact same player-match field summed by team.

    This is corroboration evidence only. Exact equality is useful when the same
    source concept exists at both grains; it does not itself prove missingness
    semantics or justify promotion.
    """
    sums = _player_field_sums(player_rows, field, season=season)
    team_materialised = tuple(team_rows)

    observed_pairs = exact = mismatches = 0
    blank_with_player_zero = blank_with_player_positive = 0
    blank_without_player_numeric = 0
    examples: list[dict[str, object]] = []

    for row in team_materialised:
        key = _key(row, season=season)
        player = sums.get(key)
        team_value = _number(row.get(field))

        if team_value is None:
            if player is None:
                blank_without_player_numeric += 1
                continue
            player_sum = float(player["sum"])
            if abs(player_sum) <= 1e-9:
                blank_with_player_zero += 1
            elif player_sum > 0:
                blank_with_player_positive += 1
                if len(examples) < 5:
                    examples.append({
                        "season": key[0],
                        "fixture_id": key[1],
                        "team_id": key[2],
                        "team_value": None,
                        "player_sum": player_sum,
                        "case": "BLANK_TEAM_POSITIVE_PLAYER_SUM",
                    })
            continue

        if player is None:
            continue
        player_sum = float(player["sum"])
        observed_pairs += 1
        if abs(team_value - player_sum) <= 1e-9:
            exact += 1
        else:
            mismatches += 1
            if len(examples) < 5:
                examples.append({
                    "season": key[0],
                    "fixture_id": key[1],
                    "team_id": key[2],
                    "team_value": team_value,
                    "player_sum": player_sum,
                    "case": "OBSERVED_TEAM_PLAYER_SUM_MISMATCH",
                })

    player_route_keys = len(sums)
    if player_route_keys == 0:
        status = "NO_EXACT_PLAYER_MATCH_CORROBORATION_ROUTE"
    elif mismatches or blank_with_player_positive:
        status = "PLAYER_MATCH_CORROBORATION_REVIEW_CONFLICTS"
    elif observed_pairs > 0 and blank_with_player_zero > 0:
        status = "PLAYER_MATCH_SUPPORTS_STRUCTURAL_ZERO_REVIEW"
    elif observed_pairs > 0:
        status = "PLAYER_MATCH_SUPPORTS_OBSERVED_VALUES_ONLY"
    else:
        status = "PLAYER_MATCH_ROUTE_INSUFFICIENT"

    return {
        "field": field,
        "season": season,
        "status": status,
        "player_route_team_keys": player_route_keys,
        "observed_team_player_pairs": observed_pairs,
        "observed_exact_matches": exact,
        "observed_mismatches": mismatches,
        "blank_team_player_zero": blank_with_player_zero,
        "blank_team_player_positive": blank_with_player_positive,
        "blank_team_without_player_numeric": blank_without_player_numeric,
        "example_conflicts": examples,
        "governance_note": (
            "Exact player-match summation is independent corroboration only when the same source field "
            "is explicitly numeric at player grain. Player blanks are never converted to zero here."
        ),
    }


def evaluate_lost_corners_opponent_route(
    rows: Iterable[Mapping[str, object]],
    *,
    season: str,
) -> dict[str, object]:
    """Test lostCorners against the opponent's cornerTaken using season+fixture identity."""
    by_fixture: defaultdict[tuple[str, str], list[Mapping[str, object]]] = defaultdict(list)
    for row in rows:
        fid = _fixture_id(row)
        if fid:
            by_fixture[(season, fid)].append(row)

    observed_pairs = exact = mismatches = 0
    blank_with_opponent_zero = blank_with_opponent_positive = 0
    blank_with_opponent_blank = 0
    examples: list[dict[str, object]] = []

    for (season_key, fid), fixture_rows in by_fixture.items():
        if len(fixture_rows) != 2:
            continue
        first, second = fixture_rows
        for subject, opponent in ((first, second), (second, first)):
            lost = _number(subject.get("lostCorners"))
            opponent_corners = _number(opponent.get("cornerTaken"))
            team_id = _team_id(subject)

            if lost is None:
                if opponent_corners is None:
                    blank_with_opponent_blank += 1
                elif abs(opponent_corners) <= 1e-9:
                    blank_with_opponent_zero += 1
                elif opponent_corners > 0:
                    blank_with_opponent_positive += 1
                    if len(examples) < 5:
                        examples.append({
                            "season": season_key,
                            "fixture_id": fid,
                            "team_id": team_id,
                            "lostCorners": None,
                            "opponent_cornerTaken": opponent_corners,
                            "case": "BLANK_LOST_CORNERS_POSITIVE_OPPONENT_CORNERS",
                        })
                continue

            if opponent_corners is None:
                continue
            observed_pairs += 1
            if abs(lost - opponent_corners) <= 1e-9:
                exact += 1
            else:
                mismatches += 1
                if len(examples) < 5:
                    examples.append({
                        "season": season_key,
                        "fixture_id": fid,
                        "team_id": team_id,
                        "lostCorners": lost,
                        "opponent_cornerTaken": opponent_corners,
                        "case": "OBSERVED_OPPONENT_CORNER_MISMATCH",
                    })

    if mismatches or blank_with_opponent_positive:
        status = "OPPONENT_ROUTE_REVIEW_CONFLICTS"
    elif observed_pairs and blank_with_opponent_zero:
        status = "OPPONENT_ROUTE_SUPPORTS_STRUCTURAL_ZERO_REVIEW"
    elif observed_pairs:
        status = "OPPONENT_ROUTE_SUPPORTS_OBSERVED_EQUIVALENCE_ONLY"
    else:
        status = "OPPONENT_ROUTE_INSUFFICIENT"

    return {
        "field": "lostCorners",
        "opponent_field": "cornerTaken",
        "season": season,
        "status": status,
        "observed_pairs": observed_pairs,
        "observed_exact_matches": exact,
        "observed_mismatches": mismatches,
        "blank_lostCorners_opponent_zero": blank_with_opponent_zero,
        "blank_lostCorners_opponent_positive": blank_with_opponent_positive,
        "blank_lostCorners_opponent_blank": blank_with_opponent_blank,
        "example_conflicts": examples,
        "governance_note": (
            "This corrects the earlier aggregate audit by preserving season in fixture identity. "
            "Opponent cornerTaken blanks remain missing and are not treated as zero."
        ),
    }


def _aggregate_player_results(
    results: Sequence[Mapping[str, object]],
    field: str,
) -> dict[str, object]:
    selected = [row for row in results if row.get("field") == field]
    totals = {
        key: sum(int(row.get(key) or 0) for row in selected)
        for key in (
            "player_route_team_keys",
            "observed_team_player_pairs",
            "observed_exact_matches",
            "observed_mismatches",
            "blank_team_player_zero",
            "blank_team_player_positive",
            "blank_team_without_player_numeric",
        )
    }
    seasons_with_route = sum(int(row.get("player_route_team_keys") or 0) > 0 for row in selected)

    if totals["player_route_team_keys"] == 0:
        status = "NO_EXACT_PLAYER_MATCH_CORROBORATION_ROUTE"
    elif totals["observed_mismatches"] or totals["blank_team_player_positive"]:
        status = "PLAYER_MATCH_CORROBORATION_REVIEW_CONFLICTS"
    elif totals["observed_team_player_pairs"] and totals["blank_team_player_zero"]:
        status = "PLAYER_MATCH_SUPPORTS_STRUCTURAL_ZERO_REVIEW"
    elif totals["observed_team_player_pairs"]:
        status = "PLAYER_MATCH_SUPPORTS_OBSERVED_VALUES_ONLY"
    else:
        status = "PLAYER_MATCH_ROUTE_INSUFFICIENT"

    return {
        "field": field,
        "seasons_with_player_route": seasons_with_route,
        "status": status,
        **totals,
    }


def _aggregate_opponent_results(results: Sequence[Mapping[str, object]]) -> dict[str, object]:
    keys = (
        "observed_pairs",
        "observed_exact_matches",
        "observed_mismatches",
        "blank_lostCorners_opponent_zero",
        "blank_lostCorners_opponent_positive",
        "blank_lostCorners_opponent_blank",
    )
    totals = {key: sum(int(row.get(key) or 0) for row in results) for key in keys}
    if totals["observed_mismatches"] or totals["blank_lostCorners_opponent_positive"]:
        status = "OPPONENT_ROUTE_REVIEW_CONFLICTS"
    elif totals["observed_pairs"] and totals["blank_lostCorners_opponent_zero"]:
        status = "OPPONENT_ROUTE_SUPPORTS_STRUCTURAL_ZERO_REVIEW"
    elif totals["observed_pairs"]:
        status = "OPPONENT_ROUTE_SUPPORTS_OBSERVED_EQUIVALENCE_ONLY"
    else:
        status = "OPPONENT_ROUTE_INSUFFICIENT"
    return {"field": "lostCorners", "status": status, **totals}


def build_audit(seasons: Sequence[str] = SEASONS) -> dict[str, object]:
    player_results: list[dict[str, object]] = []
    opponent_results: list[dict[str, object]] = []
    team_row_counts: dict[str, int] = {}
    player_row_counts: dict[str, int] = {}

    for season in seasons:
        team_rows = tuple(team_match_source_rows_for_season(season))
        player_rows = tuple(player_match_source_rows_for_season(season))
        team_row_counts[season] = len(team_rows)
        player_row_counts[season] = len(player_rows)

        for field in CANDIDATE_FIELDS:
            player_results.append(
                evaluate_player_sum_corroboration(
                    team_rows,
                    player_rows,
                    field,
                    season=season,
                )
            )
        opponent_results.append(
            evaluate_lost_corners_opponent_route(team_rows, season=season)
        )

    player_summary = {
        field: _aggregate_player_results(player_results, field)
        for field in CANDIDATE_FIELDS
    }
    opponent_summary = _aggregate_opponent_results(opponent_results)

    status_counts = Counter(row["status"] for row in player_summary.values())
    status_counts[opponent_summary["status"]] += 1

    return {
        "schema_version": "1.0.0",
        "scope": "SPARSE_ZERO_CORROBORATION_FOR_V2_HELD_TEAM_MATCH_FIELDS",
        "seasons": list(seasons),
        "team_match_row_counts": team_row_counts,
        "player_match_row_counts": player_row_counts,
        "candidate_fields": list(CANDIDATE_FIELDS),
        "player_sum_summary": player_summary,
        "lost_corners_opponent_summary": opponent_summary,
        "status_counts": dict(sorted(status_counts.items())),
        "season_player_sum_results": player_results,
        "season_lost_corners_opponent_results": opponent_results,
        "interpretation": (
            "This audit seeks independent evidence for blank-versus-zero semantics. A structural-zero "
            "promotion requires more than sparse presence: the corroborating route should agree with "
            "observed team values and resolve blank team observations to zero without positive conflicts. "
            "No result here automatically changes the governed missingness contract."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit independent sparse-zero corroboration for held team-match fields."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    result = build_audit()
    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    print(
        json.dumps(
            {
                "candidate_fields": result["candidate_fields"],
                "status_counts": result["status_counts"],
                "player_sum_summary": result["player_sum_summary"],
                "lost_corners_opponent_summary": result["lost_corners_opponent_summary"],
                "json_output": str(output),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
