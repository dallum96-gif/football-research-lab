from __future__ import annotations

from collections import Counter

from player_match_stats import player_match_source_rows_for_season, available_seasons
from source_family_adapters import source_player_season_identity


def main() -> None:
    print("=" * 96)
    print("FRL SOURCE PLAYER -> PLAYER-SEASON IDENTITY BRIDGE AUDIT")
    print("=" * 96)
    print("Existing source_player_identity_to_player_season contract only; no promotion.")
    print()

    total_obs = 0
    total_ids = 0
    totals = Counter()

    for season in available_seasons():
        rows = player_match_source_rows_for_season(season)
        ids = sorted({str(row.get("playerId") or row.get("pl_code") or "").strip() for row in rows if str(row.get("playerId") or row.get("pl_code") or "").strip()})
        verified = 0
        ambiguous = 0
        unresolved = 0

        for pid in ids:
            result = source_player_season_identity(season, pid)
            decision = str(result.get("relationship_status") or result.get("status") or "UNKNOWN").upper()
            if result.get("verified") is True or "VERIFIED" in decision:
                verified += 1
            elif "AMBIG" in decision:
                ambiguous += 1
            else:
                unresolved += 1

        obs = len(rows)
        total_obs += obs
        total_ids += len(ids)
        totals.update({"verified": verified, "ambiguous": ambiguous, "unresolved": unresolved})

        print(f"{season}: observations={obs:,} source_player_ids={len(ids):,} verified={verified:,} ambiguous={ambiguous:,} unresolved={unresolved:,}")

    print()
    print("TOTAL")
    print(f"  Player-match observations: {total_obs:,}")
    print(f"  Unique source player IDs scanned: {total_ids:,}")
    print(f"  Source Player -> Player-Season VERIFIED: {totals['verified']:,}")
    print(f"  AMBIGUOUS: {totals['ambiguous']:,}")
    print(f"  UNRESOLVED: {totals['unresolved']:,}")
    print()
    print("No files were written or modified.")
    print("=" * 96)


if __name__ == "__main__":
    main()
