from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

SEASONS = tuple(f"{year}-{str(year + 1)[-2:]}" for year in range(2016, 2026))

# Direct team-match fields that matter to the first Team/Player/League analytical families.
DIRECT_FIELDS = (
    "possessionPercentage",
    "totalScoringAtt",
    "ontargetScoringAtt",
    "shotOffTarget",
    "blockedScoringAtt",
    "cornerTaken",
    "totalPass",
    "accuratePass",
    "totalCross",
    "accurateCross",
    "totalLongBalls",
    "accurateLongBalls",
    "totalTackle",
    "wonTackle",
    "interception",
    "interceptionWon",
    "totalClearance",
    "effectiveClearance",
    "fkFoulLost",
    "fkFoulWon",
    "totalOffside",
    "totalYelCard",
    "totalRedCard",
    "saves",
    "bigChanceCreated",
    "bigChanceMissed",
    "goalAssist",
    "ballRecovery",
    "duelWon",
    "duelLost",
    "aerialWon",
    "aerialLost",
    "totalContest",
    "wonContest",
    "possLostCtrl",
    "touches",
    "touchesInOppBox",
    "expectedGoals",
    "expectedAssists",
    "expectedGoalsOnTarget",
)

# Same football concept appears at player-match grain and can be aggregated diagnostically.
PAIR_CONFIG = {
    "goalAssist": {"player": "goalAssist", "kind": "sparse_count"},
    "totalScoringAtt": {"player": "totalShots", "kind": "sparse_count"},
    "ontargetScoringAtt": {"player": "onTargetScoringAttempt", "kind": "sparse_count"},
    "shotOffTarget": {"player": "shotOffTarget", "kind": "sparse_count"},
    "blockedScoringAtt": {"player": "blockedScoringAttempt", "kind": "sparse_count"},
    "totalPass": {"player": "totalPass", "kind": "sparse_count"},
    "accuratePass": {"player": "accuratePass", "kind": "sparse_count"},
    "totalCross": {"player": "totalCross", "kind": "sparse_count"},
    "accurateCross": {"player": "accurateCross", "kind": "sparse_count"},
    "totalLongBalls": {"player": "totalLongBalls", "kind": "sparse_count"},
    "accurateLongBalls": {"player": "accurateLongBalls", "kind": "sparse_count"},
    "totalTackle": {"player": "totalTackle", "kind": "sparse_count"},
    "wonTackle": {"player": "wonTackle", "kind": "sparse_count"},
    "interceptionWon": {"player": "interceptionWon", "kind": "sparse_count"},
    "totalClearance": {"player": "totalClearance", "kind": "sparse_count"},
    "totalOffside": {"player": "totalOffside", "kind": "sparse_count"},
    "saves": {"player": "saves", "kind": "sparse_count"},
    "bigChanceCreated": {"player": "bigChanceCreated", "kind": "sparse_count"},
    "bigChanceMissed": {"player": "bigChanceMissed", "kind": "sparse_count"},
    "touches": {"player": "touches", "kind": "sparse_count"},
    "ballRecovery": {"player": "ballRecovery", "kind": "sparse_count"},
    "duelWon": {"player": "duelWon", "kind": "sparse_count"},
    "duelLost": {"player": "duelLost", "kind": "sparse_count"},
    "aerialWon": {"player": "aerialWon", "kind": "sparse_count"},
    "aerialLost": {"player": "aerialLost", "kind": "sparse_count"},
    "totalContest": {"player": "totalContest", "kind": "sparse_count"},
    "wonContest": {"player": "wonContest", "kind": "sparse_count"},
    "possLostCtrl": {"player": "possessionLostCtrl", "kind": "sparse_count"},
    "fkFoulLost": {"player": "fouls", "kind": "sparse_count"},
    "fkFoulWon": {"player": "wasFouled", "kind": "sparse_count"},
    "expectedGoals": {"player": "expectedGoals", "kind": "expected", "trigger": "totalShots"},
    "expectedAssists": {"player": "expectedAssists", "kind": "expected", "trigger": "keyPass"},
    "expectedGoalsOnTarget": {
        "player": "expectedGoalsOnTarget",
        "kind": "expected",
        "trigger": "onTargetScoringAttempt",
    },
}

EXPECTED_DIRECT_TRIGGERS = {
    "expectedGoals": "totalScoringAtt",
    "expectedAssists": "totalAttAssist",
    "expectedGoalsOnTarget": "ontargetScoringAtt",
}

# These are *candidates* for blank-means-zero normalisation, not approved production rules.
# PulseLive/Opta count surfaces are sparse for many zero-valued actions. The audit tests
# that hypothesis separately from raw non-empty coverage.
SPARSE_ZERO_COUNT_FIELDS = {
    field
    for field in DIRECT_FIELDS
    if field not in {
        "possessionPercentage",
        "expectedGoals",
        "expectedAssists",
        "expectedGoalsOnTarget",
    }
}


def num(value):
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def read(paths):
    rows, fields = [], set()
    for path in paths:
        for encoding in ("utf-8-sig", "cp1252", "latin-1"):
            try:
                with path.open("r", encoding=encoding, newline="") as handle:
                    reader = csv.DictReader(handle)
                    fields.update(reader.fieldnames or ())
                    rows.extend(dict(row) for row in reader)
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ValueError(f"Could not decode {path}")
    return rows, fields


def files(root: Path, family: str, season: str):
    name = f"{season}_{family}.csv"
    return tuple(
        club / family / name
        for club in sorted(root.iterdir())
        if club.is_dir()
        and not club.name.startswith("_")
        and (club / family / name).is_file()
    )


def source_family_inventory(root: Path, fpl_root: Path | None):
    result = {}
    for season in SEASONS:
        current = {}
        for family in ("events_stats", "players_match_stats", "players_stats", "squad"):
            paths = files(root, family, season)
            rows, fields = read(paths)
            current[family] = {
                "files": len(paths),
                "rows": len(rows),
                "fields": sorted(fields),
                "nonempty": dict(
                    Counter(
                        key
                        for row in rows
                        for key, value in row.items()
                        if value not in (None, "") and str(value).strip()
                    )
                ),
            }
        if fpl_root:
            path = fpl_root / f"{season}_all_players_gw.csv"
            rows, fields = read((path,)) if path.is_file() else ([], set())
            current["fpl_player_gw"] = {
                "files": int(path.is_file()),
                "rows": len(rows),
                "fields": sorted(fields),
                "nonempty": dict(
                    Counter(
                        key
                        for row in rows
                        for key, value in row.items()
                        if value not in (None, "") and str(value).strip()
                    )
                ),
            }
        result[season] = current
    return result


def direct_index(root: Path, season: str):
    rows, fields = read(files(root, "events_stats", season))
    matches = defaultdict(dict)
    for row in rows:
        match_id = str(row.get("matchId", "")).strip()
        venue = str(row.get("venue", "")).strip().lower()
        if match_id and venue in {"home", "away"}:
            matches[match_id][venue] = row
    pairs = {}
    for match_id, sides in matches.items():
        if "home" in sides and "away" in sides:
            pairs[(
                str(sides["home"].get("team_id", "")).strip(),
                str(sides["away"].get("team_id", "")).strip(),
            )] = match_id
    return matches, pairs, fields


def player_index(root: Path, season: str):
    rows, fields = read(files(root, "players_match_stats", season))
    matches = defaultdict(lambda: defaultdict(list))
    venues = defaultdict(dict)
    seen = set()
    for row in rows:
        match_id = str(row.get("matchId", "")).strip()
        team_id = str(row.get("team_id", "")).strip()
        venue = str(row.get("venue", "")).strip().lower()
        player_id = str(row.get("playerId") or row.get("pl_code") or "").strip()
        if not match_id or not team_id or venue not in {"home", "away"}:
            continue
        key = (match_id, team_id, player_id, str(row.get("minutesPlayed", "")).strip())
        if key in seen:
            continue
        seen.add(key)
        matches[match_id][team_id].append(row)
        venues[match_id][venue] = team_id
    pairs = {
        (sides["home"], sides["away"]): match_id
        for match_id, sides in venues.items()
        if "home" in sides and "away" in sides
    }
    return matches, pairs, fields


def direct_raw_value(row, field):
    return num(row.get(field)) if field in row else None


def direct_candidate_value(row, field):
    """Diagnostic candidate value; does not define production missingness semantics."""
    if field not in row:
        return None
    value = num(row.get(field))
    if value is not None:
        return value
    if field in SPARSE_ZERO_COUNT_FIELDS:
        return 0.0
    trigger = EXPECTED_DIRECT_TRIGGERS.get(field)
    if trigger and trigger in row:
        trigger_value = num(row.get(trigger))
        if trigger_value in (None, 0):
            return 0.0
    return None


def player_candidate_value(rows, field, config):
    if not rows or not any(field in row for row in rows):
        return None
    if config["kind"] == "sparse_count":
        return sum(num(row.get(field)) or 0.0 for row in rows)

    trigger = config["trigger"]
    total = 0.0
    for row in rows:
        if field not in row:
            return None
        value = num(row.get(field))
        trigger_value = num(row.get(trigger)) if trigger in row else None
        if value is not None:
            total += value
        elif trigger_value is not None and trigger_value > 0:
            return None
        elif trigger not in row:
            return None
    return total


def fixture_coverage(matches, field, value_fn):
    team_sides = fixtures = 0
    for match in matches.values():
        count = sum(
            1
            for side in ("home", "away")
            if side in match and value_fn(match[side], field) is not None
        )
        team_sides += count
        fixtures += count == 2
    return team_sides, fixtures


def season_audit(root: Path, season: str):
    direct, direct_pairs, direct_fields = direct_index(root, season)
    player, player_pairs, player_fields = player_index(root, season)

    coverage = {}
    for field in DIRECT_FIELDS:
        raw_sides, raw_fixtures = fixture_coverage(direct, field, direct_raw_value)
        candidate_sides, candidate_fixtures = fixture_coverage(direct, field, direct_candidate_value)
        coverage[field] = {
            "in_schema": field in direct_fields,
            "source_team_sides": sum(side in match for match in direct.values() for side in ("home", "away")),
            "raw_nonempty_team_sides": raw_sides,
            "raw_nonempty_fixtures_both_sides": raw_fixtures,
            "candidate_zero_normalised_team_sides": candidate_sides,
            "candidate_zero_normalised_fixtures_both_sides": candidate_fixtures,
            "blank_semantics": (
                "STRUCTURAL_ZERO_CANDIDATE"
                if field in SPARSE_ZERO_COUNT_FIELDS and candidate_sides > raw_sides
                else "EXPECTED_METRIC_CONDITIONAL_ZERO"
                if field in EXPECTED_DIRECT_TRIGGERS and candidate_sides > raw_sides
                else "RAW_NONEMPTY_ONLY"
            ),
        }

    comparisons = {}
    for direct_field, config in PAIR_CONFIG.items():
        player_field = config["player"]
        direct_raw_sides = direct_raw_fixtures = 0
        direct_candidate_sides = direct_candidate_fixtures = 0
        player_candidate_sides = player_candidate_fixtures = 0
        overlap = exact = within = 0
        abs_sum = max_abs = 0.0

        for match in direct.values():
            raw_count = candidate_count = 0
            for side in ("home", "away"):
                if side not in match:
                    continue
                raw_count += direct_raw_value(match[side], direct_field) is not None
                candidate_count += direct_candidate_value(match[side], direct_field) is not None
            direct_raw_sides += raw_count
            direct_raw_fixtures += raw_count == 2
            direct_candidate_sides += candidate_count
            direct_candidate_fixtures += candidate_count == 2

        for teams in player.values():
            count = sum(
                player_candidate_value(rows, player_field, config) is not None
                for rows in teams.values()
            )
            player_candidate_sides += count
            player_candidate_fixtures += count == 2

        for pair, direct_match_id in direct_pairs.items():
            player_match_id = player_pairs.get(pair)
            if not player_match_id:
                continue
            for side in ("home", "away"):
                direct_row = direct[direct_match_id].get(side)
                if not direct_row:
                    continue
                team_id = str(direct_row.get("team_id", "")).strip()
                direct_value = direct_candidate_value(direct_row, direct_field)
                player_value = player_candidate_value(
                    player[player_match_id].get(team_id, []),
                    player_field,
                    config,
                )
                if direct_value is None or player_value is None:
                    continue
                difference = abs(direct_value - player_value)
                overlap += 1
                abs_sum += difference
                max_abs = max(max_abs, difference)
                exact += difference <= 1e-9
                within += difference <= 0.01

        comparisons[direct_field] = {
            "player_field": player_field,
            "kind": config["kind"],
            "direct_in_schema": direct_field in direct_fields,
            "player_in_schema": player_field in player_fields,
            "direct_raw_nonempty_team_sides": direct_raw_sides,
            "direct_raw_nonempty_fixtures": direct_raw_fixtures,
            "direct_candidate_team_sides": direct_candidate_sides,
            "direct_candidate_fixtures": direct_candidate_fixtures,
            "player_candidate_team_sides": player_candidate_sides,
            "player_candidate_fixtures": player_candidate_fixtures,
            "overlap_team_sides": overlap,
            "exact_matches": exact,
            "within_0_01": within,
            "exact_rate": exact / overlap if overlap else None,
            "within_0_01_rate": within / overlap if overlap else None,
            "mean_abs_diff": abs_sum / overlap if overlap else None,
            "max_abs_diff": max_abs,
        }

    return {
        "direct_matches": len(direct),
        "player_matches": len(player),
        "direct_pairs": len(direct_pairs),
        "player_pairs": len(player_pairs),
        "direct_coverage": coverage,
        "direct_vs_player": comparisons,
    }


def expected_route_decision(field, seasons):
    by_season = {}
    for season in SEASONS:
        item = seasons[season]["direct_vs_player"][field]
        direct_count = item["direct_candidate_fixtures"]
        player_count = item["player_candidate_fixtures"]
        if direct_count == 0 and player_count == 0:
            decision = "COVERAGE_GAP"
        elif player_count > direct_count:
            decision = "PLAYER_DERIVED_COVERAGE_ADVANTAGE"
        elif direct_count > player_count:
            decision = "DIRECT_COVERAGE_ADVANTAGE"
        else:
            decision = "EQUAL_COVERAGE_PREFER_DIRECT_SOURCE"
        by_season[season] = {
            "direct_fixtures": direct_count,
            "player_derived_fixtures": player_count,
            "decision": decision,
        }
    return {
        "classification": "MULTIPLE_SOURCE_REPRESENTATIONS",
        "recommendation": "SEASON_SPECIFIC_SELECTION_WITH_DISTINCT_PROVENANCE",
        "by_season": by_season,
    }


def ordinary_route_decision(field, seasons):
    rows = [seasons[season]["direct_vs_player"][field] for season in SEASONS]
    overlaps = [row for row in rows if row["overlap_team_sides"]]
    total_overlap = sum(row["overlap_team_sides"] for row in overlaps)
    total_exact = sum(row["exact_matches"] for row in overlaps)
    exact_rate = total_exact / total_overlap if total_overlap else None
    sparse_zero = any(
        seasons[season]["direct_coverage"][field]["blank_semantics"] == "STRUCTURAL_ZERO_CANDIDATE"
        for season in SEASONS
    )
    return {
        "classification": "KEEP_CURRENT_ROUTE",
        "recommendation": "DIRECT_TEAM_MATCH",
        "player_derived_role": (
            "CORROBORATION_ONLY_EQUIVALENCE_NOT_PERFECT"
            if exact_rate is not None and exact_rate < 0.999999
            else "CORROBORATION_ONLY"
        ),
        "candidate_blank_semantics": (
            "STRUCTURAL_ZERO_REVIEW_REQUIRED" if sparse_zero else "NO_SPECIAL_ZERO_REVIEW_TRIGGERED"
        ),
        "candidate_normalised_exact_rate": exact_rate,
    }


def route_decisions(seasons):
    decisions = {}
    for field, config in PAIR_CONFIG.items():
        decisions[field] = (
            expected_route_decision(field, seasons)
            if config["kind"] == "expected"
            else ordinary_route_decision(field, seasons)
        )
    return decisions


def markdown(report):
    lines = [
        "# FRL automated source-route coverage audit",
        "",
        "Diagnostic evidence only. This report does not promote a source or derivation into a governed metric.",
        "",
        "Raw non-empty coverage and candidate blank-as-zero coverage are deliberately reported separately.",
        "",
        "## Route decisions",
        "",
        "| Direct field | Player field | Classification | Recommendation | Missingness note |",
        "|---|---|---|---|---|",
    ]
    for field, item in report["route_decisions"].items():
        lines.append(
            f"| `{field}` | `{PAIR_CONFIG[field]['player']}` | `{item['classification']}` | "
            f"`{item['recommendation']}` | `{item.get('candidate_blank_semantics', 'EXPECTED_PERIOD_SPECIFIC')}` |"
        )

    lines += ["", "## Direct team-match raw versus candidate-normalised coverage", ""]
    lines.append("| Field | Season | Raw non-empty sides | Candidate observed sides | Raw fx | Candidate fx | Blank semantics |")
    lines.append("|---|---|---:|---:|---:|---:|---|")
    for field in DIRECT_FIELDS:
        for season in SEASONS:
            item = report["seasons"][season]["direct_coverage"][field]
            if not item["in_schema"]:
                continue
            lines.append(
                f"| `{field}` | {season} | {item['raw_nonempty_team_sides']} | "
                f"{item['candidate_zero_normalised_team_sides']} | "
                f"{item['raw_nonempty_fixtures_both_sides']} | "
                f"{item['candidate_zero_normalised_fixtures_both_sides']} | "
                f"`{item['blank_semantics']}` |"
            )

    lines += ["", "## Direct versus player-derived candidate values", ""]
    lines.append("| Field | Season | Direct candidate fx | Player candidate fx | Overlap sides | Exact | Mean abs diff | Max abs diff |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for field in PAIR_CONFIG:
        for season in SEASONS:
            item = report["seasons"][season]["direct_vs_player"][field]
            if not item["direct_in_schema"] and not item["player_in_schema"]:
                continue
            mean = "" if item["mean_abs_diff"] is None else f"{item['mean_abs_diff']:.6g}"
            lines.append(
                f"| `{field}` | {season} | {item['direct_candidate_fixtures']} | "
                f"{item['player_candidate_fixtures']} | {item['overlap_team_sides']} | "
                f"{item['exact_matches']} | {mean} | {item['max_abs_diff']:.6g} |"
            )

    lines += ["", "## Expected-metric period decisions", ""]
    lines.append("| Field | Season | Direct fx | Player-derived fx | Diagnostic advantage |")
    lines.append("|---|---|---:|---:|---|")
    for field in ("expectedGoals", "expectedAssists", "expectedGoalsOnTarget"):
        for season, item in report["route_decisions"][field]["by_season"].items():
            lines.append(
                f"| `{field}` | {season} | {item['direct_fixtures']} | "
                f"{item['player_derived_fixtures']} | `{item['decision']}` |"
            )
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Audit preserved FRL source-route coverage without live API acquisition.")
    parser.add_argument("--pl-root", type=Path, required=True)
    parser.add_argument("--fpl-root", type=Path)
    parser.add_argument("--json-out", type=Path, default=Path("source_route_coverage.json"))
    parser.add_argument("--md-out", type=Path, default=Path("source_route_coverage.md"))
    args = parser.parse_args()
    if not args.pl_root.is_dir():
        raise SystemExit(f"PL source root not found: {args.pl_root}")

    seasons = {season: season_audit(args.pl_root, season) for season in SEASONS}
    report = {
        "schema_version": "1.1.0",
        "scope": "2016-17_to_2025-26",
        "live_api_calls": False,
        "source_families": source_family_inventory(args.pl_root, args.fpl_root),
        "seasons": seasons,
        "route_decisions": route_decisions(seasons),
        "warning": (
            "Candidate blank-as-zero values are diagnostic hypotheses only. "
            "Production use requires an explicit field-level missingness contract."
        ),
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    args.md_out.write_text(markdown(report), encoding="utf-8")

    print("FRL SOURCE ROUTE COVERAGE AUDIT")
    for season in SEASONS:
        item = seasons[season]
        print(f"{season}: direct matches={item['direct_matches']} player matches={item['player_matches']}")
    print("EXPECTED-METRIC ROUTE DECISIONS")
    for field in ("expectedGoals", "expectedAssists", "expectedGoalsOnTarget"):
        print(field)
        for season, item in report["route_decisions"][field]["by_season"].items():
            print(
                f"  {season}: direct={item['direct_fixtures']} player={item['player_derived_fixtures']} "
                f"{item['decision']}"
            )
    print("SPARSE-ZERO REVIEW FIELDS")
    for field, item in report["route_decisions"].items():
        if item.get("candidate_blank_semantics") == "STRUCTURAL_ZERO_REVIEW_REQUIRED":
            print(f"  {field}: direct route retained; blank semantics require governance")
    print(f"JSON: {args.json_out}")
    print(f"Markdown: {args.md_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
