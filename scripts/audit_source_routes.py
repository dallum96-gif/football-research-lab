from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

SEASONS = tuple(f"{y}-{str(y + 1)[-2:]}" for y in range(2016, 2026))

PAIRS = {
    "goalsFor": "goals",
    "goalAssist": "goalAssist",
    "totalScoringAtt": "totalShots",
    "ontargetScoringAtt": "onTargetScoringAttempt",
    "shotOffTarget": "shotOffTarget",
    "blockedScoringAtt": "blockedScoringAttempt",
    "totalPass": "totalPass",
    "accuratePass": "accuratePass",
    "totalCross": "totalCross",
    "accurateCross": "accurateCross",
    "totalLongBalls": "totalLongBalls",
    "accurateLongBalls": "accurateLongBalls",
    "totalTackle": "totalTackle",
    "wonTackle": "wonTackle",
    "interceptionWon": "interceptionWon",
    "totalClearance": "totalClearance",
    "totalOffside": "totalOffside",
    "saves": "saves",
    "bigChanceCreated": "bigChanceCreated",
    "bigChanceMissed": "bigChanceMissed",
    "touches": "touches",
    "ballRecovery": "ballRecovery",
    "duelWon": "duelWon",
    "duelLost": "duelLost",
    "aerialWon": "aerialWon",
    "aerialLost": "aerialLost",
    "totalContest": "totalContest",
    "wonContest": "wonContest",
    "possLostCtrl": "possessionLostCtrl",
    "fkFoulLost": "fouls",
    "fkFoulWon": "wasFouled",
    "expectedGoals": "expectedGoals",
    "expectedAssists": "expectedAssists",
    "expectedGoalsOnTarget": "expectedGoalsOnTarget",
}

DIRECT_FIELDS = (
    "possessionPercentage", "totalScoringAtt", "ontargetScoringAtt",
    "shotOffTarget", "blockedScoringAtt", "totalPass", "accuratePass",
    "totalCross", "accurateCross", "totalLongBalls", "accurateLongBalls",
    "totalTackle", "wonTackle", "interception", "interceptionWon",
    "totalClearance", "effectiveClearance", "fkFoulLost", "fkFoulWon",
    "totalOffside", "totalYelCard", "totalRedCard", "saves",
    "bigChanceCreated", "bigChanceMissed", "expectedGoals",
    "expectedAssists", "expectedGoalsOnTarget", "ballRecovery", "duelWon",
    "duelLost", "aerialWon", "aerialLost", "totalContest", "wonContest",
    "touches", "touchesInOppBox",
)


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
        for enc in ("utf-8-sig", "cp1252", "latin-1"):
            try:
                with path.open("r", encoding=enc, newline="") as fh:
                    reader = csv.DictReader(fh)
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
                "nonempty": dict(Counter(
                    key for row in rows for key, value in row.items()
                    if value not in (None, "") and str(value).strip()
                )),
            }
        if fpl_root:
            path = fpl_root / f"{season}_all_players_gw.csv"
            rows, fields = read((path,)) if path.is_file() else ([], set())
            current["fpl_player_gw"] = {
                "files": int(path.is_file()),
                "rows": len(rows),
                "fields": sorted(fields),
                "nonempty": dict(Counter(
                    key for row in rows for key, value in row.items()
                    if value not in (None, "") and str(value).strip()
                )),
            }
        result[season] = current
    return result


def direct_index(root: Path, season: str):
    rows, fields = read(files(root, "events_stats", season))
    matches = defaultdict(dict)
    for row in rows:
        mid = str(row.get("matchId", "")).strip()
        venue = str(row.get("venue", "")).strip().lower()
        if mid and venue in {"home", "away"}:
            matches[mid][venue] = row
    pairs = {}
    for mid, sides in matches.items():
        if "home" in sides and "away" in sides:
            pairs[(
                str(sides["home"].get("team_id", "")).strip(),
                str(sides["away"].get("team_id", "")).strip(),
            )] = mid
    return matches, pairs, fields


def player_index(root: Path, season: str):
    rows, fields = read(files(root, "players_match_stats", season))
    matches = defaultdict(lambda: defaultdict(list))
    venues = defaultdict(dict)
    seen = set()
    for row in rows:
        mid = str(row.get("matchId", "")).strip()
        tid = str(row.get("team_id", "")).strip()
        venue = str(row.get("venue", "")).strip().lower()
        pid = str(row.get("playerId") or row.get("pl_code") or "").strip()
        if not mid or not tid or venue not in {"home", "away"}:
            continue
        key = (mid, tid, pid, str(row.get("minutesPlayed", "")).strip())
        if key in seen:
            continue
        seen.add(key)
        matches[mid][tid].append(row)
        venues[mid][venue] = tid
    pairs = {
        (sides["home"], sides["away"]): mid
        for mid, sides in venues.items()
        if "home" in sides and "away" in sides
    }
    return matches, pairs, fields


def additive(rows, field):
    observed = [value for row in rows if (value := num(row.get(field))) is not None]
    return sum(observed) if observed else None


def expected(rows, field):
    trigger = {
        "expectedGoals": "totalShots",
        "expectedGoalsOnTarget": "onTargetScoringAttempt",
        "expectedAssists": "keyPass",
    }[field]
    total, observed = 0.0, False
    for row in rows:
        value, trigger_value = num(row.get(field)), num(row.get(trigger))
        if value is not None:
            total += value
            observed = True
        elif trigger_value is not None and trigger_value > 0:
            return None
    return total if observed or rows else None


def derive(rows, field):
    return expected(rows, field) if field.startswith("expected") else additive(rows, field)


def season_audit(root: Path, season: str):
    direct, direct_pairs, direct_fields = direct_index(root, season)
    player, player_pairs, player_fields = player_index(root, season)

    coverage = {}
    for field in DIRECT_FIELDS:
        sides = fixtures = 0
        for match in direct.values():
            count = sum(
                1 for side in ("home", "away")
                if side in match and num(match[side].get(field)) is not None
            )
            sides += count
            fixtures += count == 2
        coverage[field] = {
            "in_schema": field in direct_fields,
            "team_sides": sides,
            "fixtures_both_sides": fixtures,
        }

    comparisons = {}
    for dfield, pfield in PAIRS.items():
        dsides = dfixtures = psides = pfixtures = overlap = exact = within = 0
        abs_sum = max_abs = 0.0

        for match in direct.values():
            count = sum(
                1 for side in ("home", "away")
                if side in match and num(match[side].get(dfield)) is not None
            )
            dsides += count
            dfixtures += count == 2

        for teams in player.values():
            count = sum(derive(rows, pfield) is not None for rows in teams.values())
            psides += count
            pfixtures += count == 2

        for pair, dmid in direct_pairs.items():
            pmid = player_pairs.get(pair)
            if not pmid:
                continue
            for side in ("home", "away"):
                drow = direct[dmid].get(side)
                if not drow:
                    continue
                tid = str(drow.get("team_id", "")).strip()
                dv, pv = num(drow.get(dfield)), derive(player[pmid].get(tid, []), pfield)
                if dv is None or pv is None:
                    continue
                diff = abs(dv - pv)
                overlap += 1
                abs_sum += diff
                max_abs = max(max_abs, diff)
                exact += diff <= 1e-9
                within += diff <= 0.01

        comparisons[dfield] = {
            "player_field": pfield,
            "direct_in_schema": dfield in direct_fields,
            "player_in_schema": pfield in player_fields,
            "direct_team_sides": dsides,
            "direct_fixtures": dfixtures,
            "player_derived_team_sides": psides,
            "player_derived_fixtures": pfixtures,
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


def decision(field, seasons):
    rows = [seasons[s]["direct_vs_player"][field] for s in SEASONS]
    direct_full = all(row["direct_fixtures"] >= 380 for row in rows)
    improves = any(row["player_derived_fixtures"] > row["direct_fixtures"] for row in rows)
    overlaps = [row for row in rows if row["overlap_team_sides"]]
    exact = bool(overlaps) and all((row["exact_rate"] or 0) >= .999999 for row in overlaps)
    close = bool(overlaps) and all((row["within_0_01_rate"] or 0) >= .99 for row in overlaps)

    if field in {"expectedGoals", "expectedAssists", "expectedGoalsOnTarget"}:
        return {
            "classification": "MULTIPLE_SOURCE_REPRESENTATIONS",
            "recommendation": (
                "DERIVED_ROUTE_PREFERRED_FOR_COVERAGE_WHERE_GOVERNED"
                if improves else "KEEP_DISTINCT_REPRESENTATIONS"
            ),
        }
    if direct_full:
        return {"classification": "KEEP_CURRENT_ROUTE", "recommendation": "DIRECT_TEAM_MATCH"}
    if improves and exact:
        return {
            "classification": "BETTER_EXISTING_ROUTE_CANDIDATE",
            "recommendation": "PLAYER_DERIVED_CAN_FILL_GAPS_AFTER_MISSINGNESS_CONTRACT",
        }
    if improves and close:
        return {
            "classification": "MULTIPLE_SOURCE_REPRESENTATIONS",
            "recommendation": "KEEP_DISTINCT_UNTIL_EQUIVALENCE_PROVEN",
        }
    if improves:
        return {"classification": "SEMANTIC_REVIEW_REQUIRED", "recommendation": "DO_NOT_COALESCE"}
    return {"classification": "KEEP_CURRENT_ROUTE", "recommendation": "DIRECT_TEAM_MATCH"}


def markdown(report):
    lines = [
        "# FRL automated source-route coverage audit", "",
        "Diagnostic evidence only: this report does not promote a source or derivation into a governed metric.", "",
        "## Route decisions", "",
        "| Direct field | Player field | Classification | Recommendation |",
        "|---|---|---|---|",
    ]
    for field, item in report["route_decisions"].items():
        lines.append(
            f"| `{field}` | `{PAIRS[field]}` | `{item['classification']}` | `{item['recommendation']}` |"
        )
    lines += ["", "## Priority direct fixture coverage", ""]
    lines.append("| Field | " + " | ".join(SEASONS) + " |")
    lines.append("|---|" + "|".join("---:" for _ in SEASONS) + "|")
    for field in DIRECT_FIELDS:
        values = [str(report["seasons"][s]["direct_coverage"][field]["fixtures_both_sides"]) for s in SEASONS]
        lines.append(f"| `{field}` | " + " | ".join(values) + " |")
    lines += ["", "## Direct versus player-derived overlap", ""]
    lines.append("| Field | Season | Direct fx | Player-derived fx | Overlap sides | Exact | Mean abs diff | Max abs diff |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for field in PAIRS:
        for season in SEASONS:
            item = report["seasons"][season]["direct_vs_player"][field]
            if not item["direct_in_schema"] and not item["player_in_schema"]:
                continue
            mean = "" if item["mean_abs_diff"] is None else f"{item['mean_abs_diff']:.6g}"
            lines.append(
                f"| `{field}` | {season} | {item['direct_fixtures']} | {item['player_derived_fixtures']} | "
                f"{item['overlap_team_sides']} | {item['exact_matches']} | {mean} | {item['max_abs_diff']:.6g} |"
            )
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pl-root", type=Path, required=True)
    parser.add_argument("--fpl-root", type=Path)
    parser.add_argument("--json-out", type=Path, default=Path("source_route_coverage.json"))
    parser.add_argument("--md-out", type=Path, default=Path("source_route_coverage.md"))
    args = parser.parse_args()
    if not args.pl_root.is_dir():
        raise SystemExit(f"PL source root not found: {args.pl_root}")

    seasons = {season: season_audit(args.pl_root, season) for season in SEASONS}
    report = {
        "schema_version": "1.0.0",
        "scope": "2016-17_to_2025-26",
        "live_api_calls": False,
        "source_families": source_family_inventory(args.pl_root, args.fpl_root),
        "seasons": seasons,
        "route_decisions": {field: decision(field, seasons) for field in PAIRS},
        "warning": "Player-derived values are audit candidates only. Production use requires explicit semantic and missingness contracts.",
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    args.md_out.write_text(markdown(report), encoding="utf-8")

    print("FRL SOURCE ROUTE COVERAGE AUDIT")
    for season in SEASONS:
        item = seasons[season]
        print(f"{season}: direct matches={item['direct_matches']} player matches={item['player_matches']}")
    print("ROUTE DECISIONS")
    for field, item in report["route_decisions"].items():
        print(f"{field}: {item['classification']} -> {item['recommendation']}")
    print(f"JSON: {args.json_out}")
    print(f"Markdown: {args.md_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
