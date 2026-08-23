"""Audit longitudinal source-player -> stable FPL player_code closure.

Read-only. Uses the existing exact seasonal FPL->source-player crosswalk and
Player Research's preferred seasonal_player_id (player_code when available).
No fuzzy matching, no metric aggregation, no canonical writes.
"""
from __future__ import annotations

from collections import defaultdict

import player_identity_crosswalk as crosswalk
import player_research
from source_family_adapters import player_match_source_rows_for_season


def main() -> None:
    seasons = tuple(player_research.available_seasons())

    # Existing exact 1:1 seasonal anchors: source_player_id -> FPL player_code(s).
    source_to_codes: dict[str, set[str]] = defaultdict(set)
    for row in crosswalk.build_crosswalk_candidates():
        sid = str(row.get("source_player_id") or "").strip()
        code = str(row.get("element") or "").strip()
        if sid and code:
            source_to_codes[sid].add(code)

    # Verify that each code is genuinely stable across Player Research seasons.
    code_to_names: dict[str, set[str]] = defaultdict(set)
    code_to_seasons: dict[str, set[str]] = defaultdict(set)
    for season in seasons:
        for row in player_research._load_season_rows(season):
            code = player_research.seasonal_player_id(row).strip()
            if not code:
                continue
            name = player_research.display_player_name(row).strip()
            code_to_seasons[code].add(season)
            if name:
                code_to_names[code].add(name.casefold())

    unique_source = ambiguous_source = uncovered_source = 0
    stable_source = unstable_source = 0
    for sid, codes in source_to_codes.items():
        if len(codes) != 1:
            ambiguous_source += 1
            continue
        code = next(iter(codes))
        if len(code_to_names.get(code, set())) <= 1:
            stable_source += 1
            unique_source += 1
        else:
            unstable_source += 1
            ambiguous_source += 1

    # Coverage across every Player-Match observation using the longitudinal anchor.
    unique_obs = ambiguous_obs = uncovered_obs = 0
    for season in seasons:
        season_unique = season_ambiguous = season_uncovered = 0
        for row in player_match_source_rows_for_season(season):
            sid = str(row.get("playerId") or row.get("player_id") or row.get("pl_code") or "").strip()
            codes = source_to_codes.get(sid, set())
            if len(codes) != 1:
                if len(codes) > 1:
                    season_ambiguous += 1
                else:
                    season_uncovered += 1
                continue
            code = next(iter(codes))
            if len(code_to_names.get(code, set())) <= 1:
                season_unique += 1
            else:
                season_ambiguous += 1
        unique_obs += season_unique
        ambiguous_obs += season_ambiguous
        uncovered_obs += season_uncovered
        print(
            f"{season}: unique={season_unique:,} "
            f"ambiguous={season_ambiguous:,} "
            f"uncovered={season_uncovered:,}"
        )

    print("=" * 96)
    print("FRL SOURCE PLAYER -> STABLE FPL PLAYER_CODE CLOSURE AUDIT")
    print("=" * 96)
    print("Existing exact crosswalk + existing Player Research player_code only; no promotion.")
    print(f"Anchored source player IDs:      {unique_source + ambiguous_source:,}")
    print(f"  UNIQUE_STABLE_PLAYER_CODE:     {stable_source:,}")
    print(f"  AMBIGUOUS_OR_UNSTABLE:         {ambiguous_source:,}")
    print(f"  UNSTABLE_CODES:                 {unstable_source:,}")
    print()
    print(f"Player-match observations:       {unique_obs + ambiguous_obs + uncovered_obs:,}")
    print(f"  UNIQUE_STABLE_PLAYER_CODE:     {unique_obs:,}")
    print(f"  AMBIGUOUS_OR_UNSTABLE:         {ambiguous_obs:,}")
    print(f"  NO_LONGITUDINAL_ANCHOR:         {uncovered_obs:,}")
    print()
    print("No files were written or modified.")
    print("=" * 96)


if __name__ == "__main__":
    main()
