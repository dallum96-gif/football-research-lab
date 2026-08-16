"""Read-only cross-season FPL <-> player-match identity audit.

Uses only deterministic season-level name+verified-team matches as anchors.
No new identity is written and no fuzzy match is promoted automatically.
"""

from __future__ import annotations

from collections import defaultdict

import player_identity_audit


SEASONS = player_identity_audit.SEASONS


def build_anchor_maps(report: dict):
    source_to_fpl_names = defaultdict(set)
    source_to_teams = defaultdict(set)
    fpl_to_source = defaultdict(set)

    for season, result in report["seasons"].items():
        for item in result["exact"]:
            source_id = item["source_player_id"]
            source_to_fpl_names[source_id].add(
                player_identity_audit.normalize_name(item["fpl_name"])
            )
            source_to_teams[source_id].add(item["team_code"])
            fpl_to_source[
                (season, item["fpl_player_code"])
            ].add(source_id)

    return source_to_fpl_names, source_to_teams, fpl_to_source


def audit_crossseason(report: dict) -> dict:
    source_to_fpl_names, source_to_teams, _ = build_anchor_maps(report)

    crossseason = []
    alias_candidates = []
    unresolved = []

    anchored_source_ids = set(source_to_fpl_names)

    for season, result in report["seasons"].items():
        for item in result["missing"]:
            name = item["name"]
            team_code = item["team_code"]
            same_team_source_ids = []

            # Find source IDs already proven for another season on this team.
            for source_id in anchored_source_ids:
                if team_code in source_to_teams[source_id]:
                    names = source_to_fpl_names[source_id]
                    # Exact normalized-name evidence is already handled by
                    # the season audit. Here we are specifically looking for
                    # different historical name forms on the same anchored ID.
                    if name not in names:
                        same_team_source_ids.append(
                            (source_id, sorted(names))
                        )

            if len(same_team_source_ids) == 1:
                source_id, prior_names = same_team_source_ids[0]
                alias_candidates.append({
                    "season": season,
                    "fpl_name": name,
                    "team_code": team_code,
                    "source_player_id": source_id,
                    "anchored_names": prior_names,
                    "status": "ALIAS_CANDIDATE",
                })
            elif len(same_team_source_ids) > 1:
                unresolved.append({
                    "season": season,
                    "fpl_name": name,
                    "team_code": team_code,
                    "candidate_source_ids": [x[0] for x in same_team_source_ids],
                    "status": "MULTIPLE_ANCHORED_CANDIDATES",
                })
            else:
                unresolved.append({
                    "season": season,
                    "fpl_name": name,
                    "team_code": team_code,
                    "candidate_source_ids": [],
                    "status": "NO_ANCHOR",
                })

        for item in result["exact"]:
            source_id = item["source_player_id"]
            if len(source_to_fpl_names[source_id]) > 1:
                crossseason.append({
                    "source_player_id": source_id,
                    "fpl_names": sorted(source_to_fpl_names[source_id]),
                    "team_codes": sorted(source_to_teams[source_id]),
                    "status": "CROSS_SEASON_NAME_VARIANTS",
                })

    # Deduplicate repeated cross-season summaries.
    unique = {}
    for row in crossseason:
        unique[row["source_player_id"]] = row

    return {
        "anchored_source_ids": len(anchored_source_ids),
        "alias_candidates": alias_candidates,
        "unresolved": unresolved,
        "crossseason_name_variants": list(unique.values()),
    }


def print_report(report: dict) -> None:
    result = audit_crossseason(report)

    print("=" * 96)
    print("FRL / FPL <-> PLAYER-MATCH CROSS-SEASON IDENTITY AUDIT")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 96)
    print()
    print(f"Anchored source player IDs: {result['anchored_source_ids']:,}")
    print(f"Alias candidates:            {len(result['alias_candidates']):,}")
    print(f"Unresolved:                  {len(result['unresolved']):,}")
    print(f"Cross-season name variants:  {len(result['crossseason_name_variants']):,}")
    print()

    if result["alias_candidates"]:
        print("ALIAS CANDIDATES SAMPLE:")
        for row in result["alias_candidates"][:25]:
            print(
                f"  {row['season']} | {row['fpl_name']} | team={row['team_code']} "
                f"-> source={row['source_player_id']} | prior={row['anchored_names']}"
            )
        print()

    if result["crossseason_name_variants"]:
        print("PROVEN SOURCE-ID NAME VARIANTS SAMPLE:")
        for row in result["crossseason_name_variants"][:25]:
            print(
                f"  source={row['source_player_id']} | "
                f"names={row['fpl_names']} | teams={row['team_codes']}"
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
    base = player_identity_audit.run_audit()
    print_report(base)
