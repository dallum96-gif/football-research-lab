"""Read-only audit of the documented source playerId == FPL player_code relationship."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path


def source_rows_by_season(source_root: Path) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    pl_root = source_root / "pl_stats"
    seasons = []
    for p in sorted(pl_root.rglob("*_players_match_stats.csv")):
        name = p.name
        if name.endswith("_players_match_stats.csv"):
            seasons.append(name[: -len("_players_match_stats.csv")])
    for season in sorted(set(seasons)):
        rows: list[dict] = []
        for path in sorted(pl_root.rglob(f"{season}_players_match_stats.csv")):
            import csv
            with path.open("r", encoding="utf-8-sig", newline="") as f:
                rows.extend(csv.DictReader(f))
        out[season] = rows
    return out


def main() -> None:
    root = Path(__file__).resolve().parent / "source"
    index_path = root / "fpl_scraper" / "fpl_stats" / "_index" / "_players_index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))

    # index key is documented as the same numeric Opta/PulseLive player code.
    code_to_seasons: dict[str, set[str]] = defaultdict(set)
    code_to_names: dict[str, set[str]] = defaultdict(set)
    for code, season_rows in index.items():
        code_s = str(code).strip()
        for season, meta in season_rows.items():
            code_to_seasons[code_s].add(str(season))
            name = str(meta.get("name") or "").strip()
            if name:
                code_to_names[code_s].add(name)

    rows_by_season = source_rows_by_season(root)
    total_obs = 0
    matched_obs = 0
    unmatched_obs = 0
    unique_codes = set()
    match_by_season = Counter()
    unmatched_by_season = Counter()
    details: dict[str, dict] = {}

    for season, rows in rows_by_season.items():
        season_total = 0
        season_match = 0
        for row in rows:
            sid = str(row.get("playerId") or row.get("player_id") or row.get("pl_code") or "").strip()
            if not sid:
                continue
            season_total += 1
            total_obs += 1
            unique_codes.add(sid)
            if sid in code_to_seasons:
                season_match += 1
                matched_obs += 1
            else:
                unmatched_obs += 1
        match_by_season[season] = season_match
        unmatched_by_season[season] = season_total - season_match
        details[season] = {"observations": season_total, "matched": season_match, "unmatched": season_total - season_match}

    matched_codes = {sid for sid in unique_codes if sid in code_to_seasons}
    stable_matched_codes = {
        sid for sid in matched_codes
        if len(code_to_names[sid]) == 1
    }

    print("=" * 104)
    print("FRL DIRECT SOURCE PLAYER ID -> FPL PLAYER_CODE AUDIT")
    print("=" * 104)
    print("Upstream-documented numeric relationship only; no promotion.")
    print()
    for season in sorted(details):
        d = details[season]
        print(f"{season}: observations={d['observations']:,} matched={d['matched']:,} unmatched={d['unmatched']:,}")
    print()
    print("TOTAL")
    print(f"  Player-match observations:        {total_obs:,}")
    print(f"  Matched to FPL player_code:       {matched_obs:,}")
    print(f"  Unmatched:                         {unmatched_obs:,}")
    print(f"  Unique source player IDs:         {len(unique_codes):,}")
    print(f"  Unique IDs found in FPL index:    {len(matched_codes):,}")
    print(f"  Stable-name IDs in FPL index:     {len(stable_matched_codes):,}")
    print()
    print("No identities were promoted. No files were written or modified.")
    print("=" * 104)


if __name__ == "__main__":
    main()
