from __future__ import annotations

from collections import defaultdict

from player_identity_crosswalk import summarize
from source_family_adapters import player_match_source_rows_for_season
from player_identity_audit import SEASONS


def main():
    report = summarize()
    verified = defaultdict(set)
    candidate = defaultdict(set)
    for row in report["confirmed"]:
        key = (row["season"], row["source_player_id"])
        if row.get("status") == "VERIFIED_CANDIDATE":
            candidate[key].add(row["element"])
    # Existing later-season registry is represented separately by the source
    # identity registry consumed elsewhere; this audit keeps crosswalk status
    # explicit and does not promote candidates.

    print("=" * 104)
    print("FRL EXISTING PLAYER CROSSWALK -> PLAYER-MATCH COVERAGE AUDIT")
    print("=" * 104)
    print("Existing player_identity_crosswalk machinery only; no promotion.")
    print()

    total = 0
    candidate_obs = 0
    ambiguous_obs = 0
    uncovered_obs = 0

    for season in SEASONS:
        rows = player_match_source_rows_for_season(season)
        total += len(rows)
        covered_ids = {sid for (s, sid) in candidate if s == season}
        ambiguous_ids = set()
        for item in report["review"]:
            if item["season"] == season:
                ambiguous_ids.add(item["source_player_id"])

        c = 0
        a = 0
        u = 0
        for row in rows:
            sid = str(row.get("playerId") or row.get("player_id") or row.get("pl_code") or "").strip()
            if sid in covered_ids:
                c += 1
            elif sid in ambiguous_ids:
                a += 1
            else:
                u += 1
        candidate_obs += c
        ambiguous_obs += a
        uncovered_obs += u
        print(f"{season}: candidate_crosswalk_obs={c:,} ambiguous_crosswalk_obs={a:,} uncovered={u:,}")

    print()
    print("TOTAL")
    print(f"  Player-match observations: {total:,}")
    print(f"  Existing crosswalk candidate observations: {candidate_obs:,}")
    print(f"  Existing crosswalk ambiguous observations:  {ambiguous_obs:,}")
    print(f"  No existing crosswalk route:                {uncovered_obs:,}")
    print(f"  Crosswalk candidate rows: {report['candidate_rows']:,}")
    print(f"  Crosswalk confirmed rows: {report['confirmed_rows']:,}")
    print(f"  Crosswalk review rows:    {report['review_rows']:,}")
    print()
    print("No files were written or modified.")
    print("=" * 104)


if __name__ == "__main__":
    main()
