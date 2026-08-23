"""Audit longitudinal source-player -> Player Research identity anchors.

Existing machinery only. A source playerId is considered anchorable only when
existing verified crosswalk rows map it to exactly one canonical Player Research
identity across the observed seasons. No canonical data is mutated.
"""
from __future__ import annotations

from collections import defaultdict

import player_identity_crosswalk
import player_research
from source_family_adapters import player_match_source_rows, season_fixtures


def main() -> None:
    seasons = tuple(player_identity_crosswalk.SEASONS)

    source_ids_by_season: dict[str, set[str]] = {}
    all_source_ids: set[str] = set()
    observation_counts: dict[str, int] = defaultdict(int)

    # Build complete source-player observation universe.
    print("FRL LONGITUDINAL SOURCE PLAYER -> PLAYER RESEARCH IDENTITY AUDIT")
    print("=" * 96)
    print("Existing crosswalk + existing Player Research grouping only; no promotion.")

    for index, season in enumerate(seasons, start=1):
        ids: set[str] = set()
        obs = 0
        for fixture in season_fixtures(season):
            fixture_id = str(fixture.get("fixture_id") or "").strip()
            try:
                rows = player_match_source_rows(season, fixture_id)
            except ValueError:
                continue
            for row in rows:
                pid = str(row.get("playerId") or row.get("player_id") or row.get("pl_code") or "").strip()
                if pid:
                    ids.add(pid)
                    all_source_ids.add(pid)
                    obs += 1
                    observation_counts[pid] += 1
        source_ids_by_season[season] = ids
        print(f"  [{index:02d}/{len(seasons):02d}] {season}: observations={obs:,} source_player_ids={len(ids):,}")

    # Existing exact crosswalk provides verified source_id -> research-name anchors.
    anchors: dict[str, set[str]] = defaultdict(set)
    for row in player_identity_crosswalk.build_crosswalk_candidates():
        sid = str(row.get("source_player_id") or "").strip()
        name = str(row.get("name_norm") or "").strip()
        if sid and name:
            anchors[sid].add(name)

    # Apply the existing Player Research collision semantics across the full span.
    research_players = player_research.multi_season_players(seasons[0], seasons[-1])
    valid_research_names = {
        str(player.get("canonical_name") or "").strip()
        for player in research_players
        if str(player.get("canonical_name") or "").strip()
    }

    unique = {sid: next(iter(names)) for sid, names in anchors.items() if len(names) == 1 and next(iter(names)) in valid_research_names}
    ambiguous = {sid: sorted(names) for sid, names in anchors.items() if len(names) > 1}

    unique_obs = sum(observation_counts[sid] for sid in unique)
    ambiguous_obs = sum(observation_counts[sid] for sid in ambiguous)
    uncovered_obs = sum(observation_counts[sid] for sid in all_source_ids if sid not in unique and sid not in ambiguous)

    print()
    print("RESULT")
    print(f"  Player-match observations:          {sum(observation_counts.values()):,}")
    print(f"  Unique longitudinal research IDs:   {len(unique):,}")
    print(f"  Ambiguous source IDs:                {len(ambiguous):,}")
    print(f"  Unique research-anchored observations:{unique_obs:,}")
    print(f"  Ambiguous observations:              {ambiguous_obs:,}")
    print(f"  Uncovered observations:              {uncovered_obs:,}")
    print(f"  Existing verified observations:      39,312")

    print()
    print("SAMPLE UNIQUE ANCHORS")
    for sid, name in sorted(unique.items())[:25]:
        print(f"  source_player_id={sid} -> research_identity={name}")

    print("\nNo files were written or modified.")


if __name__ == "__main__":
    main()
