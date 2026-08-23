from __future__ import annotations

from collections import Counter

from player_match_stats import available_seasons
from source_family_adapters import player_match_source_rows_for_season, player_season_source_rows


def source_id(row):
    return str(row.get("playerId") or row.get("pl_code") or row.get("player_id") or "").strip()


def main() -> None:
    print("=" * 104)
    print("FRL SOURCE PLAYER -> PLAYER-SEASON IDENTITY BRIDGE AUDIT")
    print("=" * 104)
    print("Existing source_player_identity_to_player_season contract only; no promotion.")
    print()

    total_obs = 0
    total_ids = 0
    totals = Counter()

    for season in available_seasons():
        match_rows = player_match_source_rows_for_season(season)
        observed = Counter(source_id(row) for row in match_rows if source_id(row))
        season_rows = player_season_source_rows(season)

        by_id = Counter(source_id(row) for row in season_rows if source_id(row))

        verified_ids = {sid for sid, count in by_id.items() if count == 1}
        ambiguous_ids = {sid for sid, count in by_id.items() if count > 1}
        observed_ids = set(observed)

        verified_observation_count = sum(
            observed[sid] for sid in observed_ids if sid in verified_ids
        )
        ambiguous_observation_count = sum(
            observed[sid] for sid in observed_ids if sid in ambiguous_ids
        )
        unresolved_observation_count = sum(
            observed[sid]
            for sid in observed_ids
            if sid not in verified_ids and sid not in ambiguous_ids
        )

        verified_id_count = len(observed_ids & verified_ids)
        ambiguous_id_count = len(observed_ids & ambiguous_ids)
        unresolved_id_count = len(observed_ids - verified_ids - ambiguous_ids)

        total_obs += sum(observed.values())
        total_ids += len(observed_ids)
        totals.update(
            {
                "verified_ids": verified_id_count,
                "ambiguous_ids": ambiguous_id_count,
                "unresolved_ids": unresolved_id_count,
                "verified_obs": verified_observation_count,
                "ambiguous_obs": ambiguous_observation_count,
                "unresolved_obs": unresolved_observation_count,
            }
        )

        print(
            f"{season}: observations={sum(observed.values()):,} "
            f"source_player_ids={len(observed_ids):,} "
            f"verified_ids={verified_id_count:,} "
            f"ambiguous_ids={ambiguous_id_count:,} "
            f"unresolved_ids={unresolved_id_count:,} "
            f"verified_observations={verified_observation_count:,}"
        )

    print()
    print("TOTAL")
    print(f"  Player-match observations: {total_obs:,}")
    print(f"  Unique source player IDs scanned: {total_ids:,}")
    print(f"  Source Player -> Player-Season VERIFIED IDs: {totals['verified_ids']:,}")
    print(f"  Source Player -> Player-Season AMBIGUOUS IDs: {totals['ambiguous_ids']:,}")
    print(f"  Source Player -> Player-Season UNRESOLVED IDs: {totals['unresolved_ids']:,}")
    print(f"  Observations with verified Player-Season: {totals['verified_obs']:,}")
    print(f"  Observations with ambiguous Player-Season: {totals['ambiguous_obs']:,}")
    print(f"  Observations without Player-Season route: {totals['unresolved_obs']:,}")
    print()
    print("No files were written or modified.")
    print("=" * 104)


if __name__ == "__main__":
    main()
