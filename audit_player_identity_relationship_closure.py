"""Read-only closure audit for the existing FRL player identity routes.

This audit does not invent a new identity method and does not mutate the
canonical registry. It measures how much of the 2016-17 to 2025-26
player-match source population is covered by the repository's existing
identity machinery:

- 2016-17..2019-20: existing FPL element -> pl_code -> source playerId audit
  route, reported as CANDIDATE_ONLY unless separately promoted;
- 2020-21..2025-26: existing verified player_identity_registry route.

The purpose is to identify the true remaining identity frontier before any
promotion or materialisation change is attempted.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
from pathlib import Path

import player_identity_audit
import player_research
from player_identity_registry import build_registry
from source_family_adapters import player_match_source_rows_for_season

ROOT = Path(__file__).resolve().parent
PL_ROOT = Path(player_identity_audit.PL_ROOT)
MERGED_PLAYERS = PL_ROOT / "_merged" / "players"
SEASONS = tuple(player_identity_audit.SEASONS)
EARLY = SEASONS[:4]
LATER = SEASONS[4:]


def _n(value: object) -> str:
    return str(value or "").strip()


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _distinct_fpl_elements(season: str) -> set[str]:
    return {
        _n(row.get("element") or row.get("player_code"))
        for row in player_research._load_season_rows(season)
        if _n(row.get("element") or row.get("player_code"))
    }


def _early_plcode_map(season: str) -> tuple[dict[str, set[str]], dict[str, dict]]:
    """Return FPL element -> source playerId candidates from the existing bridge.

    The map reproduces the existing audit's exact mechanism: the season-local
    FPL ``element`` is compared to the merged players source ``pl_code``, and
    each ``pl_code`` points to one or more source ``playerId`` values.
    """
    path = MERGED_PLAYERS / f"{season}_players_stats.csv"
    rows = _load_csv(path)
    by_pl_code: dict[str, set[str]] = defaultdict(set)
    by_source: dict[str, dict] = {}
    for row in rows:
        source_id = _n(row.get("playerId"))
        pl_code = _n(row.get("pl_code"))
        if source_id and pl_code:
            by_pl_code[pl_code].add(source_id)
            by_source[source_id] = row
    return by_pl_code, by_source


def _verified_registry_map() -> dict[tuple[str, str], set[str]]:
    out: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in build_registry():
        if _n(row.get("identity_status")) != "VERIFIED":
            continue
        season = _n(row.get("season"))
        element = _n(row.get("fpl_element"))
        source_id = _n(row.get("source_player_id"))
        if season and element and source_id:
            out[(season, element)].add(source_id)
    return out


def _source_player_ids_and_observations(season: str) -> tuple[set[str], int]:
    """Count unique source IDs and player-match observations for one season."""
    rows = player_match_source_rows_for_season(season)
    ids = {
        _n(row.get("playerId") or row.get("player_id") or row.get("pl_code"))
        for row in rows
        if _n(row.get("playerId") or row.get("player_id") or row.get("pl_code"))
    }
    return ids, len(rows)


def main() -> None:
    registry = _verified_registry_map()

    print("=" * 104)
    print("FRL PLAYER IDENTITY RELATIONSHIP CLOSURE AUDIT")
    print("=" * 104)
    print("Existing identity machinery only; no identity promotion and no canonical mutation.")
    print()

    total_observations = 0
    total_source_ids = set()
    verified_observations = 0
    candidate_only_observations = 0
    uncovered_observations = 0
    ambiguous_observations = 0

    for season in SEASONS:
        source_ids, observations = _source_player_ids_and_observations(season)
        total_observations += observations
        total_source_ids.update(source_ids)

        if season in EARLY:
            pl_map, _ = _early_plcode_map(season)
            fpl_elements = _distinct_fpl_elements(season)
            unique_element_to_source: dict[str, str] = {}
            ambiguous_elements = set()
            for element in fpl_elements:
                candidates = pl_map.get(element, set())
                if len(candidates) == 1:
                    unique_element_to_source[element] = next(iter(candidates))
                elif len(candidates) > 1:
                    ambiguous_elements.add(element)

            covered_ids = set(unique_element_to_source.values())
            candidate_only = source_ids & covered_ids
            ambiguous_ids = set()
            for element in ambiguous_elements:
                ambiguous_ids.update(pl_map.get(element, set()))
            ambiguous_ids &= source_ids

            verified_count = 0
            print(f"{season}")
            print(f"  route: CANDIDATE_ONLY_EARLY_PLCODE")
            print(f"  FPL season elements: {len(fpl_elements):,}")
            print(f"  source player IDs:   {len(source_ids):,}")
            print(f"  player-match rows:   {observations:,}")
            print(f"  unique element->source candidates: {len(unique_element_to_source):,}")
            print(f"  candidate-covered source IDs:       {len(candidate_only):,}")
            print(f"  ambiguous source IDs:               {len(ambiguous_ids):,}")
            print(f"  uncovered source IDs:               {len(source_ids - candidate_only):,}")
            print()

            candidate_only_observations += sum(
                1
                for row in player_match_source_rows_for_season(season)
                if _n(row.get("playerId") or row.get("player_id") or row.get("pl_code")) in candidate_only
            )
            ambiguous_observations += sum(
                1
                for row in player_match_source_rows_for_season(season)
                if _n(row.get("playerId") or row.get("player_id") or row.get("pl_code")) in ambiguous_ids
            )
            uncovered_observations += observations - sum(
                1
                for row in player_match_source_rows_for_season(season)
                if _n(row.get("playerId") or row.get("player_id") or row.get("pl_code")) in candidate_only
            )
        else:
            verified_ids = set().union(
                *(registry.get((season, element), set()) for element in _distinct_fpl_elements(season))
            )
            covered = source_ids & verified_ids
            uncovered = source_ids - covered

            print(f"{season}")
            print(f"  route: VERIFIED_REGISTRY")
            print(f"  source player IDs:   {len(source_ids):,}")
            print(f"  player-match rows:   {observations:,}")
            print(f"  verified-covered source IDs: {len(covered):,}")
            print(f"  uncovered source IDs:         {len(uncovered):,}")
            print()

            for row in player_match_source_rows_for_season(season):
                sid = _n(row.get("playerId") or row.get("player_id") or row.get("pl_code"))
                if sid in covered:
                    verified_observations += 1
                else:
                    uncovered_observations += 1

    print("=" * 104)
    print("TOTAL")
    print("=" * 104)
    print(f"Player-match observations:            {total_observations:,}")
    print(f"Unique source player IDs observed:    {len(total_source_ids):,}")
    print(f"Later-season verified observations:  {verified_observations:,}")
    print(f"Early candidate-only observations:   {candidate_only_observations:,}")
    print(f"Observations involving ambiguous IDs: {ambiguous_observations:,}")
    print(f"Observations with no existing route: {uncovered_observations:,}")
    print()
    print("INTERPRETATION")
    print("- Later-season registry coverage is verified and may feed the canonical relationship only where the registry is already verified.")
    print("- Early pl_code coverage is reported as candidate-only because the existing bridge audit itself does not promote it.")
    print("- No names, fuzzy matching, or unproven cross-season continuity are introduced here.")
    print("=" * 104)


if __name__ == "__main__":
    main()
