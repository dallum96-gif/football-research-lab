"""Read-only discovery audit for early-season FPL club context.

The 2016-17 through 2019-20 FPL gameweek files do not expose team/team_code
in the current loader. Before building any bridge, inspect the local upstream
source tree for another existing file that carries both a player identity key
and team/club context for the same season.

This audit reports headers and candidate files only. It does not create or
promote any identity mapping.
"""
from __future__ import annotations

import csv
from pathlib import Path

PL_ROOT = Path(r"C:\Users\dlall\football_database\Premier-League-Stats\pl_stats")
MERGED_PLAYERS = PL_ROOT / "_merged" / "players"
SEASONS = ("2016-17", "2017-18", "2018-19", "2019-20")
PLAYER_KEYS = {"element", "player_code", "playerid", "player_id", "id"}
TEAM_KEYS = {
    "team", "team_id", "team_code", "club", "club_id", "canonical_name",
    "source_name", "persistent_team_code", "local_team_id",
}


def read_header(path: Path):
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                return next(csv.reader(handle), [])
        except (UnicodeDecodeError, StopIteration):
            continue
    return []


def season_player_file(season: str) -> Path | None:
    path = MERGED_PLAYERS / f"{season}_all_players_gw.csv"
    return path if path.is_file() else None


def relevant(name: str, season: str) -> bool:
    lower = name.lower()
    return season in name and lower.endswith(".csv")


def main() -> None:
    print("=" * 96)
    print("FRL EARLY-SEASON FPL CLUB-PATH DISCOVERY AUDIT")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 96)
    print(f"Source root: {PL_ROOT}")

    if not PL_ROOT.is_dir():
        raise SystemExit(f"Approved upstream source root not found: {PL_ROOT}")

    print("\nEARLY FPL GAMEWEEK FILE HEADERS:")
    for season in SEASONS:
        path = season_player_file(season)
        if path is None:
            print(f"  {season}: MISSING")
            continue
        cols = read_header(path)
        print(f"  {season}: {cols}")

    print("\nCANDIDATE SOURCE FILES WITH BOTH PLAYER-ID + TEAM/CLUB FIELDS:")
    candidates = []
    for path in PL_ROOT.rglob("*.csv"):
        if any(path.name.startswith(f"{season}_") or f"_{season}_" in path.name for season in SEASONS) is False:
            continue
        cols = {c.strip().casefold() for c in read_header(path)}
        has_player = bool(cols & PLAYER_KEYS)
        has_team = bool(cols & TEAM_KEYS)
        if has_player and has_team:
            candidates.append((path, sorted(cols & PLAYER_KEYS), sorted(cols & TEAM_KEYS)))

    if not candidates:
        print("  NONE FOUND")
    else:
        for path, player_cols, team_cols in sorted(candidates):
            print(f"  {path} | player_keys={player_cols} | team_keys={team_cols}")

    print("\nNOTES:")
    print("  - This is discovery only; no identity joins are attempted.")
    print("  - Source-local IDs remain source-local until an explicit verified bridge exists.")
    print("  - The next implementation step depends on whether a defensible existing source seam is found.")
    print("\nNo files were written or modified.")
    print("=" * 96)


if __name__ == "__main__":
    main()
