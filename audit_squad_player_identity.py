"""Read-only audit of squad source-player IDs against the verified FRL player crosswalk.

This does not promote identities or mutate canonical data. It measures which
squad playerId values are already backed by the existing verified
FPL-element -> source-player identity pathway and flags source-level conflicts.
"""
from __future__ import annotations

from collections import defaultdict

from player_identity_crosswalk import SEASONS, source_records
from player_metadata_source import source_rows as squad_source_rows
from player_identity_registry import build_registry


def build_audit() -> dict:
    verified_registry = build_registry()
    verified_by_season = defaultdict(set)
    for row in verified_registry:
        verified_by_season[row["season"]].add(str(row["source_player_id"]).strip())

    squad_seen = defaultdict(list)
    for season in SEASONS:
        for row in squad_source_rows(season):
            sid = str(row.get("playerId") or "").strip()
            if not sid:
                continue
            squad_seen[(season, sid)].append(row)

    verified = []
    unmatched = []
    conflicts = []

    for (season, sid), rows in sorted(squad_seen.items()):
        names = {str(row.get("displayName") or "").strip() for row in rows if row.get("displayName")}
        clubs = {str(row.get("team") or row.get("team_name") or "").strip() for row in rows if row.get("team") or row.get("team_name")}
        if len(names) > 1 or len(clubs) > 1:
            conflicts.append({
                "season": season,
                "source_player_id": sid,
                "names": sorted(names),
                "clubs": sorted(clubs),
            })
        if sid in verified_by_season[season]:
            verified.append((season, sid))
        else:
            unmatched.append((season, sid))

    return {
        "squad_source_player_rows": len(squad_seen),
        "verified_source_player_rows": len(verified),
        "unmatched_source_player_rows": len(unmatched),
        "source_conflicts": len(conflicts),
        "verified": verified,
        "unmatched": unmatched,
        "conflicts": conflicts,
    }


def print_report(report: dict) -> None:
    print("=" * 96)
    print("FRL SQUAD SOURCE-PLAYER IDENTITY AUDIT")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 96)
    print(f"Distinct season/source-player rows: {report['squad_source_player_rows']:,}")
    print(f"Already verified through FRL crosswalk: {report['verified_source_player_rows']:,}")
    print(f"Not currently verified through crosswalk: {report['unmatched_source_player_rows']:,}")
    print(f"Source-level squad conflicts: {report['source_conflicts']:,}")
    if report["conflicts"]:
        print("\nCONFLICT SAMPLE:")
        for row in report["conflicts"][:20]:
            print(f"  {row['season']} | source={row['source_player_id']} | names={row['names']} | clubs={row['clubs']}")
    print("\nNo files were written or modified.")
    print("=" * 96)


if __name__ == "__main__":
    print_report(build_audit())
