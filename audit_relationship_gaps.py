"""Read-only follow-up audit for relationship gaps in the all-season matrix.

Separates genuinely missing relationships from source-schema unavailability and
inspects the player-match -> player-season identity edge independently.
"""
from __future__ import annotations

from collections import defaultdict

import player_identity_audit
import source_family_adapters as adapters

SEASONS = tuple(player_identity_audit.SEASONS)


def fpl_relationship_status(season: str) -> dict:
    report = player_identity_audit.audit_season(season)
    # The existing audit only indexes FPL rows when name + verified team + player
    # code are available. Therefore zero candidates can mean source-schema
    # unavailability rather than zero players.
    rows = list(player_identity_audit.player_research._load_season_rows(season))
    team_present = 0
    player_code_present = 0
    complete_for_identity = 0
    for row in rows:
        club = player_identity_audit.player_research._row_club(row)
        team_code = str(row.get("team_code") or "").strip()
        player_code = player_identity_audit.player_research.seasonal_player_id(row)
        if club or team_code:
            team_present += 1
        if player_code:
            player_code_present += 1
        if (club or team_code) and player_code:
            complete_for_identity += 1

    if not complete_for_identity:
        status = "UNAVAILABLE_SOURCE_CONTEXT"
    elif report["exact"]:
        status = "PARTIALLY_RESOLVED"
    else:
        status = "AVAILABLE_BUT_UNRESOLVED"

    return {
        "fpl_rows": len(rows),
        "team_context_rows": team_present,
        "player_code_rows": player_code_present,
        "identity_ready_rows": complete_for_identity,
        "exact": len(report["exact"]),
        "missing": len(report["missing"]),
        "ambiguous": len(report["ambiguous"]),
        "status": status,
    }


def player_source_overlap(season: str) -> dict:
    match_ids = defaultdict(set)
    season_ids = defaultdict(set)

    for row in adapters.player_match_source_rows_for_season(season):
        pid = str(row.get("playerId") or row.get("pl_code") or row.get("player_id") or "").strip()
        if pid:
            match_ids[pid].add(str(row.get("playerName") or "").strip())

    for row in adapters.player_season_source_rows(season):
        pid = str(row.get("playerId") or "").strip()
        if pid:
            season_ids[pid].add(str(row.get("playerName") or row.get("player_name") or "").strip())

    overlap = set(match_ids) & set(season_ids)
    return {
        "player_match_ids": len(match_ids),
        "player_season_ids": len(season_ids),
        "overlap": len(overlap),
        "match_only": len(set(match_ids) - set(season_ids)),
        "season_only": len(set(season_ids) - set(match_ids)),
        "overlap_name_mismatch": sum(bool(match_ids[i] - season_ids[i]) for i in overlap),
        "overlap_sample": sorted(overlap)[:10],
    }


def fixture_gap(season: str) -> dict:
    fixtures = adapters.season_fixtures(season)
    missing = []
    for fixture in fixtures:
        fid = str(fixture.get("fixture_id") or "").strip()
        try:
            adapters.resolve_source_match(season, fid)
        except ValueError:
            missing.append((fid, fixture.get("home_team"), fixture.get("away_team")))
    return {
        "canonical": len(fixtures),
        "missing": missing,
    }


def run() -> dict:
    return {
        season: {
            "fpl": fpl_relationship_status(season),
            "player_source": player_source_overlap(season),
            "fixture": fixture_gap(season),
        }
        for season in SEASONS
    }


def print_report(results: dict) -> None:
    print("=" * 112)
    print("FRL RELATIONSHIP GAP CLASSIFICATION AUDIT")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 112)
    print()
    for season, result in results.items():
        f = result["fpl"]
        o = result["player_source"]
        g = result["fixture"]
        print(
            f"{season}: FPL status={f['status']} | "
            f"FPL rows={f['fpl_rows']} team-context={f['team_context_rows']} "
            f"identity-ready={f['identity_ready_rows']} exact={f['exact']} "
            f"missing={f['missing']} ambiguous={f['ambiguous']}"
        )
        print(
            f"         player-match/player-season IDs: "
            f"{o['player_match_ids']} / {o['player_season_ids']} | "
            f"overlap={o['overlap']} | match-only={o['match_only']} | season-only={o['season_only']} "
            f"| overlap-name-mismatch={o['overlap_name_mismatch']}"
        )
        if g["missing"]:
            print(f"         fixture-source gaps: {g['missing'][:10]}")
        print()
    print("Interpretation: source-schema unavailability is distinct from unresolved identity.")
    print("No files were written or modified.")
    print("=" * 112)


if __name__ == "__main__":
    print_report(run())
