"""Read-only inventory of native player identity surfaces across source families.

This deliberately does not reconcile or promote identities. It inventories the
keys that each source family actually exposes, with season/path context, so the
next reconciliation layer can be built from observed evidence rather than
assumed schemas.
"""
from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path


SEASON_RE = re.compile(r"(?:^|/)(\d{4}-\d{2})(?:_.*)?(?:\.csv)?$")
SEASON_ANY_RE = re.compile(r"(\d{4}-\d{2})")


def read_csv_header(path: Path) -> list[str]:
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with path.open("r", encoding=encoding, newline="") as fh:
                return next(csv.reader(fh))
        except UnicodeDecodeError:
            continue
        except StopIteration:
            return []
    raise ValueError(f"Could not decode CSV header: {path}")


def season_from_path(path: Path) -> str | None:
    match = SEASON_ANY_RE.search(path.name)
    return match.group(1) if match else None


def emit(rows: list[dict[str, str]], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "season",
        "source_family",
        "surface",
        "identity_key",
        "identity_role",
        "context_key",
        "path_pattern",
        "status",
        "notes",
    ]
    with out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def add_row(rows: list[dict[str, str]], **kwargs: str) -> None:
    rows.append(
        {
            "season": kwargs.get("season", ""),
            "source_family": kwargs.get("source_family", ""),
            "surface": kwargs.get("surface", ""),
            "identity_key": kwargs.get("identity_key", ""),
            "identity_role": kwargs.get("identity_role", ""),
            "context_key": kwargs.get("context_key", ""),
            "path_pattern": kwargs.get("path_pattern", ""),
            "status": kwargs.get("status", "OBSERVED"),
            "notes": kwargs.get("notes", ""),
        }
    )


def main() -> None:
    root = Path(__file__).resolve().parent / "source"
    if not root.exists():
        raise FileNotFoundError(f"CI source checkout not found: {root}")

    rows: list[dict[str, str]] = []
    summary: defaultdict[tuple[str, str], set[str]] = defaultdict(set)

    # PL player-match source family.
    for path in sorted(root.glob("pl_stats/**/*_players_match_stats.csv")):
        season = season_from_path(path)
        if not season:
            continue
        header = {h.strip() for h in read_csv_header(path)}
        for key, role in (
            ("playerId", "NATIVE_LONGITUDINAL_SOURCE_ID"),
            ("name", "DISPLAY_IDENTITY"),
            ("teamId", "SEASONAL_TEAM_CONTEXT"),
        ):
            if key in header:
                add_row(
                    rows,
                    season=season,
                    source_family="PL_OPTAPLAYER_MATCH",
                    surface="player_match_stats",
                    identity_key=key,
                    identity_role=role,
                    context_key="teamId" if "teamId" in header else "",
                    path_pattern="pl_stats/**/{season}_players_match_stats.csv",
                    notes="Observed in native player-match source header.",
                )
                summary[("PL_OPTAPLAYER_MATCH", season)].add(key)
        
    # PL player-season source family.
    for path in sorted(root.glob("pl_stats/**/*_players_stats.csv")):
        season = season_from_path(path)
        if not season:
            continue
        header = {h.strip() for h in read_csv_header(path)}
        for key, role in (
            ("playerId", "NATIVE_LONGITUDINAL_SOURCE_ID"),
            ("name", "DISPLAY_IDENTITY"),
            ("teamId", "SEASONAL_TEAM_CONTEXT"),
        ):
            if key in header:
                add_row(
                    rows,
                    season=season,
                    source_family="PL_OPTAPLAYER_SEASON",
                    surface="player_stats",
                    identity_key=key,
                    identity_role=role,
                    context_key="teamId" if "teamId" in header else "",
                    path_pattern="pl_stats/**/{season}_players_stats.csv",
                    notes="Observed in native player-season source header.",
                )
                summary[("PL_OPTAPLAYER_SEASON", season)].add(key)

    # FPL merged per-team player files. The build_index_fpl implementation
    # establishes player_code as the source-native key on this surface.
    for path in sorted(root.glob("fpl_scraper/fpl_stats/teams/*/players/*_all_players_gw.csv")):
        season = season_from_path(path)
        if not season:
            continue
        header = {h.strip() for h in read_csv_header(path)}
        for key, role in (
            ("player_code", "FPL_LONGITUDINAL_PLAYER_CODE"),
            ("element", "FPL_SEASONAL_ELEMENT"),
            ("first_name", "DISPLAY_IDENTITY_COMPONENT"),
            ("second_name", "DISPLAY_IDENTITY_COMPONENT"),
            ("web_name", "DISPLAY_IDENTITY"),
            ("team", "FPL_SEASONAL_TEAM_ELEMENT"),
        ):
            if key in header:
                add_row(
                    rows,
                    season=season,
                    source_family="FPL",
                    surface="team_player_gw_merged",
                    identity_key=key,
                    identity_role=role,
                    context_key="team" if "team" in header else "",
                    path_pattern="fpl_scraper/fpl_stats/teams/*/players/*_{season}_all_players_gw.csv",
                    notes="Observed in per-team historical player file.",
                )
                summary[("FPL", season)].add(key)

    # FPL individual player directories: the directory name itself carries a
    # source-native code even when the row schema varies historically.
    for path in sorted(root.glob("fpl_scraper/fpl_stats/players/*/*_gw_stats.csv")):
        season = season_from_path(path)
        if not season:
            continue
        player_dir = path.parent.name
        code = player_dir.rsplit("_", 1)[-1]
        if code.isdigit():
            add_row(
                rows,
                season=season,
                source_family="FPL",
                surface="individual_player_directory",
                identity_key="player_directory_code",
                identity_role="FPL_LONGITUDINAL_PLAYER_CODE",
                context_key="",
                path_pattern="fpl_scraper/fpl_stats/players/{name}_{code}/{season}_gw_stats.csv",
                notes="Numeric player code observed in source directory key.",
            )
            summary[("FPL", season)].add("player_directory_code")
        header = {h.strip() for h in read_csv_header(path)}
        for key, role in (
            ("element", "FPL_SEASONAL_ELEMENT"),
            ("player_code", "FPL_LONGITUDINAL_PLAYER_CODE"),
            ("name", "DISPLAY_IDENTITY"),
        ):
            if key in header:
                add_row(
                    rows,
                    season=season,
                    source_family="FPL",
                    surface="individual_player_gw_stats",
                    identity_key=key,
                    identity_role=role,
                    context_key="",
                    path_pattern="fpl_scraper/fpl_stats/players/{name}_{code}/{season}_gw_stats.csv",
                    notes="Observed in individual player historical file header.",
                )
                summary[("FPL", season)].add(key)

    # Current/derived FPL index is kept separate because it is explicitly a
    # generated index, not the primary historical observation surface.
    index_path = root / "fpl_scraper" / "fpl_stats" / "_index" / "_players_index.json"
    if index_path.is_file():
        try:
            data = json.loads(index_path.read_text(encoding="utf-8"))
            seasons = sorted({str(s) for row in data.values() for s in row})
            for season in seasons:
                add_row(
                    rows,
                    season=season,
                    source_family="FPL",
                    surface="generated_players_index",
                    identity_key="json_top_level_key",
                    identity_role="FPL_LONGITUDINAL_PLAYER_CODE",
                    context_key="season",
                    path_pattern="fpl_scraper/fpl_stats/_index/_players_index.json",
                    notes="Generated index keyed by player code; not treated as primary historical evidence.",
                )
        except (OSError, json.JSONDecodeError):
            add_row(
                rows,
                source_family="FPL",
                surface="generated_players_index",
                identity_key="json_top_level_key",
                identity_role="FPL_LONGITUDINAL_PLAYER_CODE",
                path_pattern="fpl_scraper/fpl_stats/_index/_players_index.json",
                status="UNREADABLE",
            )

    emit(rows, Path(__file__).resolve().parent / "data" / "source_family_player_identity_inventory.csv")

    # Compact console summary for CI logs.
    print("=" * 104)
    print("FRL SOURCE-FAMILY PLAYER IDENTITY INVENTORY")
    print("=" * 104)
    print(f"Inventory rows: {len(rows):,}")
    for (family, season), keys in sorted(summary.items()):
        print(f"{family:24s} {season:8s} keys={','.join(sorted(keys))}")
    print()
    print("No identity reconciliation or promotion performed.")
    print("Output: data/source_family_player_identity_inventory.csv")
    print("=" * 104)


if __name__ == "__main__":
    main()
