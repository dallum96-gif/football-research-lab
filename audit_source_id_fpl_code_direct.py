"""Read-only audit of the documented source playerId == FPL player_code relationship."""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

TARGET_SEASONS = tuple(f"{year}-{str(year + 1)[-2:]}" for year in range(2016, 2026))


def open_csv(path: Path):
    last_error = None
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            handle = path.open("r", encoding=encoding, newline="")
            reader = csv.DictReader(handle)
            _ = reader.fieldnames
            return handle, reader, encoding
        except UnicodeDecodeError as exc:
            last_error = exc
            try:
                handle.close()
            except Exception:
                pass
    raise ValueError(f"Could not decode CSV: {path}") from last_error


def pl_observation_stats(source_root: Path, season: str):
    pl_root = source_root / "pl_stats"
    observed_ids: set[str] = set()
    observations = 0
    name_variants: dict[str, set[str]] = defaultdict(set)
    files = sorted(pl_root.rglob(f"{season}_players_match_stats.csv"))
    for path in files:
        handle, reader, _ = open_csv(path)
        try:
            for row in reader:
                sid = str(row.get("playerId") or row.get("player_id") or row.get("pl_code") or "").strip()
                if not sid:
                    continue
                observations += 1
                observed_ids.add(sid)
                name = str(row.get("playerName") or row.get("player_name") or row.get("name") or "").strip()
                if name:
                    name_variants[sid].add(name)
        finally:
            handle.close()
    return observations, observed_ids, name_variants, files


def fpl_player_codes(source_root: Path, season: str):
    path = source_root / "fpl_scraper" / "fpl_stats" / "_merged" / "players" / f"{season}_all_players_gw.csv"
    codes: set[str] = set()
    names_by_code: dict[str, set[str]] = defaultdict(set)
    if not path.exists():
        return codes, names_by_code, path, None, None

    handle, reader, encoding = open_csv(path)
    try:
        fields = reader.fieldnames or []
        if "player_code" not in fields:
            raise ValueError(f"{path.name}: expected player_code column; got {fields[:20]}")
        for row in reader:
            code = str(row.get("player_code") or "").strip()
            if not code:
                continue
            codes.add(code)
            name = str(row.get("second_name") or row.get("first_name") or row.get("web_name") or row.get("name") or "").strip()
            if name:
                names_by_code[code].add(name)
    finally:
        handle.close()
    return codes, names_by_code, path, encoding, fields


def main() -> None:
    root = Path(__file__).resolve().parent / "source"
    observed_codes: set[str] = set()
    matched_codes: set[str] = set()
    stable_matched_codes: set[str] = set()
    exact_matched_obs = 0
    exact_unmatched_obs = 0
    total_obs = 0

    print("=" * 104)
    print("FRL DIRECT SOURCE PLAYER ID -> SEASONAL FPL PLAYER_CODE AUDIT")
    print("=" * 104)
    print("Upstream-documented numeric relationship only; no promotion.")
    print()

    for season in TARGET_SEASONS:
        observations, source_ids, source_names, source_files = pl_observation_stats(root, season)
        codes, fpl_names, fpl_path, fpl_encoding, fields = fpl_player_codes(root, season)
        matched = source_ids & codes

        season_match_obs = 0
        for path in source_files:
            handle, reader, _ = open_csv(path)
            try:
                for row in reader:
                    sid = str(row.get("playerId") or row.get("player_id") or row.get("pl_code") or "").strip()
                    if sid in matched:
                        season_match_obs += 1
            finally:
                handle.close()

        season_unmatched_obs = observations - season_match_obs
        total_obs += observations
        exact_matched_obs += season_match_obs
        exact_unmatched_obs += season_unmatched_obs
        observed_codes.update(source_ids)
        matched_codes.update(matched)
        stable_matched_codes.update(
            sid for sid in matched
            if len(source_names.get(sid, set())) == 1
            and len(fpl_names.get(sid, set())) == 1
        )

        fpl_status = "MISSING"
        if fpl_path.exists():
            fpl_status = f"rows_with_codes={len(codes):,} encoding={fpl_encoding}"
        print(
            f"{season}: PL_obs={observations:,} PL_ids={len(source_ids):,} "
            f"FPL_status={fpl_status} matched_ids={len(matched):,} "
            f"matched_obs={season_match_obs:,} unmatched_obs={season_unmatched_obs:,}"
        )

    print()
    print("TOTAL")
    print(f"  Player-match observations:             {total_obs:,}")
    print(f"  Matched by same-season player_code:   {exact_matched_obs:,}")
    print(f"  Unmatched observations:               {exact_unmatched_obs:,}")
    print(f"  Unique source player IDs:             {len(observed_codes):,}")
    print(f"  Unique IDs with same-season FPL code: {len(matched_codes):,}")
    print(f"  Stable-name matched IDs:              {len(stable_matched_codes):,}")
    print()
    print("No identities were promoted. No files were written or modified.")
    print("=" * 104)


if __name__ == "__main__":
    main()
