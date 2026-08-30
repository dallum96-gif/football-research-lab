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
        "blank_rule": "ZERO_WHEN_GOVERNED_TRIGGER_ZERO",
    },
    EXPECTED_ASSISTS: {
        "slug": "expected_assists",
        "source_field": "expectedAssists",
        "trigger_field": None,
        "blank_rule": "ZERO_ALWAYS_AUDITED_PLAYER_REPRESENTATION",
    },
    EXPECTED_GOALS_ON_TARGET: {
        "slug": "expected_goals_on_target",
        "source_field": "expectedGoalsOnTarget",
        "trigger_field": "onTargetScoringAttempt",
        "blank_rule": "ZERO_WHEN_GOVERNED_TRIGGER_ZERO",
    },
}

RUNTIME_FIELDS = (
    "season",
    "fixture_id",
    "home_expected_goals",
    "home_expected_assists",
    "home_expected_goals_on_target",
    "away_expected_goals",
    "away_expected_assists",
    "away_expected_goals_on_target",
)


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
        return {
            "value": None,
            "status": "FIELD_UNAVAILABLE",
            "player_rows": len(player_rows),
            "source_observed_rows": 0,
            "structural_zero_rows": 0,
            "unsafe_missing_rows": 0,
        }
    if not player_rows:
        return {
            "value": None,
            "status": "NO_PLAYER_MATCH_ROWS",
            "player_rows": 0,
            "source_observed_rows": 0,
            "structural_zero_rows": 0,
            "unsafe_missing_rows": 0,
        }
    if trigger_field and trigger_field not in source_fields:
        return {
            "value": None,
            "status": "TRIGGER_FIELD_UNAVAILABLE",
            "player_rows": len(player_rows),
            "source_observed_rows": 0,
            "structural_zero_rows": 0,
            "unsafe_missing_rows": 0,
        }

    total = 0.0
    observed = 0
    structural_zero = 0
    unsafe_missing = 0

    for row in player_rows:
        value = num(row.get(source_field))
        if value is not None:
            total += value
            observed += 1
            continue

        if metric == EXPECTED_ASSISTS:
            structural_zero += 1
            continue

        trigger_value = num(row.get(trigger_field))
        if trigger_value is not None and trigger_value > 0:
            unsafe_missing += 1
        else:
            structural_zero += 1

    if unsafe_missing:
        return {
            "value": None,
            "status": "MISSING_POSITIVE_TRIGGER_INPUT",
            "player_rows": len(player_rows),
            "source_observed_rows": observed,
            "structural_zero_rows": structural_zero,
            "unsafe_missing_rows": unsafe_missing,
        }

    return {
        "value": total,
        "status": "AVAILABLE",
        "player_rows": len(player_rows),
        "source_observed_rows": observed,
        "structural_zero_rows": structural_zero,
        "unsafe_missing_rows": 0,
    }


def _side_columns(prefix: str, metric: str, derived: dict) -> dict[str, str | int | float]:
    slug = METRIC_SPECS[metric]["slug"]
    value = derived["value"]
    return {
        f"{prefix}_{slug}": "" if value is None else format(float(value), ".12g"),
        f"{prefix}_{slug}_status": derived["status"],
        f"{prefix}_{slug}_player_rows": derived["player_rows"],
        f"{prefix}_{slug}_source_observed_rows": derived["source_observed_rows"],
        f"{prefix}_{slug}_structural_zero_rows": derived["structural_zero_rows"],
        f"{prefix}_{slug}_unsafe_missing_rows": derived["unsafe_missing_rows"],
    }


def materialize(pl_root: Path) -> tuple[list[dict], dict]:
    packaged = _read_packaged_fixtures()
    by_season = {season: [] for season in SEASONS}
    for row in packaged:
        by_season[row["season"]].append(row)

    output: list[dict] = []
    coverage = {
        metric: {season: 0 for season in SEASONS}
        for metric in METRIC_SPECS
    }
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
                    f"Direct source bridge missing for {season}/{bridge['fixture_id']} "
                    f"source_match_id={direct_match_id}"
                )

            home_team_id = str(direct_sides["home"].get("team_id", "")).strip()
            away_team_id = str(direct_sides["away"].get("team_id", "")).strip()
            player_match_id = player_pairs.get((home_team_id, away_team_id))
            if not player_match_id:
                raise MaterializationError(
                    f"Player-match bridge missing for {season}/{bridge['fixture_id']} "
                    f"pair={home_team_id}/{away_team_id}"
                )

            record: dict[str, str | int | float] = {
                "season": season,
                "fixture_id": bridge["fixture_id"],
                "representation": PLAYER_MATCH_DERIVED_TEAM_MATCH,
                "construction_version": CONSTRUCTION_VERSION,
                "direct_source_match_id": direct_match_id,
                "player_source_match_id": player_match_id,
                "source_home_team_id": home_team_id,
                "source_away_team_id": away_team_id,
            }

            side_results = {"home": {}, "away": {}}
            for side, team_id in (("home", home_team_id), ("away", away_team_id)):
                rows = player[player_match_id].get(team_id, [])
                for metric in METRIC_SPECS:
                    derived = _derive_metric(rows, metric, player_fields)
                    side_results[side][metric] = derived
                    record.update(_side_columns(side, metric, derived))
                    state_counts[metric][season][derived["status"]] += 1

            for metric in METRIC_SPECS:
                if all(
                    side_results[side][metric]["value"] is not None
                    for side in ("home", "away")
                ):
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

    metadata = {
        "schema_version": SCHEMA_VERSION,
        "construction_version": CONSTRUCTION_VERSION,
        "representation": PLAYER_MATCH_DERIVED_TEAM_MATCH,
        "source_repository": SOURCE_REPOSITORY,
        "source_family": "players_match_stats",
        "seasons": list(SEASONS),
        "row_count": len(output),
        "fixture_population_per_season": 380,
        "runtime_fields": list(RUNTIME_FIELDS),
        "coverage_fixtures": coverage,
        "team_side_state_counts": {
            metric: {
                season: dict(sorted(state_counts[metric][season].items()))
                for season in SEASONS
            }
            for metric in METRIC_SPECS
        },
        "missingness_rules": {
            EXPECTED_GOALS: (
                "Blank player expectedGoals is zero only when governed totalShots is zero; "
                "positive-shot blank xG makes the team-match derivation missing."
            ),
            EXPECTED_ASSISTS: (
                "Blank player expectedAssists is structural zero for the audited 2022-23 "
                "through 2025-26 player-match representation."
            ),
            EXPECTED_GOALS_ON_TARGET: (
                "Blank player expectedGoalsOnTarget is zero only when governed "
                "onTargetScoringAttempt is zero; positive-SOT blank xGOT makes the "
                "team-match derivation missing."
            ),
        },
        "representation_mixing_allowed": False,
        "runtime_note": (
            "The tracked runtime artifact is intentionally compact. Per-player derivation "
            "diagnostics are reproducible from the pinned source and summarised in "
            "team_side_state_counts rather than duplicated on every runtime row."
        ),
    }
    return output, metadata


def _runtime_rows(rows: list[dict]) -> list[dict[str, str]]:
    return [
        {field: str(row.get(field, "")) for field in RUNTIME_FIELDS}
        for row in rows
    ]


def _write_runtime_csv(path: Path, rows: list[dict]) -> dict[str, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=RUNTIME_FIELDS,
            extrasaction="raise",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(_runtime_rows(rows))

    artifact = path.read_bytes()
    digest = hashlib.sha256(artifact).hexdigest()
    return {
        "artifact_compression": "none",
        "artifact_sha256": digest,
        "uncompressed_csv_sha256": digest,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Materialize governed player-derived team expected metrics."
    )
    parser.add_argument("--pl-root", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument(
        "--csv-out",
        type=Path,
        default=Path("data/frl_player_derived_expected_metrics_v1.csv"),
    )
    parser.add_argument(
        "--metadata-out",
        type=Path,
        default=Path("data/frl_player_derived_expected_metrics_v1_metadata.json"),
    )
    args = parser.parse_args()

    if not args.pl_root.is_dir():
        raise SystemExit(f"PL source root not found: {args.pl_root}")

    rows, metadata = materialize(args.pl_root)
    artifact_metadata = _write_runtime_csv(args.csv_out, rows)
    metadata.update(artifact_metadata)
    metadata["artifact_path"] = str(args.csv_out).replace("\\", "/")
    metadata["source_commit"] = args.source_commit
    args.metadata_out.parent.mkdir(parents=True, exist_ok=True)
    args.metadata_out.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("FRL PLAYER-DERIVED EXPECTED METRICS MATERIALIZATION")
    print(f"rows={len(rows)}")
    print(f"source_commit={args.source_commit}")
    print(f"artifact_sha256={metadata['artifact_sha256']}")
    for metric in METRIC_SPECS:
        print(metric)
        for season in SEASONS:
            print(
                f"  {season}: fixtures={metadata['coverage_fixtures'][metric][season]} "
                f"states={metadata['team_side_state_counts'][metric][season]}"
            )
    print(f"CSV: {args.csv_out}")
    print(f"Metadata: {args.metadata_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
