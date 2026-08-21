"""Read-only audit of early-season PL player source ID relationships."""
from __future__ import annotations
import csv
import os
from collections import defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCE_ROOT = os.path.abspath(os.path.join(ROOT, "..", "Premier-League-Stats", "pl_stats"))
SEASONS = ("2016-17", "2017-18", "2018-19", "2019-20")


def load_csv(path):
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with open(path, newline="", encoding=enc) as f:
                r = csv.DictReader(f)
                return list(r)
        except UnicodeDecodeError:
            continue
    raise ValueError(path)


def season_rows(season):
    merged = os.path.join(SOURCE_ROOT, "_merged", "players", f"{season}_players_stats.csv")
    rows = load_csv(merged)
    return merged, rows


def ps_rows(season):
    # Adapter module is available in the repo/worktree.
    from source_family_adapters import player_season_source_rows
    return player_season_source_rows(season)


def main():
    print("=" * 96)
    print("FRL EARLY-SEASON PL PLAYER SOURCE ID RELATIONSHIP AUDIT")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 96)
    for season in SEASONS:
        path, merged = season_rows(season)
        ps = ps_rows(season)
        mid = {str(r.get("playerId") or "").strip() for r in merged if str(r.get("playerId") or "").strip()}
        pid = {str(r.get("playerId") or "").strip() for r in ps if str(r.get("playerId") or "").strip()}
        overlap = mid & pid
        print(f"{season}: merged={len(mid):,} player-season={len(pid):,} direct-ID-overlap={len(overlap):,}")
        print(f"  merged-only={len(mid-pid):,} player-season-only={len(pid-mid):,}")
        if overlap:
            mismatches = []
            ps_by_id = {str(r.get("playerId") or "").strip(): r for r in ps}
            for r in merged:
                sid = str(r.get("playerId") or "").strip()
                if sid in overlap:
                    a = str(r.get("playerName") or "").strip().casefold()
                    b = str(ps_by_id[sid].get("playerName") or "").strip().casefold()
                    if a != b:
                        mismatches.append((sid, r.get("playerName"), ps_by_id[sid].get("playerName")))
            print(f"  same-ID-name-mismatches={len(mismatches):,}")
            for item in mismatches[:5]:
                print("   ", item)
        print(f"  source={path}")
    print("\nNo files were written or modified.")
    print("=" * 96)

if __name__ == "__main__":
    main()
