from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from audit_source_routes import (
    SEASONS,
    direct_index,
    num,
    player_index,
)


EXPECTED_CONFIG = {
    "expectedGoals": {
        "direct_trigger": "totalScoringAtt",
        "player_metric": "expectedGoals",
        "player_trigger": "totalShots",
    },
    "expectedAssists": {
        "direct_trigger": "totalAttAssist",
        "player_metric": "expectedAssists",
        "player_trigger": "keyPass",
    },
    "expectedGoalsOnTarget": {
        "direct_trigger": "ontargetScoringAtt",
        "player_metric": "expectedGoalsOnTarget",
        "player_trigger": "onTargetScoringAttempt",
    },
}


def _fixture_count(side_status: dict[tuple[str, str], bool]) -> int:
    by_match: dict[str, set[str]] = {}
    for (match_id, side), available in side_status.items():
        if not available:
            continue
        by_match.setdefault(match_id, set()).add(side)
    return sum(sides == {"home", "away"} for sides in by_match.values())


def _trigger_evidence(
    direct,
    direct_pairs,
    player,
    player_pairs,
    direct_trigger: str,
    player_trigger: str,
    direct_trigger_in_schema: bool,
    player_trigger_in_schema: bool,
) -> dict:
    counts = Counter()
    absolute_difference = 0.0
    maximum_difference = 0.0

    if not direct_trigger_in_schema or not player_trigger_in_schema:
        return {
            "classification": "TRIGGER_ROUTE_UNAVAILABLE",
            "aligned_team_sides": 0,
            "direct_observed_team_sides": 0,
            "direct_blank_team_sides": 0,
            "direct_blank_player_zero": 0,
            "direct_blank_player_positive": 0,
            "observed_overlap_team_sides": 0,
            "observed_exact_team_sides": 0,
            "observed_exact_rate": None,
            "observed_mean_abs_diff": None,
            "observed_max_abs_diff": None,
        }

    for pair, direct_match_id in direct_pairs.items():
        player_match_id = player_pairs.get(pair)
        if not player_match_id:
            continue

        for side in ("home", "away"):
            direct_row = direct[direct_match_id].get(side)
            if direct_row is None:
                continue
            team_id = str(direct_row.get("team_id", "")).strip()
            player_rows = player[player_match_id].get(team_id, [])
            if not player_rows:
                continue

            counts["aligned_team_sides"] += 1
            direct_value = num(direct_row.get(direct_trigger))
            player_value = sum(num(row.get(player_trigger)) or 0.0 for row in player_rows)

            if direct_value is None:
                counts["direct_blank_team_sides"] += 1
                if player_value == 0:
                    counts["direct_blank_player_zero"] += 1
                else:
                    counts["direct_blank_player_positive"] += 1
                continue

            counts["direct_observed_team_sides"] += 1
            difference = abs(direct_value - player_value)
            counts["observed_overlap_team_sides"] += 1
            absolute_difference += difference
            maximum_difference = max(maximum_difference, difference)
            if difference <= 1e-9:
                counts["observed_exact_team_sides"] += 1

    overlap = counts["observed_overlap_team_sides"]
    exact_rate = (
        counts["observed_exact_team_sides"] / overlap
        if overlap
        else None
    )
    blank_positive = counts["direct_blank_player_positive"]
    blank_count = counts["direct_blank_team_sides"]

    if (
        overlap
        and exact_rate is not None
        and exact_rate >= 0.99
        and blank_positive == 0
    ):
        classification = "SPARSE_ZERO_STRONGLY_SUPPORTED"
    elif overlap and exact_rate is not None and exact_rate >= 0.95 and blank_positive == 0:
        classification = "SPARSE_ZERO_SUPPORTED_WITH_SOURCE_ANOMALIES"
    elif blank_count and blank_positive:
        classification = "BLANK_ZERO_CONTRADICTED"
    else:
        classification = "INSUFFICIENT_TRIGGER_EVIDENCE"

    return {
        "classification": classification,
        "aligned_team_sides": counts["aligned_team_sides"],
        "direct_observed_team_sides": counts["direct_observed_team_sides"],
        "direct_blank_team_sides": blank_count,
        "direct_blank_player_zero": counts["direct_blank_player_zero"],
        "direct_blank_player_positive": blank_positive,
        "observed_overlap_team_sides": overlap,
        "observed_exact_team_sides": counts["observed_exact_team_sides"],
        "observed_exact_rate": exact_rate,
        "observed_mean_abs_diff": absolute_difference / overlap if overlap else None,
        "observed_max_abs_diff": maximum_difference,
    }


def _direct_expected_value(
    row: dict,
    metric: str,
    trigger: str,
    metric_in_schema: bool,
    trigger_zero_supported: bool,
) -> tuple[float | None, str]:
    if not metric_in_schema:
        return None, "METRIC_NOT_IN_SCHEMA"

    value = num(row.get(metric))
    if value is not None:
        return value, "SOURCE_OBSERVED"

    trigger_value = num(row.get(trigger))
    if trigger_value is not None and trigger_value > 0:
        return None, "MISSING_WITH_POSITIVE_TRIGGER"
    if trigger_value == 0:
        return 0.0, "CONDITIONAL_ZERO_EXPLICIT_TRIGGER"
    if trigger_value is None and trigger_zero_supported:
        return 0.0, "CONDITIONAL_ZERO_GOVERNED_TRIGGER"
    return None, "MISSING_TRIGGER_UNRESOLVED"


def _player_expected_value(
    rows: list[dict],
    metric: str,
    trigger: str,
    metric_in_schema: bool,
    trigger_in_schema: bool,
    trigger_zero_supported: bool,
) -> tuple[float | None, str, Counter]:
    states = Counter()
    if not rows or not metric_in_schema or not trigger_in_schema:
        return None, "ROUTE_UNAVAILABLE", states

    total = 0.0
    for row in rows:
        value = num(row.get(metric))
        if value is not None:
            total += value
            states["SOURCE_OBSERVED_PLAYER_ROWS"] += 1
            continue

        trigger_value = num(row.get(trigger))
        if trigger_value is not None and trigger_value > 0:
            states["MISSING_WITH_POSITIVE_TRIGGER_PLAYER_ROWS"] += 1
            return None, "UNSAFE_POSITIVE_TRIGGER_GAP", states
        if trigger_value == 0:
            states["CONDITIONAL_ZERO_EXPLICIT_TRIGGER_PLAYER_ROWS"] += 1
            continue
        if trigger_value is None and trigger_zero_supported:
            states["CONDITIONAL_ZERO_GOVERNED_TRIGGER_PLAYER_ROWS"] += 1
            continue

        states["MISSING_TRIGGER_UNRESOLVED_PLAYER_ROWS"] += 1
        return None, "UNRESOLVED_TRIGGER_GAP", states

    return total, "DERIVED", states


def _season_metric_audit(root: Path, season: str, metric: str, config: dict) -> dict:
    direct, direct_pairs, direct_fields = direct_index(root, season)
    player, player_pairs, player_fields = player_index(root, season)

    direct_trigger = config["direct_trigger"]
    player_metric = config["player_metric"]
    player_trigger = config["player_trigger"]

    trigger_evidence = _trigger_evidence(
        direct,
        direct_pairs,
        player,
        player_pairs,
        direct_trigger,
        player_trigger,
        direct_trigger in direct_fields,
        player_trigger in player_fields,
    )
    trigger_zero_supported = trigger_evidence["classification"] in {
        "SPARSE_ZERO_STRONGLY_SUPPORTED",
        "SPARSE_ZERO_SUPPORTED_WITH_SOURCE_ANOMALIES",
    }

    direct_status: dict[tuple[str, str], bool] = {}
    direct_states = Counter()
    direct_values: dict[tuple[str, str], float] = {}
    for match_id, sides in direct.items():
        for side in ("home", "away"):
            row = sides.get(side)
            if row is None:
                continue
            value, state = _direct_expected_value(
                row,
                metric,
                direct_trigger,
                metric in direct_fields,
                trigger_zero_supported,
            )
            direct_states[state] += 1
            available = value is not None
            direct_status[(match_id, side)] = available
            if available:
                direct_values[(match_id, side)] = value

    player_status: dict[tuple[str, str], bool] = {}
    player_states = Counter()
    player_values_by_match_team: dict[tuple[str, str], float] = {}
    player_row_states = Counter()
    for match_id, teams in player.items():
        venue_to_team = {}
        for side in ("home", "away"):
            for team_id, rows in teams.items():
                if any(str(row.get("venue", "")).strip().lower() == side for row in rows):
                    venue_to_team[side] = team_id
                    break
        for side, team_id in venue_to_team.items():
            value, state, row_states = _player_expected_value(
                teams.get(team_id, []),
                player_metric,
                player_trigger,
                player_metric in player_fields,
                player_trigger in player_fields,
                trigger_zero_supported,
            )
            player_states[state] += 1
            player_row_states.update(row_states)
            available = value is not None
            player_status[(match_id, side)] = available
            if available:
                player_values_by_match_team[(match_id, team_id)] = value

    overlap = exact = within_0_01 = 0
    abs_sum = max_abs = 0.0
    for pair, direct_match_id in direct_pairs.items():
        player_match_id = player_pairs.get(pair)
        if not player_match_id:
            continue
        for side in ("home", "away"):
            direct_row = direct[direct_match_id].get(side)
            if direct_row is None:
                continue
            direct_value = direct_values.get((direct_match_id, side))
            team_id = str(direct_row.get("team_id", "")).strip()
            player_value = player_values_by_match_team.get((player_match_id, team_id))
            if direct_value is None or player_value is None:
                continue
            difference = abs(direct_value - player_value)
            overlap += 1
            abs_sum += difference
            max_abs = max(max_abs, difference)
            exact += difference <= 1e-9
            within_0_01 += difference <= 0.01

    direct_sides = sum(direct_status.values())
    player_sides = sum(player_status.values())
    direct_fixtures = _fixture_count(direct_status)
    player_fixtures = _fixture_count(player_status)

    return {
        "metric": metric,
        "direct_trigger": direct_trigger,
        "player_metric": player_metric,
        "player_trigger": player_trigger,
        "trigger_evidence": trigger_evidence,
        "trigger_zero_supported_for_diagnostic_derivation": trigger_zero_supported,
        "direct": {
            "metric_in_schema": metric in direct_fields,
            "trigger_in_schema": direct_trigger in direct_fields,
            "available_team_sides": direct_sides,
            "available_fixtures": direct_fixtures,
            "states": dict(direct_states),
        },
        "player_derived": {
            "metric_in_schema": player_metric in player_fields,
            "trigger_in_schema": player_trigger in player_fields,
            "available_team_sides": player_sides,
            "available_fixtures": player_fixtures,
            "team_states": dict(player_states),
            "player_row_states": dict(player_row_states),
        },
        "agreement": {
            "overlap_team_sides": overlap,
            "exact_team_sides": exact,
            "within_0_01_team_sides": within_0_01,
            "exact_rate": exact / overlap if overlap else None,
            "within_0_01_rate": within_0_01 / overlap if overlap else None,
            "mean_abs_diff": abs_sum / overlap if overlap else None,
            "max_abs_diff": max_abs,
        },
    }


def audit(root: Path) -> dict:
    seasons = {}
    for season in SEASONS:
        seasons[season] = {
            metric: _season_metric_audit(root, season, metric, config)
            for metric, config in EXPECTED_CONFIG.items()
        }
    return {
        "schema_version": "1.0.0",
        "scope": "2016-17_to_2025-26",
        "live_api_calls": False,
        "purpose": (
            "Validate trigger missingness and strict player-derived team expected-metric "
            "coverage before any governed source-route promotion."
        ),
        "seasons": seasons,
        "warning": (
            "Diagnostic evidence only. Trigger classifications and derived coverage do not "
            "promote a production route or declare cross-representation comparability."
        ),
    }


def markdown(report: dict) -> str:
    lines = [
        "# FRL expected-metric route governance audit",
        "",
        "Diagnostic evidence only. No production source route is changed by this report.",
        "",
        "## Trigger evidence",
        "",
        "| Metric | Season | Trigger pair | Classification | Direct blanks | Blank→player zero | Blank→player positive | Observed exact rate |",
        "|---|---|---|---|---:|---:|---:|---:|",
    ]
    for season in SEASONS:
        for metric, item in report["seasons"][season].items():
            trigger = item["trigger_evidence"]
            exact_rate = trigger["observed_exact_rate"]
            exact_text = "" if exact_rate is None else f"{exact_rate:.4f}"
            lines.append(
                f"| `{metric}` | {season} | `{item['direct_trigger']}` ↔ `{item['player_trigger']}` | "
                f"`{trigger['classification']}` | {trigger['direct_blank_team_sides']} | "
                f"{trigger['direct_blank_player_zero']} | {trigger['direct_blank_player_positive']} | {exact_text} |"
            )

    lines += [
        "",
        "## Governed-candidate route coverage",
        "",
        "Coverage below uses the trigger classification only as a diagnostic candidate. It is not production governance.",
        "",
        "| Metric | Season | Direct fx | Player-derived fx | Direct states | Player team states |",
        "|---|---|---:|---:|---|---|",
    ]
    for season in SEASONS:
        for metric, item in report["seasons"][season].items():
            lines.append(
                f"| `{metric}` | {season} | {item['direct']['available_fixtures']} | "
                f"{item['player_derived']['available_fixtures']} | "
                f"`{json.dumps(item['direct']['states'], sort_keys=True)}` | "
                f"`{json.dumps(item['player_derived']['team_states'], sort_keys=True)}` |"
            )

    lines += [
        "",
        "## Direct versus player-derived representation agreement",
        "",
        "| Metric | Season | Overlap sides | Exact rate | Within 0.01 | Mean abs diff | Max abs diff |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for season in SEASONS:
        for metric, item in report["seasons"][season].items():
            agreement = item["agreement"]
            exact = agreement["exact_rate"]
            within = agreement["within_0_01_rate"]
            mean = agreement["mean_abs_diff"]
            lines.append(
                f"| `{metric}` | {season} | {agreement['overlap_team_sides']} | "
                f"{'' if exact is None else f'{exact:.4f}'} | "
                f"{'' if within is None else f'{within:.4f}'} | "
                f"{'' if mean is None else f'{mean:.6g}'} | {agreement['max_abs_diff']:.6g} |"
            )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit expected-metric trigger semantics and candidate source routes."
    )
    parser.add_argument("--pl-root", type=Path, required=True)
    parser.add_argument("--json-out", type=Path, default=Path("expected_metric_routes.json"))
    parser.add_argument("--md-out", type=Path, default=Path("expected_metric_routes.md"))
    args = parser.parse_args()

    if not args.pl_root.is_dir():
        raise SystemExit(f"PL source root not found: {args.pl_root}")

    report = audit(args.pl_root)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    args.md_out.write_text(markdown(report), encoding="utf-8")

    print("FRL EXPECTED-METRIC ROUTE GOVERNANCE AUDIT")
    for metric in EXPECTED_CONFIG:
        print(metric)
        for season in SEASONS:
            item = report["seasons"][season][metric]
            print(
                f"  {season}: trigger={item['trigger_evidence']['classification']} "
                f"direct_fx={item['direct']['available_fixtures']} "
                f"player_fx={item['player_derived']['available_fixtures']} "
                f"overlap={item['agreement']['overlap_team_sides']}"
            )
    print(f"JSON: {args.json_out}")
    print(f"Markdown: {args.md_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
