"""Read-only diagnostic of FPL team-context coverage by season.

This does not modify identity data. It distinguishes raw source fields from
Player Research's derived _club context and reports the seasons responsible
for missing team evidence.
"""
from __future__ import annotations

from collections import Counter, defaultdict

import player_research
from player_identity_crosswalk import SEASONS


def audit() -> dict:
    rows = []
    for season in SEASONS:
        season_rows = list(player_research._load_season_rows(season))
        rows.append({
            "season": season,
            "rows": len(season_rows),
            "team": sum(bool(str(r.get("team") or "").strip()) for r in season_rows),
            "team_code": sum(bool(str(r.get("team_code") or "").strip()) for r in season_rows),
            "club": sum(bool(str(r.get("_club") or "").strip()) for r in season_rows),
            "all_blank": sum(not any(str(r.get(k) or "").strip() for k in ("team", "team_code", "_club")) for r in season_rows),
        })
    return {"seasons": rows}


def print_report(report: dict) -> None:
    print("=" * 96)
    print("FRL FPL TEAM-CONTEXT COVERAGE BY SEASON")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 96)
    print("season     rows   team  team_code   _club  all_blank")
    for row in report["seasons"]:
        print(f"{row['season']:9} {row['rows']:6} {row['team']:6} {row['team_code']:10} {row['club']:7} {row['all_blank']:10}")
    print("\nNo files were written or modified.")
    print("=" * 96)


if __name__ == "__main__":
    print_report(audit())
