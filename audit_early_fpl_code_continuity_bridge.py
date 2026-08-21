"""Read-only audit of early FPL element continuity into PL player identity.

Uses only FPL element -> source-player mappings already proven in later seasons.
For early seasons, it checks whether the same FPL element identifies exactly one
player-season source player. It never writes or promotes canonical identity.
"""
from __future__ import annotations

from collections import defaultdict
import player_identity_audit
import player_research

EARLY = ("2016-17", "2017-18", "2018-19", "2019-20")


def distinct_fpl(season):
    out = {}
    for row in player_research._load_season_rows(season):
        element = str(row.get("element") or "").strip()
        if element:
            out.setdefault(element, row)
    return out


def direct_anchor_map():
    report = player_identity_audit.run_audit()
    anchors = defaultdict(set)
    for season, result in report["seasons"].items():
        for item in result["exact"]:
            code = str(item.get("fpl_player_code") or "").strip()
            source = str(item.get("source_player_id") or "").strip()
            if code and source:
                anchors[code].add(source)
    return anchors


def player_season_ids(season):
    ids = defaultdict(set)
    for row in player_season_rows(season):
        pid = str(row.get("playerId") or "").strip()
        if pid:
            ids[pid].add(row.get("playerName", ""))
    return ids


def player_season_rows(season):
    return player_research.query_lab.load_player_season_rows(season) if hasattr(player_research.query_lab, "load_player_season_rows") else []


def source_ids_for_early_season(season):
    # Reuse the repository's verified PL source-player index directly.
    return {
        pid
        for values in player_identity_audit.source_player_index(season).values()
        for pid, _name in values
    }


def run():
    anchors = direct_anchor_map()
    print("=" * 96)
    print("FRL EARLY FPL ELEMENT CONTINUITY BRIDGE AUDIT")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 96)
    print(f"Later-season proven FPL element -> source IDs: {len(anchors):,}")

    totals = {"fpl": 0, "anchor": 0, "source_present": 0, "confirmed": 0, "ambiguous_anchor": 0}
    for season in EARLY:
        fpl = distinct_fpl(season)
        source_ids = source_ids_for_early_season(season)
        anchored = 0
        confirmed = 0
        ambiguous = 0
        for element in fpl:
            ids = anchors.get(element, set())
            if ids:
                anchored += 1
                if len(ids) == 1:
                    source_id = next(iter(ids))
                    if source_id in source_ids:
                        confirmed += 1
                else:
                    ambiguous += 1
        totals["fpl"] += len(fpl)
        totals["anchor"] += anchored
        totals["source_present"] += confirmed
        totals["confirmed"] += confirmed
        totals["ambiguous_anchor"] += ambiguous
        print(f"{season}: FPL identities={len(fpl):,} element anchors={anchored:,} source-present={confirmed:,} ambiguous-anchor={ambiguous:,}")

    print("\nTOTALS:")
    print(f"  Early FPL identities:           {totals['fpl']:,}")
    print(f"  Elements proven elsewhere:      {totals['anchor']:,}")
    print(f"  Anchor source ID present early: {totals['source_present']:,}")
    print(f"  Ambiguous continuity anchors:   {totals['ambiguous_anchor']:,}")
    print("\nNo files were written or modified.")
    print("=" * 96)

if __name__ == "__main__":
    run()
