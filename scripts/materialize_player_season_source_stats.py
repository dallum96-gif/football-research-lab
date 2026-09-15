"""Materialise governed source-native Player-Season statistics for runtime.

The source checkout is accessed only by this explicit build step. Duplicate
club-file rows for the same player-season are retained once when their values
agree and fail closed when they conflict. Source blanks stay blank.
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUPPORTED_SEASONS = tuple(
    f"{year}-{str(year + 1)[-2:]}"
    for year in range(2016, 2027)
)
DEFAULT_OUTPUT = ROOT / "data" / "player_season_source_stats_v1.csv"
DEFAULT_METADATA = (
    ROOT / "data" / "player_season_source_stats_v1.metadata.json"
)
SOURCE_FIELDS = {
    "forward_passes": "forwardPasses",
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
    return tuple(sorted(
        path
        for path in pl_stats_root.glob(
            f"*/players_stats/{season}_players_stats.csv"
        )
        if not any(
            part.startswith("_")
            for part in path.relative_to(pl_stats_root).parts
        )
    ))


def materialize_season(
    pl_stats_root: Path,
    season: str,
) -> list[dict[str, str]]:
    paths = _season_files(pl_stats_root, season)
    if not paths:
        raise RuntimeError(f"No Player-Season source files found for {season}")

    by_player: dict[str, dict[str, str]] = {}
    for path in paths:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            required = {"playerId", *SOURCE_FIELDS.values()}
            missing = required - set(reader.fieldnames or ())
            if missing:
                raise RuntimeError(
                    f"{path} is missing required fields: {sorted(missing)}"
                )

            for source in reader:
                source_player_id = str(source.get("playerId") or "").strip()
                if not source_player_id:
                    continue
                row = {
                    "season": season,
                    "source_player_id": source_player_id,
                    **{
                        metric: _normalise_number(source.get(source_field))
                        for metric, source_field in SOURCE_FIELDS.items()
                    },
                }
                previous = by_player.get(source_player_id)
                if previous is not None and previous != row:
                    raise RuntimeError(
                        "Conflicting duplicate Player-Season rows for "
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

    rows = [
        row
        for season in seasons
        for row in materialize_season(pl_stats_root, season)
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["season", "source_player_id", *SOURCE_FIELDS],
        )
        writer.writeheader()
        writer.writerows(rows)

    counts = {
        season: sum(row["season"] == season for row in rows)
        for season in seasons
    }
    observed_counts = {
        season: sum(
            row["season"] == season and row["forward_passes"] != ""
            for row in rows
        )
        for season in seasons
    }
    metadata = {
        "schema_version": "1.0.0",
        "projection_version": "PLAYER_SEASON_SOURCE_STATS_V1",
        "materialized_date": date.today().isoformat(),
        "source_repository": "imadeddine-belkat/Premier-League-Stats",
        "source_release_sha": source_release_sha,
        "source_release_date": source_release_date,
        "source_resource": "pl_stats/*/players_stats/{season}_players_stats.csv",
        "source_grain": "player-season",
        "source_fields": SOURCE_FIELDS,
        "identity_policy": {
            "current": "FPL_PLAYER_CODE_TO_PLAYER_SEASON_PLAYER_ID_EXACT",
            "historical": (
                "FPL_ELEMENT_TO_VERIFIED_PLAYER_MATCH_ID_"
                "TO_PLAYER_SEASON_PLAYER_ID"
            ),
            "unresolved": "UNAVAILABLE",
        },
        "duplicate_policy": "DEDUPLICATE_IDENTICAL_PLAYER_SEASON_ROWS",
        "missingness_policy": "SOURCE_BLANK_IS_UNAVAILABLE_NOT_ZERO",
        "seasons": list(seasons),
        "rows_by_season": counts,
        "observed_forward_passes_by_season": observed_counts,
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
