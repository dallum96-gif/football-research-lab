from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from expected_metric_routing import (  # noqa: E402
    EXPECTED_ASSISTS,
    EXPECTED_GOALS,
    EXPECTED_GOALS_ON_TARGET,
    PLAYER_MATCH_DERIVED_TEAM_MATCH,
    REPRESENTATION_FIXTURE_COVERAGE,
)
from audit_source_routes import direct_index, num, player_index  # noqa: E402


CONSTRUCTION_VERSION = "FRL_PLAYER_DERIVED_EXPECTED_METRICS_V1"
SCHEMA_VERSION = "1.0.0"
SOURCE_REPOSITORY = "imadeddine-belkat/Premier-League-Stats"
SEASONS = ("2022-23", "2023-24", "2024-25", "2025-26")
PACKAGED_FIXTURES = ROOT / "data" / "fixture_match_stats.csv"

METRIC_SPECS = {
    EXPECTED_GOALS: {
        "slug": "expected_goals",
        "source_field": "expectedGoals",
        "trigger_field": "totalShots",
    },
    EXPECTED_ASSISTS: {
        "slug": "expected_assists",
        "source_field": "expectedAssists",
        "trigger_field": None,
    },
    EXPECTED_GOALS_ON_TARGET: {
        "slug": "expected_goals_on_target",
        "source_field": "expectedGoalsOnTarget",
        "trigger_field": "onTargetScoringAttempt",
    },
}


class MaterializationError(RuntimeError):
    pass


def _read_packaged_fixtures() -> tuple[dict[str, str], ...]:
    with PACKAGED_FIXTURES.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = tuple(csv.DictReader(handle))
    selected = tuple(row for row in rows if row.get("season") in SEASONS)
    if len(selected) != 380 * len(SEASONS):
        raise MaterializationError(
            f"Expected {380 * len(SEASONS)} packaged fixtures, found {len(selected)}"
        )
    keys = [(row.get("season"), row.get("fixture_id")) for row in selected]
    if len(keys) != len(set(keys)):
        raise MaterializationError("Packaged fixture bridge contains duplicate season/fixture keys")
    return selected


def _derive_metric(
    player_rows: list[dict],
    metric: str,
    source_fields: set[str],
) -> dict:
    spec = METRIC_SPECS[metric]
    source_field = spec["source_field"]
    trigger_field = spec["trigger_field"]

    if source_field not in source_fields:
        return {"value": None, "status": "FIELD_UNAVAILABLE"}
    if not player_rows:
        return {"value": None, "status": "NO_PLAYER_MATCH_ROWS"}
    if trigger_field and trigger_field not in source_fields:
        return {"value": None, "status": "TRIGGER_FIELD_UNAVAILABLE"}

    total = 0.0
    unsafe_missing = 0
    for row in player_rows:
        value = num(row.get(source_field))
        if value is not None:
            total += value
            continue

        if metric == EXPECTED_ASSISTS:
            continue

        trigger_value = num(row.get(trigger_field))
        if trigger_value is not None and trigger_value > 0:
            unsafe_missing += 1

    if unsafe_missing:
        return {"value": None, "status": "MISSING_POSITIVE_TRIGGER_INPUT"}

    # Preserved expected-metric source observations use four-decimal precision.
    # Canonicalising after additive aggregation prevents binary-float noise such
    # as 0.9967999999999999 from becoming part of the governed artifact.
    return {"value": round(total, 4), "status": "AVAILABLE"}


def materialize(pl_root: Path) -> tuple[list[dict], dict]:
    packaged = _read_packaged_fixtures()
    by_season = {season: [] for season in SEASONS}
    for row in packaged:
        by_season[row["season"]].append(row)

    output: list[dict] = []
    coverage = {metric: {season: 0 for season in SEASONS} for metric in METRIC_SPECS}
    state_counts = {
        metric: {season: Counter() for season in SEASONS}
        for metric in METRIC_SPECS
    }

    for season in SEASONS:
        direct, _, _ = direct_index(pl_root, season)
        player, player_pairs, player_fields = player_index(pl_root, season)
        player_fields = set(player_fields)

        for bridge in sorted(by_season[season], key=lambda row: int(row["fixture_id"])):
            direct_match_id = str(bridge.get("source_match_id", "")).strip()
            direct_sides = direct.get(direct_match_id)
            if not direct_sides or "home" not in direct_sides or "away" not in direct_sides:
                raise MaterializationError(
                    f"Direct source bridge missing for {season}/{bridge['fixture_id']}"
                )

            home_team_id = str(direct_sides["home"].get("team_id", "")).strip()
            away_team_id = str(direct_sides["away"].get("team_id", "")).strip()
            player_match_id = player_pairs.get((home_team_id, away_team_id))
            if not player_match_id:
                raise MaterializationError(
                    f"Player-match bridge missing for {season}/{bridge['fixture_id']}"
                )

            record: dict[str, object] = {
                "season": season,
                "fixture_id": str(bridge["fixture_id"]),
            }
            side_results: dict[str, dict[str, dict]] = {"home": {}, "away": {}}

            for side, team_id in (("home", home_team_id), ("away", away_team_id)):
                rows = player[player_match_id].get(team_id, [])
                for metric, spec in METRIC_SPECS.items():
                    derived = _derive_metric(rows, metric, player_fields)
                    side_results[side][metric] = derived
                    record[f"{side}_{spec['slug']}"] = derived["value"]
                    state_counts[metric][season][derived["status"]] += 1

            for metric in METRIC_SPECS:
                if all(side_results[side][metric]["value"] is not None for side in ("home", "away")):
                    coverage[metric][season] += 1

            output.append(record)

    if len(output) != 1520:
        raise MaterializationError(f"Expected 1520 output rows, found {len(output)}")

    for metric in METRIC_SPECS:
        for season in SEASONS:
            expected = REPRESENTATION_FIXTURE_COVERAGE[metric][season][
                PLAYER_MATCH_DERIVED_TEAM_MATCH
            ]
            actual = coverage[metric][season]
            if actual != expected:
                raise MaterializationError(
                    f"Coverage drift for {metric} {season}: expected {expected}, got {actual}"
                )

    return output, {
        "coverage_fixtures": coverage,
        "team_side_state_counts": {
            metric: {
                season: dict(sorted(state_counts[metric][season].items()))
                for season in SEASONS
            }
            for metric in METRIC_SPECS
        },
    }


def _write_product_xg(rows: list[dict], runtime_dir: Path) -> dict[str, str]:
    runtime_dir.mkdir(parents=True, exist_ok=True)
    hashes: dict[str, str] = {}

    for season in SEASONS:
        season_rows = sorted(
            (row for row in rows if row["season"] == season),
            key=lambda row: int(str(row["fixture_id"])),
        )
        if [int(str(row["fixture_id"])) for row in season_rows] != list(range(1, 381)):
            raise MaterializationError(f"Canonical fixture sequence is incomplete for {season}")

        payload = [
            [row["home_expected_goals"], row["away_expected_goals"]]
            for row in season_rows
        ]
        text = json.dumps(payload, separators=(",", ":")) + "\n"
        path = runtime_dir / f"{season}.json"
        path.write_text(text, encoding="utf-8", newline="")
        hashes[season] = hashlib.sha256(path.read_bytes()).hexdigest()

    return hashes


def _metadata(audit: dict, hashes: dict[str, str], source_commit: str) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "construction_version": CONSTRUCTION_VERSION,
        "representation": PLAYER_MATCH_DERIVED_TEAM_MATCH,
        "metric": EXPECTED_GOALS,
        "source_repository": SOURCE_REPOSITORY,
        "source_family": "players_match_stats",
        "source_commit": source_commit,
        "seasons": list(SEASONS),
        "fixture_population_per_season": 380,
        "layout": (
            "Each season file is a 380-item JSON array ordered by canonical fixture_id "
            "1..380; each item is [home_xg, away_xg]."
        ),
        "coverage_fixtures": audit["coverage_fixtures"][EXPECTED_GOALS],
        "season_file_sha256": hashes,
        "missingness_rule": (
            "Blank player expectedGoals is structural zero only when governed player "
            "totalShots is zero; positive-shot blank xG makes the affected team-match "
            "observation unavailable."
        ),
        "representation_mixing_allowed": False,
        "product_scope": (
            "Expected goals is the first product-ready player-derived expected metric. "
            "xA and xGOT remain governed/derivable but are not yet packaged for product "
            "runtime because current Team Stats Overview does not consume them."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Materialize governed player-derived expected metrics and product xG."
    )
    parser.add_argument("--pl-root", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument(
        "--runtime-dir",
        type=Path,
        default=Path("data/player_derived_expected_goals_v1"),
    )
    parser.add_argument("--metadata-out", type=Path, default=None)
    args = parser.parse_args()

    if not args.pl_root.is_dir():
        raise SystemExit(f"PL source root not found: {args.pl_root}")

    rows, audit = materialize(args.pl_root)
    hashes = _write_product_xg(rows, args.runtime_dir)
    metadata = _metadata(audit, hashes, args.source_commit)
    metadata_out = args.metadata_out or args.runtime_dir / "metadata.json"
    metadata_out.parent.mkdir(parents=True, exist_ok=True)
    metadata_out.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("FRL PLAYER-DERIVED EXPECTED METRICS MATERIALIZATION")
    print(f"source_commit={args.source_commit}")
    print(f"xG={metadata['coverage_fixtures']}")
    print(f"xA={audit['coverage_fixtures'][EXPECTED_ASSISTS]}")
    print(f"xGOT={audit['coverage_fixtures'][EXPECTED_GOALS_ON_TARGET]}")
    print(f"runtime_dir={args.runtime_dir}")
    print(f"metadata={metadata_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
