"""Read-only audit of the documented source playerId == FPL player_code relationship."""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

TARGET_SEASONS = tuple(f"{year}-{str(year + 1)[-2:]}" for year in range(2016, 2026))


def pl_observation_stats(source_root: Path, season: str):
    pl_root = source_root / "pl_stats"
    observed_ids: set[str] = set()
    observations = 0
    matched_name_variants: dict[str, set[str]] = defaultdict(set)

    for path in sorted(pl_root.rglob(f"{season}_players_match_stats.csv")):
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                sid = str(
                    row.get("playerId") or row.get("player_id") or row.get("pl_code") or ""
                ).strip()
                if not sid:
                    continue
                observations += 1
                observed_ids.add(sid)
                name = str(
                    row.get("playerName") or row.get("player_name") or row.get("name") or ""
                ).strip()
                if name:
                    matched_name_variants[sid].add(name)

    return observations, observed_ids, matched_name_variants


def fpl_player_codes(source_root: Path, season: str):
    path = source_root / "fpl_scraper" / "fpl_stats" / "_merged" / "players" / f"{season}_all_players_gw.csv"
    codes: set[str] = set()
    names_by_code: dict[str, set[str]] = defaultdict(set)
    if not path.exists():
        return codes, names_by_code

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            code = str(row.get("player_code") or "").strip()
            if not code:
                continue
            codes.add(code)
            name = str(
                row.get("second_name")
                or row.get("first_name")
                or row.get("web_name")
                or row.get("name")
                or ""
            ).strip()
            if name:
                names_by_code[code].add(name)
    return codes, names_by_code


def main() -> None:
    root = Path(__file__).resolve().parent / "source"

    total_obs = 0
    matched_obs = 0
    unmatched_obs = 0
    observed_codes: set[str] = set()
    matched_codes: set[str] = set()
    stable_matched_codes: set[str] = set()

    print("=" * 104)
    print("FRL DIRECT SOURCE PLAYER ID -> SEASONAL FPL PLAYER_CODE AUDIT")
    print("=" * 104)
    print("Upstream-documented numeric relationship only; no promotion.")
    print()

    for season in TARGET_SEASONS:
        observations, source_ids, source_names = pl_observation_stats(root, season)
        codes, fpl_names = fpl_player_codes(root, season)

        matched = source_ids & codes
        unmatched = source_ids - codes
        total_obs += observations
        matched_obs += sum(
            1
            for path in sorted((root / "pl_stats").rglob(f"{season}_players_match_stats.csv"))
            for row in csv.DictReader(path.open("r", encoding="utf-8-sig", newline=""))
            if str(row.get("playerId") or row.get("player_id") or row.get("pl_code") or "").strip() in matched
        )
        unmatched_obs += observations - (matched_obs - sum(
            1
            for s in TARGET_SEASONS
            if s != season
        )) if False else 0

        # Re-count only the current season's observation matches/unmatches cleanly.
        season_match_obs = 0
        for path in sorted((root / "pl_stats").rglob(f"{season}_players_match_stats.csv")):
            with path.open("r", encoding="utf-8-sig", newline="") as f:
                for row in csv.DictReader(f):
                    sid = str(row.get("playerId") or row.get("player_id") or row.get("pl_code") or "").strip()
                    if sid in matched:
                        season_match_obs += 1
        season_unmatched_obs = observations - season_match_obs
        # Replace the temporary accumulation above with the exact season values.
        matched_obs -= season_match_obs if False else 0
        # The loop uses exact season counts below; aggregate separately.
        observed_codes.update(source_ids)
        matched_codes.update(matched)
        stable_matched_codes.update(
            sid for sid in matched
            if len(source_names.get(sid, set())) == 1
            and len(fpl_names.get(sid, set())) == 1
        )

        print(
            f"{season}: observations={observations:,} "
            f"source_ids={len(source_ids):,} fpl_codes={len(codes):,} "
            f"matched_ids={len(matched):,} unmatched_ids={len(unmatched):,} "
            f"matched_observations={season_match_obs:,} unmatched_observations={season_unmatched_obs:,}"
        )

        # Rebuild aggregate observation totals accurately after the print.
        if season == TARGET_SEASONS[0]:
            exact_matched_obs = season_match_obs
            exact_unmatched_obs = season_unmatched_obs
        else:
            exact_matched_obs += season_match_obs
            exact_unmatched_obs += season_unmatched_obs

    print()
    print("TOTAL")
    print(f"  Player-match observations:        {total_obs:,}")
    print(f"  Matched by same-season player_code:{exact_matched_obs:,}")
    print(f"  Unmatched observations:            {exact_unmatched_obs:,}")
    print(f"  Unique source player IDs:          {len(observed_codes):,}")
    print(f"  Unique IDs with same-season FPL code:{len(matched_codes):,}")
    print(f"  Stable-name matched IDs:           {len(stable_matched_codes):,}")
    print()
    print("No identities were promoted. No files were written or modified.")
    print("=" * 104)


if __name__ == "__main__":
    main()
