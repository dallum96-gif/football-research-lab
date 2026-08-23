"""Read-only audit of FPL element -> source playerId conflicts.

This deliberately does not promote or write identity mappings. It recomputes
exact normalized-name + verified-team candidates and reports any season-local
FPL element that has more than one candidate external playerId.
"""
from __future__ import annotations

from collections import defaultdict

import player_identity_crosswalk as cw


def conflict_report():
    candidates = cw.build_crosswalk_candidates()
    grouped = defaultdict(list)
    for row in candidates:
        grouped[(row["season"], row["element"])].append(row)

    conflicts = []
    for (season, element), rows in sorted(grouped.items()):
        source_ids = sorted({row["source_player_id"] for row in rows})
        if len(source_ids) > 1:
            conflicts.append({
                "season": season,
                "fpl_element": element,
                "source_player_ids": source_ids,
                "candidates": rows,
            })
    return conflicts


if __name__ == "__main__":
    conflicts = conflict_report()
    print("=" * 96)
    print("FRL PLAYER IDENTITY CONFLICT AUDIT")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 96)
    print(f"Conflicting FPL elements: {len(conflicts):,}")
    for item in conflicts:
        print(
            f"  {item['season']} | element={item['fpl_element']} | "
            f"source_ids={item['source_player_ids']}"
        )
        for candidate in item["candidates"]:
            print(
                f"    name={candidate['name_norm']} | "
                f"team={candidate['team_code']} | "
                f"source={candidate['source_player_id']}"
            )
    print("No files were written or modified.")
    print("=" * 96)
