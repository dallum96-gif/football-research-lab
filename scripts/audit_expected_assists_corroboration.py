from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from audit_source_routes import SEASONS, direct_index, num, player_index


DIRECT_METRIC = "expectedAssists"
PLAYER_METRIC = "expectedAssists"
PLAYER_TRIGGER = "keyPass"


def _player_side_value(rows: list[dict], metric_in_schema: bool) -> tuple[float | None, dict]:
    if not rows or not metric_in_schema:
        return None, {
            "candidate_available": False,
            "unsafe_positive_trigger_rows": 0,
            "blank_trigger_rows": 0,
            "source_observed_rows": 0,
        }

    total = 0.0
    unsafe_positive = 0
    blank_trigger = 0
    observed = 0

    for row in rows:
        value = num(row.get(PLAYER_METRIC))
        if value is not None:
            total += value
            observed += 1
            continue

        trigger = num(row.get(PLAYER_TRIGGER))
        if trigger is not None and trigger > 0:
            unsafe_positive += 1
        elif trigger is None:
            blank_trigger += 1

    return total, {
        "candidate_available": unsafe_positive == 0,
        "unsafe_positive_trigger_rows": unsafe_positive,
        "blank_trigger_rows": blank_trigger,
        "source_observed_rows": observed,
    }


def _season_audit(root: Path, season: str) -> dict:
    direct, direct_pairs, direct_fields = direct_index(root, season)
    player, player_pairs, player_fields = player_index(root, season)

    direct_in_schema = DIRECT_METRIC in direct_fields
    player_in_schema = PLAYER_METRIC in player_fields
    trigger_in_schema = PLAYER_TRIGGER in player_fields

    counts = Counter()
    candidate_fixture_sides: dict[tuple[str, str], bool] = {}
    zero_fill_fixture_sides: dict[tuple[str, str], bool] = {}
    agreement_abs_sum = 0.0
    agreement_max_abs = 0.0
    unsafe_overlap_abs_sum = 0.0
    unsafe_overlap_max_abs = 0.0
    exceptions = []
    unsafe_examples = []

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
            player_value, state = _player_side_value(player_rows, player_in_schema)
            zero_available = player_value is not None
            candidate_available = zero_available and state["candidate_available"]
            zero_fill_fixture_sides[(player_match_id, side)] = zero_available
            candidate_fixture_sides[(player_match_id, side)] = candidate_available

            counts["player_source_observed_rows"] += state["source_observed_rows"]
            counts["player_blank_trigger_rows"] += state["blank_trigger_rows"]
            counts["player_unsafe_positive_trigger_rows"] += state["unsafe_positive_trigger_rows"]
            if state["unsafe_positive_trigger_rows"]:
                counts["player_unsafe_team_sides"] += 1

            direct_value = num(direct_row.get(DIRECT_METRIC)) if direct_in_schema else None
            if direct_value is None:
                continue

            counts["direct_observed_team_sides"] += 1
            if player_value is None:
                continue

            difference = abs(direct_value - player_value)
            counts["zero_fill_overlap_team_sides"] += 1
            agreement_abs_sum += difference
            agreement_max_abs = max(agreement_max_abs, difference)
            if difference <= 1e-9:
                counts["zero_fill_exact"] += 1
            if difference <= 0.0001:
                counts["zero_fill_within_0_0001"] += 1
            if difference <= 0.01:
                counts["zero_fill_within_0_01"] += 1
            else:
                exceptions.append(
                    {
                        "season": season,
                        "direct_match_id": direct_match_id,
                        "player_match_id": player_match_id,
                        "side": side,
                        "team_id": team_id,
                        "direct_expected_assists": direct_value,
                        "player_zero_fill_expected_assists": player_value,
                        "difference": difference,
                        "unsafe_positive_trigger_rows": state["unsafe_positive_trigger_rows"],
                    }
                )

            if state["unsafe_positive_trigger_rows"]:
                counts["unsafe_team_sides_with_direct_overlap"] += 1
                unsafe_overlap_abs_sum += difference
                unsafe_overlap_max_abs = max(unsafe_overlap_max_abs, difference)
                if difference <= 0.01:
                    counts["unsafe_overlap_within_0_01"] += 1
                if len(unsafe_examples) < 20:
                    unsafe_examples.append(
                        {
                            "season": season,
                            "direct_match_id": direct_match_id,
                            "player_match_id": player_match_id,
                            "side": side,
                            "team_id": team_id,
                            "direct_expected_assists": direct_value,
                            "player_zero_fill_expected_assists": player_value,
                            "difference": difference,
                            "unsafe_positive_trigger_rows": state["unsafe_positive_trigger_rows"],
                        }
                    )

    def fixture_count(side_map: dict[tuple[str, str], bool]) -> int:
        matches: dict[str, set[str]] = {}
        for (match_id, side), available in side_map.items():
            if available:
                matches.setdefault(match_id, set()).add(side)
        return sum(sides == {"home", "away"} for sides in matches.values())

    overlap = counts["zero_fill_overlap_team_sides"]
    unsafe_overlap = counts["unsafe_team_sides_with_direct_overlap"]

    return {
        "direct_metric_in_schema": direct_in_schema,
        "player_metric_in_schema": player_in_schema,
        "player_trigger_in_schema": trigger_in_schema,
        "aligned_team_sides": counts["aligned_team_sides"],
        "direct_observed_team_sides": counts["direct_observed_team_sides"],
        "player_zero_fill_available_team_sides": sum(zero_fill_fixture_sides.values()),
        "player_zero_fill_available_fixtures": fixture_count(zero_fill_fixture_sides),
        "player_trigger_guarded_available_team_sides": sum(candidate_fixture_sides.values()),
        "player_trigger_guarded_available_fixtures": fixture_count(candidate_fixture_sides),
        "player_source_observed_rows": counts["player_source_observed_rows"],
        "player_blank_trigger_rows": counts["player_blank_trigger_rows"],
        "player_unsafe_positive_trigger_rows": counts["player_unsafe_positive_trigger_rows"],
        "player_unsafe_team_sides": counts["player_unsafe_team_sides"],
        "zero_fill_agreement": {
            "overlap_team_sides": overlap,
            "exact": counts["zero_fill_exact"],
            "within_0_0001": counts["zero_fill_within_0_0001"],
            "within_0_01": counts["zero_fill_within_0_01"],
            "exact_rate": counts["zero_fill_exact"] / overlap if overlap else None,
            "within_0_0001_rate": counts["zero_fill_within_0_0001"] / overlap if overlap else None,
            "within_0_01_rate": counts["zero_fill_within_0_01"] / overlap if overlap else None,
            "mean_abs_diff": agreement_abs_sum / overlap if overlap else None,
            "max_abs_diff": agreement_max_abs,
        },
        "unsafe_positive_trigger_overlap": {
            "team_sides": unsafe_overlap,
            "within_0_01": counts["unsafe_overlap_within_0_01"],
            "within_0_01_rate": (
                counts["unsafe_overlap_within_0_01"] / unsafe_overlap
                if unsafe_overlap
                else None
            ),
            "mean_abs_diff": unsafe_overlap_abs_sum / unsafe_overlap if unsafe_overlap else None,
            "max_abs_diff": unsafe_overlap_max_abs,
        },
        "exceptions_over_0_01": exceptions,
        "unsafe_examples": unsafe_examples,
    }


def audit(root: Path) -> dict:
    seasons = {season: _season_audit(root, season) for season in SEASONS}

    strong_overlap = [
        seasons[season]["zero_fill_agreement"]
        for season in ("2024-25", "2025-26")
        if seasons[season]["zero_fill_agreement"]["overlap_team_sides"]
    ]
    total_overlap = sum(item["overlap_team_sides"] for item in strong_overlap)
    total_within = sum(item["within_0_01"] for item in strong_overlap)
    max_abs = max((item["max_abs_diff"] for item in strong_overlap), default=0.0)

    if total_overlap >= 500 and total_within == total_overlap and max_abs <= 0.001:
        classification = "PLAYER_XA_BLANK_ZERO_STRONGLY_SUPPORTED_BY_DIRECT_XA_OVERLAP"
    elif total_overlap and total_within / total_overlap >= 0.99:
        classification = "PLAYER_XA_BLANK_ZERO_SUPPORTED_WITH_EXCEPTIONS"
    else:
        classification = "PLAYER_XA_BLANK_ZERO_NOT_ESTABLISHED"

    return {
        "schema_version": "1.0.0",
        "scope": "2016-17_to_2025-26",
        "live_api_calls": False,
        "question": (
            "Can blank player-match expectedAssists values be treated as zero for additive "
            "team-match xA derivation, independently of totalAttAssist/keyPass trigger equivalence?"
        ),
        "classification": classification,
        "classification_basis": {
            "seasons": ["2024-25", "2025-26"],
            "overlap_team_sides": total_overlap,
            "within_0_01_team_sides": total_within,
            "max_abs_diff": max_abs,
        },
        "seasons": seasons,
        "warning": (
            "Diagnostic evidence only. This report does not change production routing or "
            "declare the direct and player-derived xA representations identical."
        ),
    }


def markdown(report: dict) -> str:
    basis = report["classification_basis"]
    lines = [
        "# FRL expected-assists corroboration audit",
        "",
        "Diagnostic evidence only. No production route is changed by this report.",
        "",
        f"**Classification:** `{report['classification']}`",
        "",
        (
            f"2024-25 + 2025-26 direct-overlap basis: {basis['overlap_team_sides']} team sides; "
            f"{basis['within_0_01_team_sides']} within 0.01; max absolute difference "
            f"{basis['max_abs_diff']:.6g}."
        ),
        "",
        "| Season | Direct observed sides | Zero-fill player fx | Trigger-guarded player fx | Unsafe player team sides | Overlap sides | Within 0.01 | Mean abs diff | Max abs diff |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for season in SEASONS:
        item = report["seasons"][season]
        agreement = item["zero_fill_agreement"]
        lines.append(
            f"| {season} | {item['direct_observed_team_sides']} | "
            f"{item['player_zero_fill_available_fixtures']} | "
            f"{item['player_trigger_guarded_available_fixtures']} | "
            f"{item['player_unsafe_team_sides']} | "
            f"{agreement['overlap_team_sides']} | {agreement['within_0_01']} | "
            f"{'' if agreement['mean_abs_diff'] is None else f'{agreement['mean_abs_diff']:.6g}'} | "
            f"{agreement['max_abs_diff']:.6g} |"
        )

    lines += ["", "## Unsafe positive-key-pass overlap", ""]
    lines.append("| Season | Unsafe overlap sides | Within 0.01 | Mean abs diff | Max abs diff |")
    lines.append("|---|---:|---:|---:|---:|")
    for season in SEASONS:
        item = report["seasons"][season]["unsafe_positive_trigger_overlap"]
        lines.append(
            f"| {season} | {item['team_sides']} | {item['within_0_01']} | "
            f"{'' if item['mean_abs_diff'] is None else f'{item['mean_abs_diff']:.6g}'} | "
            f"{item['max_abs_diff']:.6g} |"
        )

    exceptions = [
        item
        for season in SEASONS
        for item in report["seasons"][season]["exceptions_over_0_01"]
    ]
    lines += ["", "## Exceptions over 0.01", ""]
    if not exceptions:
        lines.append("None.")
    else:
        lines.append("```json")
        lines.append(json.dumps(exceptions, indent=2, sort_keys=True))
        lines.append("```")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit player-match expected-assists blank-zero semantics against direct xA."
    )
    parser.add_argument("--pl-root", type=Path, required=True)
    parser.add_argument("--json-out", type=Path, default=Path("expected_assists_corroboration.json"))
    parser.add_argument("--md-out", type=Path, default=Path("expected_assists_corroboration.md"))
    args = parser.parse_args()

    if not args.pl_root.is_dir():
        raise SystemExit(f"PL source root not found: {args.pl_root}")

    report = audit(args.pl_root)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    args.md_out.write_text(markdown(report), encoding="utf-8")

    print("FRL EXPECTED-ASSISTS CORROBORATION AUDIT")
    print(report["classification"])
    for season in SEASONS:
        item = report["seasons"][season]
        agreement = item["zero_fill_agreement"]
        print(
            f"{season}: direct_sides={item['direct_observed_team_sides']} "
            f"zero_fill_fx={item['player_zero_fill_available_fixtures']} "
            f"guarded_fx={item['player_trigger_guarded_available_fixtures']} "
            f"unsafe_sides={item['player_unsafe_team_sides']} "
            f"overlap={agreement['overlap_team_sides']} "
            f"within_0_01={agreement['within_0_01']}"
        )
    print(f"JSON: {args.json_out}")
    print(f"Markdown: {args.md_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
