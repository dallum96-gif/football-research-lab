"""Materialise the governed Player-Season representation used by Player Profile.

Descriptive participation and all four position-specific profile templates are
preserved from the same Player-Season source row. The merged upstream season
file is preferred; direct club files are a validated fallback. Missing source
fields and source blanks remain unavailable rather than becoming zero.
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUPPORTED_SEASONS = tuple(f"{year}-{str(year + 1)[-2:]}" for year in range(2016, 2027))
DEFAULT_OUTPUT = ROOT / "data" / "player_profile_source_stats_v1.csv"
DEFAULT_METADATA = ROOT / "data" / "player_profile_source_stats_v1.metadata.json"

SOURCE_FIELDS = {
    "source_appearances": "gamesPlayed",
    "source_starts": "starts",
    "source_minutes": "timePlayed",
    "expected_goals": "expectedGoals",
    "expected_assists": "expectedAssists",
    "goals": "goals",
    "accurate_opposition_half_passes": "successfulPassesOppositionHalf",
    "forward_passes": "forwardPasses",
    "recoveries": "recoveries",
    "tackles_won": "tacklesWon",
    "total_tackles": "totalTackles",
    "interceptions": "interceptions",
    "total_clearances": "totalClearances",
    "aerial_duels": "aerialDuels",
    "aerial_duels_won": "aerialDuelsWon",
    "total_shots": "totalShots",
    "total_touches_in_opposition_box": "totalTouchesInOppositionBox",
    "successful_dribbles": "successfulDribbles",
    "expected_goals_on_target_conceded": "expectedGoalsOnTargetConceded",
    "goals_conceded": "goalsConceded",
    "saves_made": "savesMade",
    "catches": "catches",
    "punches": "punches",
    "goalkeeper_smothers": "goalkeeperSmother",
    "gk_successful_distribution": "gkSuccessfulDistribution",
    "gk_unsuccessful_distribution": "gkUnsuccessfulDistribution",
}


def _normalise_number(value: object) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    try:
        return str(float(text))
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Non-numeric Player-Season value: {text!r}") from exc


def _season_files(pl_stats_root: Path, season: str) -> tuple[Path, ...]:
    merged = pl_stats_root / "_merged" / "players" / f"{season}_players_stats.csv"
    if merged.is_file():
        return (merged,)
    return tuple(sorted(
        path
        for path in pl_stats_root.glob(f"*/players_stats/{season}_players_stats.csv")
        if not any(part.startswith("_") for part in path.relative_to(pl_stats_root).parts)
    ))


def materialize_season(pl_stats_root: Path, season: str) -> list[dict[str, str]]:
    paths = _season_files(pl_stats_root, season)
    if not paths:
        raise RuntimeError(f"No Player-Season source files found for {season}")

    by_player: dict[str, dict[str, str]] = {}
    for path in paths:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if "playerId" not in set(reader.fieldnames or ()):
                raise RuntimeError(f"{path} is missing required field playerId")
            for source in reader:
                source_player_id = str(source.get("playerId") or "").strip()
                if not source_player_id:
                    continue
                row = {
                    "season": season,
                    "source_player_id": source_player_id,
                    "source_player_name": str(source.get("playerName") or "").strip(),
                    "source_position": str(source.get("position") or "").strip(),
                    **{
                        metric: _normalise_number(source.get(source_field))
                        for metric, source_field in SOURCE_FIELDS.items()
                    },
                }
                previous = by_player.get(source_player_id)
                if previous is not None and previous != row:
                    raise RuntimeError(
                        "Conflicting duplicate Player-Season profile rows for "
                        f"{season}/{source_player_id}"
                    )
                by_player[source_player_id] = row

    return [by_player[key] for key in sorted(by_player, key=int)]


def materialize(
    pl_stats_root: Path,
    seasons: tuple[str, ...],
    output: Path,
    metadata_path: Path,
    source_release_sha: str,
    source_release_date: str,
) -> dict[str, int]:
    unknown = set(seasons) - set(SUPPORTED_SEASONS)
    if unknown:
        raise RuntimeError(f"Unsupported seasons: {sorted(unknown)}")
    if not pl_stats_root.is_dir():
        raise RuntimeError(f"Player-Season source root not found: {pl_stats_root}")

    rows = [row for season in seasons for row in materialize_season(pl_stats_root, season)]
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "season",
        "source_player_id",
        "source_player_name",
        "source_position",
        *SOURCE_FIELDS,
    ]
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    counts = {season: sum(row["season"] == season for row in rows) for season in seasons}
    observed = {
        season: {
            metric: sum(row["season"] == season and row[metric] != "" for row in rows)
            for metric in SOURCE_FIELDS
        }
        for season in seasons
    }
    metadata = {
        "schema_version": "1.1.0",
        "projection_version": "PLAYER_PROFILE_SOURCE_STATS_V1",
        "milestone": "PLAYER_PROFILE_POSITIONAL_RADARS_V1",
        "materialized_date": date.today().isoformat(),
        "source_repository": "imadeddine-belkat/Premier-League-Stats",
        "source_release_sha": source_release_sha,
        "source_release_date": source_release_date,
        "source_resource": "pl_stats/_merged/players/{season}_players_stats.csv (preferred); direct club players_stats fallback",
        "source_grain": "player-season",
        "source_fields": SOURCE_FIELDS,
        "position_templates": ["GKP", "DEF", "MID", "FWD"],
        "participation_policy": "PROFILE_PARTICIPATION_USES_SAME_PLAYER_SEASON_ROW_WHEN_COMPLETE; FPL_PLAYER_FIXTURE_AGGREGATE_IS_FAIL_CLOSED_FALLBACK",
        "denominator_policy": "PER90_USES_SAME_ROW_TIMEPLAYED; RATIOS_USE_ONLY_SAME_ROW_SOURCE_FIELDS",
        "missingness_policy": "MISSING_FIELD_OR_SOURCE_BLANK_IS_UNAVAILABLE_NOT_ZERO",
        "duplicate_policy": "DEDUPLICATE_IDENTICAL_PLAYER_SEASON_ROWS_FAIL_ON_CONFLICT",
        "seasons": list(seasons),
        "rows_by_season": counts,
        "observed_by_season": observed,
    }
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return counts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pl-stats-root", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--source-release-sha", required=True)
    parser.add_argument("--source-release-date", required=True)
    parser.add_argument("--seasons", nargs="+", default=SUPPORTED_SEASONS)
    args = parser.parse_args()
    counts = materialize(
        args.pl_stats_root,
        tuple(args.seasons),
        args.output,
        args.metadata,
        args.source_release_sha,
        args.source_release_date,
    )
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
