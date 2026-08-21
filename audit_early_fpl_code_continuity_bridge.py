"""Read-only audit of early FPL identity recovery via proven FPL-code continuity.

This does not create or promote identities. It asks a narrower question:
can a teamless 2016-20 FPL seasonal player code be traced to a source
playerId already proven elsewhere, and does that source playerId exist in the
same early-season player-season source?

A positive result is evidence for a source-family bridge, not automatic
canonical identity promotion.
"""
from __future__ import annotations

from collections import defaultdict

import player_identity_audit
import player_identity_crossseason_audit
import player_research
from source_family_adapters import player_season_source_rows

SEASONS = tuple(player_identity_audit.SEASONS)
EARLY = SEASONS[:4]


def distinct_fpl_codes(season: str) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for row in player_research._load_season_rows(season):
        code = str(row.get("element") or row.get("player_code") or "").strip()
        if code:
            rows.setdefault(code, row)
    return rows


def confirmed_fpl_to_source() -> dict[str, set[str]]:
    base = player_identity_audit.run_audit()
    fpl_to_source, _source_to_fpl, _source_to_team = (
        player_identity_crossseason_audit.build_anchor_maps(base)
    )
    return {code: set(ids) for code, ids in fpl_to_source.items()}


def early_player_season_ids(season: str) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for row in player_season_source_rows(season):
        pid = str(row.get("playerId") or "").strip()
        if pid:
            rows.setdefault(pid, row)
    return rows


def audit() -> dict:
    anchors = confirmed_fpl_to_source()
    results = []

    totals = defaultdict(int)
    for season in EARLY:
        fpl = distinct_fpl_codes(season)
        ps = early_player_season_ids(season)
        season_result = []

        for code, row in fpl.items():
            source_ids = sorted(anchors.get(code, set()))
            if not source_ids:
                status = "NO_CONTINUITY_ANCHOR"
            elif len(source_ids) > 1:
                status = "MULTIPLE_CONTINUITY_ANCHORS"
            elif source_ids[0] not in ps:
                status = "ANCHOR_NOT_PRESENT_IN_EARLY_PLAYER_SEASON"
            else:
                status = "CONTINUITY_ANCHORED_TO_EARLY_PLAYER_SEASON"

            item = {
                "season": season,
                "fpl_code": code,
                "fpl_name": player_research.display_player_name(row),
                "source_ids": source_ids,
                "early_player_season_name": ps[source_ids[0]].get("playerName") if len(source_ids) == 1 and source_ids[0] in ps else "",
                "status": status,
            }
            season_result.append(item)
            totals[status] += 1

        results.append({"season": season, "rows": season_result})

    return {
        "anchors": sum(len(v) for v in anchors.values()),
        "unique_fpl_codes_with_anchors": len(anchors),
        "totals": dict(totals),
        "seasons": results,
    }


def print_report(report: dict) -> None:
    print("=" * 96)
    print("FRL EARLY-SEASON FPL CODE CONTINUITY BRIDGE AUDIT")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 96)
    print(f"Proven FPL-code -> source-player anchors: {report['anchors']:,}")
    print(f"Unique FPL codes with anchors:             {report['unique_fpl_codes_with_anchors']:,}")
    print()
    for season in report["seasons"]:
        counts = defaultdict(int)
        for row in season["rows"]:
            counts[row["status"]] += 1
        print(season["season"])
        for key, value in sorted(counts.items()):
            print(f"  {key}: {value:,}")

    print("\nCONTINUITY-ANCHORED SAMPLE:")
    shown = 0
    for season in report["seasons"]:
        for row in season["rows"]:
            if row["status"] == "CONTINUITY_ANCHORED_TO_EARLY_PLAYER_SEASON":
                print(
                    f"  {row['season']} | element={row['fpl_code']} | {row['fpl_name']} "
                    f"-> source={row['source_ids'][0]} | player-season={row['early_player_season_name']}"
                )
                shown += 1
                if shown >= 25:
                    break
        if shown >= 25:
            break

    print("\nNo files were written or modified.")
    print("=" * 96)


if __name__ == "__main__":
    print_report(audit())
