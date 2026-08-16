"""Read-only cross-season FPL <-> player-match identity audit.

This layer propagates only identities already proven by the deterministic
season-level audit. It never promotes fuzzy/name-only matches.
"""

from __future__ import annotations

from collections import defaultdict

import player_identity_audit

SEASONS = player_identity_audit.SEASONS


def build_anchor_maps(report: dict):
    """Build proven FPL-code -> source-player-ID continuity anchors."""
    fpl_to_source_ids = defaultdict(set)
    source_to_fpl_codes = defaultdict(set)
    source_to_teams = defaultdict(set)

    for season, result in report["seasons"].items():
        for item in result["exact"]:
            fpl_code = str(item["fpl_player_code"]).strip()
            source_id = str(item["source_player_id"]).strip()
            team_code = str(item["team_code"]).strip()

            if not fpl_code or not source_id:
                continue

            fpl_to_source_ids[fpl_code].add(source_id)
            source_to_fpl_codes[source_id].add(fpl_code)
            if team_code:
                source_to_teams[source_id].add(team_code)

    return fpl_to_source_ids, source_to_fpl_codes, source_to_teams


def _current_source_ids_by_team(report_season: dict):
    """Return source IDs represented in this season keyed by source team."""
    # The base audit already has the deterministic source index available only
    # through its audit function, so rebuild the lightweight current-season
    # source index here using its public audit helpers.
    season = report_season["season"]
    index = player_identity_audit.source_player_index(season)
    by_team = defaultdict(set)
    for (_name, team_code), identities in index.items():
        for source_id, _display in identities:
            by_team[team_code].add(source_id)
    return by_team


def audit_crossseason(report: dict) -> dict:
    """Propagate only identities anchored by the same FPL player code."""
    fpl_to_source_ids, source_to_fpl_codes, source_to_teams = build_anchor_maps(report)

    confirmed = []
    unresolved = []
    crossseason_variants = []

    # Pre-build source IDs present in each current season/team.
    current_source_by_team = {
        season: _current_source_ids_by_team(result)
        for season, result in report["seasons"].items()
    }

    anchored_source_ids = set(source_to_fpl_codes)

    for season, result in report["seasons"].items():
        for item in result["missing"]:
            fpl_ids = [str(x).strip() for x in item.get("fpl_ids", []) if str(x).strip()]
            team_code = str(item["team_code"]).strip()

            candidates = set()
            anchor_evidence = []

            # A source ID is eligible only if the exact FPL player code has
            # already been proven against it in another season.
            for fpl_code in fpl_ids:
                for source_id in fpl_to_source_ids.get(fpl_code, set()):
                    if source_id in current_source_by_team[season].get(team_code, set()):
                        candidates.add(source_id)
                        anchor_evidence.append((fpl_code, source_id))

            if len(candidates) == 1:
                source_id = next(iter(candidates))
                confirmed.append({
                    "season": season,
                    "fpl_name": item["name"],
                    "fpl_player_codes": fpl_ids,
                    "team_code": team_code,
                    "source_player_id": source_id,
                    "evidence": sorted(set(anchor_evidence)),
                    "status": "CROSS_SEASON_CONFIRMED",
                })
            elif len(candidates) > 1:
                unresolved.append({
                    "season": season,
                    "fpl_name": item["name"],
                    "fpl_player_codes": fpl_ids,
                    "team_code": team_code,
                    "candidate_source_ids": sorted(candidates),
                    "status": "MULTIPLE_FPL_ANCHORED_SOURCE_IDS",
                })
            else:
                unresolved.append({
                    "season": season,
                    "fpl_name": item["name"],
                    "fpl_player_codes": fpl_ids,
                    "team_code": team_code,
                    "candidate_source_ids": [],
                    "status": "NO_FPL_CODE_ANCHOR",
                })

    # Identify source IDs that have genuinely different proven FPL codes or
    # names across seasons. Those are review evidence rather than errors.
    for source_id in sorted(anchored_source_ids):
        fpl_codes = sorted(source_to_fpl_codes[source_id])
        if len(fpl_codes) > 1:
            crossseason_variants.append({
                "source_player_id": source_id,
                "fpl_player_codes": fpl_codes,
                "teams": sorted(source_to_teams[source_id]),
                "status": "SOURCE_ID_MULTI_FPL_CODE",
            })

    return {
        "anchored_source_ids": len(anchored_source_ids),
        "confirmed": confirmed,
        "unresolved": unresolved,
        "crossseason_variants": crossseason_variants,
    }


def print_report(report: dict) -> None:
    result = audit_crossseason(report)

    print("=" * 96)
    print("FRL / FPL <-> PLAYER-MATCH CROSS-SEASON IDENTITY AUDIT")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 96)
    print()
    print(f"Anchored source player IDs: {result['anchored_source_ids']:,}")
    print(f"Cross-season confirmed:     {len(result['confirmed']):,}")
    print(f"Unresolved:                 {len(result['unresolved']):,}")
    print(f"Cross-season variants:      {len(result['crossseason_variants']):,}")
    print()

    if result["confirmed"]:
        print("CROSS-SEASON CONFIRMED SAMPLE:")
        for row in result["confirmed"][:25]:
            print(
                f"  {row['season']} | {row['fpl_name']} | team={row['team_code']} "
                f"-> source={row['source_player_id']} | evidence={row['evidence']}"
            )
        print()

    if result["crossseason_variants"]:
        print("SOURCE-ID VARIANTS SAMPLE:")
        for row in result["crossseason_variants"][:25]:
            print(
                f"  source={row['source_player_id']} | "
                f"fpl_codes={row['fpl_player_codes']} | teams={row['teams']}"
            )
        print()

    if result["unresolved"]:
        print("UNRESOLVED SAMPLE:")
        for row in result["unresolved"][:25]:
            print(
                f"  {row['season']} | {row['fpl_name']} | team={row['team_code']} "
                f"| status={row['status']}"
            )

    print()
    print("No files were written or modified.")
    print("=" * 96)


if __name__ == "__main__":
    print_report(player_identity_audit.run_audit())
