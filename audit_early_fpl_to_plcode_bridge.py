"""Read-only audit of early-season FPL element -> PL source pl_code relationship.

No identity promotion or canonical writes. Measures exact key overlap by
season, then checks whether any exact element/pl_code matches are unique and
whether they resolve to the established player-season source namespace.
"""
from __future__ import annotations

import csv
import os
from collections import defaultdict

import player_research
from player_identity_crosswalk import SEASONS
from source_family_adapters import player_season_source_rows

ROOT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
)


def source_rows(path):
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with open(path, "r", encoding=encoding, newline="") as handle:
                yield from csv.DictReader(handle)
            return
        except UnicodeDecodeError:
            continue


def merged_player_path(season: str) -> str:
    return os.path.join(
        ROOT,
        "Premier-League-Stats",
        "pl_stats",
        "_merged",
        "players",
        f"{season}_players_stats.csv",
    )


def audit_season(season: str) -> dict:
    fpl = {}
    for row in player_research._load_season_rows(season):
        element = str(row.get("element") or row.get("player_code") or "").strip()
        if element:
            fpl.setdefault(element, row)

    merged_by_pl_code = defaultdict(set)
    merged_by_player_id = {}
    for row in source_rows(merged_player_path(season)):
        pl_code = str(row.get("pl_code") or "").strip()
        player_id = str(row.get("playerId") or "").strip()
        if pl_code:
            merged_by_pl_code[pl_code].add(player_id)
        if player_id:
            merged_by_player_id[player_id] = row

    ps_ids = {
        str(row.get("playerId") or "").strip()
        for row in player_season_source_rows(season)
        if str(row.get("playerId") or "").strip()
    }

    exact = set(fpl) & set(merged_by_pl_code)
    unique = {e: next(iter(merged_by_pl_code[e])) for e in exact if len(merged_by_pl_code[e]) == 1}
    ambiguous = {e: sorted(merged_by_pl_code[e]) for e in exact if len(merged_by_pl_code[e]) > 1}
    unique_to_ps = {e: pid for e, pid in unique.items() if pid in ps_ids}

    return {
        "season": season,
        "fpl": len(fpl),
        "merged": len(merged_by_player_id),
        "fpl_plcode_overlap": len(exact),
        "unique_exact": len(unique),
        "ambiguous_exact": len(ambiguous),
        "unique_to_player_season": len(unique_to_ps),
        "sample": [
            (
                e,
                unique[e],
                str(fpl[e].get("name") or fpl[e].get("second_name") or ""),
                str(merged_by_player_id[unique[e]].get("playerName") or ""),
            )
            for e in sorted(unique_to_ps)[:15]
        ],
    }


def main():
    print("=" * 96)
    print("FRL EARLY-SEASON FPL ELEMENT -> PL CODE BRIDGE AUDIT")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 96)
    totals = defaultdict(int)
    for season in SEASONS[:4]:
        report = audit_season(season)
        print(f"{season}: FPL={report['fpl']} merged={report['merged']} exact_element_plcode={report['fpl_plcode_overlap']}")
        print(f"  unique={report['unique_exact']} ambiguous={report['ambiguous_exact']} unique+player-season={report['unique_to_player_season']}")
        if report["sample"]:
            print("  sample:")
            for row in report["sample"][:5]:
                print(f"    element={row[0]} -> playerId={row[1]} | FPL={row[2]} | PL={row[3]}")
        totals["fpl"] += report["fpl"]
        totals["merged"] += report["merged"]
        totals["overlap"] += report["fpl_plcode_overlap"]
        totals["unique"] += report["unique_exact"]
        totals["ambiguous"] += report["ambiguous_exact"]
        totals["unique_ps"] += report["unique_to_player_season"]
    print("\nTOTALS:")
    print(f"  FPL identities: {totals['fpl']}")
    print(f"  exact element/pl_code overlap: {totals['overlap']}")
    print(f"  unique exact bridges: {totals['unique']}")
    print(f"  ambiguous exact bridges: {totals['ambiguous']}")
    print(f"  unique bridges resolving to player-season IDs: {totals['unique_ps']}")
    print("\nNo files were written or modified.")
    print("=" * 96)


if __name__ == "__main__":
    main()
