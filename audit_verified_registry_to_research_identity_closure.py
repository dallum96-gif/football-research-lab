"""Audit verified source-player registry -> Player Research identity closure.

Read-only. Uses the existing verified player_identity_registry.csv semantics
and the existing Player Research seasonal identifier/canonical-name machinery.
No new identity matching is performed and no canonical data is written.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import player_research
from source_family_adapters import player_match_source_rows_for_season

ROOT = Path(__file__).resolve().parent
REGISTRY = ROOT / "player_identity_registry.csv"


def load_registry() -> list[dict[str, str]]:
    with REGISTRY.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def research_identity_index() -> dict[tuple[str, str], set[str]]:
    """Map (season, seasonal player key) -> canonical research identity."""
    index: dict[tuple[str, str], set[str]] = defaultdict(set)
    for season in player_research.available_seasons():
        for row in player_research._load_season_rows(season):
            player_key = player_research.seasonal_player_id(row).strip()
            canonical = player_research.canonical_player_name(row).strip()
            if player_key and canonical:
                index[(season, player_key)].add(canonical)
    return index


def observed_source_ids_by_season() -> dict[str, list[str]]:
    observed: dict[str, list[str]] = {}
    for season in player_research.available_seasons():
        rows = player_match_source_rows_for_season(season)
        observed[season] = [
            str(row.get("playerId") or row.get("player_id") or row.get("pl_code") or "").strip()
            for row in rows
            if str(row.get("playerId") or row.get("player_id") or row.get("pl_code") or "").strip()
        ]
    return observed


def closure_maps(registry: list[dict[str, str]], research_index):
    source_to_canonicals: dict[str, set[str]] = defaultdict(set)
    source_to_pairs: dict[str, set[tuple[str, str]]] = defaultdict(set)

    for row in registry:
        if row.get("identity_status") != "VERIFIED":
            continue
        season = str(row.get("season") or "").strip()
        element = str(row.get("fpl_element") or "").strip()
        source_id = str(row.get("source_player_id") or "").strip()
        if not season or not element or not source_id:
            continue

        for canonical in research_index.get((season, element), set()):
            source_to_canonicals[source_id].add(canonical)
            source_to_pairs[source_id].add((season, element))

    return source_to_canonicals, source_to_pairs


def main() -> None:
    registry = load_registry()
    research_index = research_identity_index()
    source_to_canonicals, source_to_pairs = closure_maps(registry, research_index)
    observed_by_season = observed_source_ids_by_season()

    all_source_ids = set(source_id for ids in observed_by_season.values() for source_id in ids)

    unique_ids = {sid for sid in all_source_ids if len(source_to_canonicals.get(sid, set())) == 1}
    ambiguous_ids = {sid for sid in all_source_ids if len(source_to_canonicals.get(sid, set())) > 1}
    uncovered_ids = all_source_ids - unique_ids - ambiguous_ids

    unique_obs = ambiguous_obs = uncovered_obs = 0
    print("=" * 96)
    print("FRL VERIFIED REGISTRY -> PLAYER RESEARCH IDENTITY CLOSURE AUDIT")
    print("=" * 96)
    print("Existing verified player_identity_registry.csv + existing Player Research identity semantics; no promotion.")
    print()

    for season in player_research.available_seasons():
        season_ids = observed_by_season.get(season, [])
        season_unique = sum(1 for sid in season_ids if sid in unique_ids)
        season_ambiguous = sum(1 for sid in season_ids if sid in ambiguous_ids)
        season_uncovered = len(season_ids) - season_unique - season_ambiguous
        unique_obs += season_unique
        ambiguous_obs += season_ambiguous
        uncovered_obs += season_uncovered
        print(
            f"{season}: observations={len(season_ids):,} "
            f"unique={season_unique:,} ambiguous={season_ambiguous:,} uncovered={season_uncovered:,}"
        )

    print("=" * 96)
    print("TOTAL")
    print("=" * 96)
    print(f"Verified registry rows:            {len(registry):,}")
    print(f"Observed source player IDs:         {len(all_source_ids):,}")
    print(f"  UNIQUE_RESEARCH_IDENTITY:          {len(unique_ids):,}")
    print(f"  AMBIGUOUS_RESEARCH_IDENTITY:       {len(ambiguous_ids):,}")
    print(f"  NO_RESEARCH_IDENTITY:              {len(uncovered_ids):,}")
    print()
    print(f"Player-match observations:           {sum(len(v) for v in observed_by_season.values()):,}")
    print(f"  UNIQUE_RESEARCH_IDENTITY:          {unique_obs:,}")
    print(f"  AMBIGUOUS_RESEARCH_IDENTITY:       {ambiguous_obs:,}")
    print(f"  NO_RESEARCH_IDENTITY:              {uncovered_obs:,}")
    print()

    samples = sorted(unique_ids)[:20]
    if samples:
        print("UNIQUE SAMPLE:")
        for sid in samples:
            print(
                f"  source={sid} -> canonical={sorted(source_to_canonicals[sid])} "
                f"pairs={sorted(source_to_pairs[sid])}"
            )
    print()
    print("No files were written or modified.")
    print("=" * 96)


if __name__ == "__main__":
    main()
