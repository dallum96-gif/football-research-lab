"""Read-only all-season relationship integrity audit for the FRL source families.

This audit is deliberately broader than any one source/schema anomaly. It reports,
for every available season:

- canonical fixture -> source match resolution
- canonical team-season -> source team coverage
- FPL -> source player-match identity classification
- source player-match ID -> player-season ID overlap
- source field availability by family

Nothing is promoted into canonical identity and nothing is written to data files.
Identity classes are evidence-driven: exact, missing, ambiguous, or unavailable.
"""
from __future__ import annotations

from collections import defaultdict

import player_identity_audit
import query_lab
import source_family_adapters as adapters


SEASONS = tuple(player_identity_audit.SEASONS)


def team_registry_by_season():
    rows = query_lab.load_identity_registry()
    out = defaultdict(list)
    for row in rows:
        season = str(row.get("season") or "").strip()
        if season:
            out[season].append(row)
    return out


def fixture_relationship(season: str) -> dict:
    fixtures = adapters.season_fixtures(season)
    resolved = 0
    missing = 0
    source_ids = set()
    for fixture in fixtures:
        fid = str(fixture.get("fixture_id") or "").strip()
        try:
            result = adapters.resolve_source_match(season, fid)
        except ValueError:
            missing += 1
            continue
        resolved += 1
        source_ids.add(result["source_match_id"])
    return {
        "canonical_fixtures": len(fixtures),
        "resolved_source_matches": resolved,
        "missing_source_matches": missing,
        "unique_source_match_ids": len(source_ids),
    }


def team_relationship(season: str, registry: dict) -> dict:
    rows = registry.get(season, [])
    verified = [r for r in rows if r.get("mapping_status") == "VERIFIED"]
    persistent = {str(r.get("persistent_team_code") or "").strip() for r in verified if r.get("persistent_team_code")}

    source_team_ids = set()
    root = adapters.PL_ROOT
    # The source team-match adapter exposes the season's source rows without
    # requiring a canonical fixture lookup for this coverage audit.
    expected = f"{season}_events_stats.csv"
    for club_dir in root.iterdir():
        if not club_dir.is_dir() or club_dir.name.startswith("_"):
            continue
        path = club_dir / "events_stats" / expected
        if not path.is_file():
            continue
        rows_data, _ = adapters._read_csv(path)
        for row in rows_data:
            tid = str(row.get("team_id") or "").strip()
            if tid:
                source_team_ids.add(tid)

    return {
        "registry_rows": len(rows),
        "verified_team_rows": len(verified),
        "verified_persistent_team_codes": len(persistent),
        "source_team_ids": len(source_team_ids),
        "verified_codes_present_in_source": len(persistent & source_team_ids),
        "verified_codes_missing_from_source": len(persistent - source_team_ids),
    }


def player_relationship(season: str) -> dict:
    report = player_identity_audit.audit_season(season)
    return {
        "fpl_candidates": report["fpl_candidates"],
        "source_player_candidates": report["source_candidates"],
        "exact_1_to_1": len(report["exact"]),
        "missing": len(report["missing"]),
        "ambiguous": len(report["ambiguous"]),
    }


def player_source_overlap(season: str) -> dict:
    player_match_ids = set()
    for row in adapters.player_match_source_rows_for_season(season):
        pid = str(row.get("playerId") or row.get("pl_code") or row.get("player_id") or "").strip()
        if pid:
            player_match_ids.add(pid)

    player_season_ids = set()
    for row in adapters.player_season_source_rows(season):
        pid = str(row.get("playerId") or "").strip()
        if pid:
            player_season_ids.add(pid)

    return {
        "player_match_source_ids": len(player_match_ids),
        "player_season_source_ids": len(player_season_ids),
        "direct_id_overlap": len(player_match_ids & player_season_ids),
        "player_match_only": len(player_match_ids - player_season_ids),
        "player_season_only": len(player_season_ids - player_match_ids),
    }


def field_availability(season: str) -> dict:
    inventory = adapters.source_field_inventory(season)
    return {family: len(fields) for family, fields in inventory.items()}


def run():
    registry = team_registry_by_season()
    results = {}
    for season in SEASONS:
        results[season] = {
            "fixtures": fixture_relationship(season),
            "teams": team_relationship(season, registry),
            "players": player_relationship(season),
            "player_source_overlap": player_source_overlap(season),
            "field_counts": field_availability(season),
        }
    return results


def print_report(results: dict) -> None:
    print("=" * 120)
    print("FRL ALL-SEASON RELATIONSHIP INTEGRITY MATRIX")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 120)
    print()
    print(
        "season     fixtures resolved/missing   teams verified/source   "
        "players exact/missing/ambig   player-id overlap   fields team/player/player-season"
    )
    print("-" * 120)
    for season, r in results.items():
        f = r["fixtures"]
        t = r["teams"]
        p = r["players"]
        o = r["player_source_overlap"]
        c = r["field_counts"]
        print(
            f"{season}  "
            f"{f['resolved_source_matches']:4}/{f['missing_source_matches']:<4}               "
            f"{t['verified_team_rows']:3}/{t['source_team_ids']:<3}               "
            f"{p['exact_1_to_1']:4}/{p['missing']:<4}/{p['ambiguous']:<3}              "
            f"{o['direct_id_overlap']:4}/{o['player_match_only']:<3}/{o['player_season_only']:<3}       "
            f"{c['fixture_team_match']:3}/{c['player_match']:3}/{c['player_season']:3}"
        )

    print()
    print("RELATIONSHIP INTERPRETATION")
    print("- Exact 1:1 player matches are evidence-backed only.")
    print("- Missing and ambiguous relationships remain unresolved; they are not promoted.")
    print("- Field-count differences are source availability/schema differences, not identity failures.")
    print("- Direct player ID overlap is reported independently from FPL identity resolution.")
    print()
    print("No files were written or modified.")
    print("=" * 120)


if __name__ == "__main__":
    print_report(run())
