"""Audit longitudinal source-player -> Player Research identity closure.

Read-only. Uses only the existing source player-match records, the existing
FPL element -> source-player crosswalk candidates, and the existing Player
Research canonical-name function. It never writes canonical data and never
performs fuzzy matching or metric aggregation.
"""
from __future__ import annotations

from collections import defaultdict

import player_identity_crosswalk as crosswalk
import player_research
import player_match_stats


def main() -> None:
    seasons = tuple(player_research.available_seasons())
    source_ids: set[str] = set()
    observations_by_season: dict[str, list[str]] = {}

    for season in seasons:
        sids: list[str] = []
        for row in player_match_stats.player_match_source_rows(season):
            sid = str(row.get("playerId") or row.get("player_id") or row.get("pl_code") or "").strip()
            if sid:
                source_ids.add(sid)
                sids.append(sid)
        observations_by_season[season] = sids

    candidates = crosswalk.build_crosswalk_candidates()
    pair_to_sources: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in candidates:
        pair_to_sources[(str(row["season"]), str(row["element"]))].add(str(row["source_player_id"]))

    source_to_research: dict[str, set[str]] = defaultdict(set)
    for season in seasons:
        for row in player_research._load_season_rows(season):
            element = str(row.get("element") or row.get("player_code") or row.get("id") or "").strip()
            if not element:
                continue
            canonical = player_research.canonical_player_name(row)
            if not canonical:
                continue
            for sid in pair_to_sources.get((season, element), set()):
                source_to_research[sid].add(canonical)

    unique = ambiguous = uncovered = 0
    for sid in sorted(source_ids):
        count = len(source_to_research.get(sid, set()))
        if count == 1:
            unique += 1
        elif count > 1:
            ambiguous += 1
        else:
            uncovered += 1

    unique_obs = ambiguous_obs = uncovered_obs = 0
    for season in seasons:
        season_unique = season_ambiguous = season_uncovered = 0
        for sid in observations_by_season[season]:
            count = len(source_to_research.get(sid, set()))
            if count == 1:
                season_unique += 1
            elif count > 1:
                season_ambiguous += 1
            else:
                season_uncovered += 1
        unique_obs += season_unique
        ambiguous_obs += season_ambiguous
        uncovered_obs += season_uncovered
        print(f"{season}: unique={season_unique:,} ambiguous={season_ambiguous:,} uncovered={season_uncovered:,}")

    print("=" * 96)
    print("FRL SOURCE PLAYER -> PLAYER RESEARCH IDENTITY CLOSURE AUDIT")
    print("=" * 96)
    print("Existing source-player observations + existing crosswalk + existing Player Research identity semantics; no promotion.")
    print(f"Unique source player IDs:        {unique + ambiguous + uncovered:,}")
    print(f"  UNIQUE_RESEARCH_IDENTITY:      {unique:,}")
    print(f"  AMBIGUOUS_RESEARCH_IDENTITY:   {ambiguous:,}")
    print(f"  NO_RESEARCH_IDENTITY:           {uncovered:,}")
    print()
    print(f"Player-match observations:       {unique_obs + ambiguous_obs + uncovered_obs:,}")
    print(f"  UNIQUE_RESEARCH_IDENTITY:      {unique_obs:,}")
    print(f"  AMBIGUOUS_RESEARCH_IDENTITY:   {ambiguous_obs:,}")
    print(f"  NO_RESEARCH_IDENTITY:           {uncovered_obs:,}")
    print()
    print("No files were written or modified.")
    print("=" * 96)


if __name__ == "__main__":
    main()
