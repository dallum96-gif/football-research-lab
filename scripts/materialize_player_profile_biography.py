"""Materialise packaged squad biography evidence for Player Profile runtime."""
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUPPORTED_SEASONS = tuple(f"{year}-{str(year + 1)[-2:]}" for year in range(2016, 2027))
DEFAULT_OUTPUT = ROOT / "data" / "player_profile_biography_v1.csv"
DEFAULT_METADATA = ROOT / "data" / "player_profile_biography_v1.metadata.json"

FIELDS = (
    "season",
    "source_player_id",
    "team_name",
    "display_name",
    "first_name",
    "last_name",
    "nationality",
    "nationality_code",
    "birth_date",
    "birth_country",
    "preferred_foot",
    "height_cm",
    "weight_kg",
    "shirt_number",
    "join_date",
    "on_loan",
    "source_file",
)


def _team_name(path: Path, pl_stats_root: Path) -> str:
    club_dir = path.relative_to(pl_stats_root).parts[0]
    name = club_dir.rsplit("_", 1)[0]
    return name.replace("_", " ")


def _season_files(pl_stats_root: Path, season: str) -> tuple[Path, ...]:
    return tuple(sorted(
        path
        for path in pl_stats_root.glob(f"*/squad/{season}_squad.csv")
        if not any(part.startswith("_") for part in path.relative_to(pl_stats_root).parts)
    ))


def materialize_season(pl_stats_root: Path, season: str) -> list[dict[str, str]]:
    paths = _season_files(pl_stats_root, season)
    if not paths:
        raise RuntimeError(f"No squad source files found for {season}")

    output: dict[tuple[str, str], dict[str, str]] = {}
    for path in paths:
        team_name = _team_name(path, pl_stats_root)
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            required = {"playerId", "displayName", "firstName", "lastName"}
            missing = required - set(reader.fieldnames or ())
            if missing:
                raise RuntimeError(f"{path} is missing required fields: {sorted(missing)}")
            for source in reader:
                source_player_id = str(source.get("playerId") or "").strip()
                if not source_player_id:
                    continue
                row = {
                    "season": season,
                    "source_player_id": source_player_id,
                    "team_name": team_name,
                    "display_name": str(source.get("displayName") or "").strip(),
                    "first_name": str(source.get("firstName") or "").strip(),
                    "last_name": str(source.get("lastName") or "").strip(),
                    "nationality": str(source.get("nationality") or "").strip(),
                    "nationality_code": str(source.get("isoCode") or "").strip(),
                    "birth_date": str(source.get("birthDate") or "").strip(),
                    "birth_country": str(source.get("birthCountry") or "").strip(),
                    "preferred_foot": str(source.get("preferredFoot") or "").strip(),
                    "height_cm": str(source.get("height_cm") or "").strip(),
                    "weight_kg": str(source.get("weight_kg") or "").strip(),
                    "shirt_number": str(source.get("shirtNumber") or "").strip(),
                    "join_date": str(source.get("joinDate") or "").strip(),
                    "on_loan": str(source.get("onLoan") or "").strip(),
                    "source_file": str(path.relative_to(pl_stats_root)),
                }
                key = (source_player_id, team_name.casefold())
                previous = output.get(key)
                if previous is not None and previous != row:
                    raise RuntimeError(
                        f"Conflicting duplicate squad biography rows for {season}/{source_player_id}/{team_name}"
                    )
                output[key] = row

    return sorted(output.values(), key=lambda row: (int(row["source_player_id"]), row["team_name"].casefold()))


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
        raise RuntimeError(f"Squad source root not found: {pl_stats_root}")

    rows = [row for season in seasons for row in materialize_season(pl_stats_root, season)]
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    counts = {season: sum(row["season"] == season for row in rows) for season in seasons}
    metadata = {
        "schema_version": "1.0.0",
        "projection_version": "PLAYER_PROFILE_BIOGRAPHY_V1",
        "milestone": "PLAYER_PROFILE_UNIVERSAL_FOUNDATION_V1",
        "materialized_date": date.today().isoformat(),
        "source_repository": "imadeddine-belkat/Premier-League-Stats",
        "source_release_sha": source_release_sha,
        "source_release_date": source_release_date,
        "source_resource": "pl_stats/*/squad/{season}_squad.csv",
        "source_grain": "player-squad-season",
        "runtime_policy": "RUNTIME_READS_PACKAGED_PROJECTION_ONLY",
        "identity_policy": "VERIFIED_PROFILE_SOURCE_PLAYER_ID_PLUS_EXACT_NORMALISED_NAME",
        "seasons": list(seasons),
        "rows_by_season": counts,
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
