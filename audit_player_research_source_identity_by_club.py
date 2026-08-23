from __future__ import annotations

import csv
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

import player_research
from source_family_adapters import player_match_source_rows_for_season

ROOT = Path(__file__).resolve().parent
TEAM_SEASONS = ROOT / "identity" / "team_seasons.csv"
SEASONS = tuple(player_research.available_seasons())


def norm(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.casefold().replace("'", "")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def team_map() -> dict[tuple[str, str], str]:
    out = {}
    with TEAM_SEASONS.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if str(row.get("mapping_status", "")).strip() != "VERIFIED":
                continue
            season = str(row.get("season", "")).strip()
            local_id = str(row.get("local_team_id", "")).strip()
            persistent = str(row.get("persistent_team_code", "")).strip()
            if season and local_id and persistent:
                out[(season, local_id)] = persistent
    return out


def research_keys(season: str) -> dict[tuple[str, str], set[str]]:
    out = defaultdict(set)
    for row in player_research._load_season_rows(season):
        name = norm(player_research.display_player_name(row))
        team_code = str(row.get("team_code") or "").strip()
        if name and team_code:
            out[(name, team_code)].add(player_research.seasonal_player_id(row))
    return out


def source_keys(season: str, tm: dict[tuple[str, str], str]) -> dict[tuple[str, str], set[str]]:
    out = defaultdict(set)
    for row in player_match_source_rows_for_season(season):
        name = norm(row.get("playerName") or row.get("player_name") or row.get("name"))
        local_team = str(row.get("team_id") or "").strip()
        persistent = tm.get((season, local_team), "")
        source_id = str(row.get("playerId") or row.get("player_id") or row.get("pl_code") or "").strip()
        if name and persistent and source_id:
            out[(name, persistent)].add(source_id)
    return out


def main() -> None:
    tm = team_map()
    total_exact = total_ambiguous = total_missing_source = total_missing_research = 0
    print("=" * 104)
    print("FRL PLAYER RESEARCH -> SOURCE PLAYER IDENTITY BY VERIFIED CLUB")
    print("=" * 104)
    print("Existing Player Research + verified team hierarchy; no identity promotion.")
    print()
    for i, season in enumerate(SEASONS, 1):
        research = research_keys(season)
        source = source_keys(season, tm)
        exact = ambiguous = missing_source = missing_research = 0
        for key, research_ids in research.items():
            source_ids = source.get(key, set())
            if not source_ids:
                missing_source += 1
            elif len(source_ids) == 1:
                exact += 1
            else:
                ambiguous += 1
        for key in source:
            if key not in research:
                missing_research += 1
        total_exact += exact
        total_ambiguous += ambiguous
        total_missing_source += missing_source
        total_missing_research += missing_research
        print(f"  [{i:02d}/{len(SEASONS):02d}] {season}: exact={exact} ambiguous={ambiguous} missing_source={missing_source} missing_research={missing_research}")
    print("\nTOTAL")
    print(f"  Exact seasonal research->source links: {total_exact:,}")
    print(f"  Ambiguous:                              {total_ambiguous:,}")
    print(f"  Research keys missing source player:   {total_missing_source:,}")
    print(f"  Source keys missing Player Research:   {total_missing_research:,}")
    print("\nNo files were written or modified.")
    print("=" * 104)


if __name__ == "__main__":
    main()
