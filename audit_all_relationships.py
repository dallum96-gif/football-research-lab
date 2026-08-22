"""Read-only all-season relationship integrity audit for the FRL source families.

The matrix reports the relationship state at the same contract boundary used by
production adapters. It keeps identity, observation, and source availability
separate and never promotes an inferred join.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import player_identity_audit
import query_lab
import source_family_adapters as adapters
from player_match_stats import source_player_id
from player_relationship_adapters import resolve_fpl_player_identity


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
    persistent = {
        str(r.get("persistent_team_code") or "").strip()
        for r in verified
        if r.get("persistent_team_code")
    }

    source_team_ids = set()
    root = Path(adapters.PL_ROOT)
    expected = f"{season}_events_stats.csv"
    if not root.is_dir():
        raise FileNotFoundError(f"Approved upstream source not found: {root}")
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
    """Report FPL->FRL player relationship using the enforced contract."""
    audit = player_identity_audit.audit_season(season)
    fpl_rows = audit["fpl_candidates"]
    verified = 0
    unresolved = 0
    ambiguous = 0
    unavailable = 0

    # The identity adapter is cached; evaluate each seasonal FPL element once.
    elements = set()
    for row in fpl_rows:
        element = str(row.get("element") or row.get("fpl_element") or "").strip()
        if element:
            elements.add(element)

    for element in elements:
        result = resolve_fpl_player_identity(season, element)
        status = result["relationship_status"]
        if status == "VERIFIED":
            verified += 1
        elif status == "UNRESOLVED":
            unresolved += 1
        elif status == "AMBIGUOUS":
            ambiguous += 1
        elif status == "UNAVAILABLE":
            unavailable += 1

    return {
        "fpl_elements": len(elements),
        "verified": verified,
        "unresolved": unresolved,
        "ambiguous": ambiguous,
        "unavailable": unavailable,
    }


def player_source_overlap(season: str) -> dict:
    """Compare source namespaces using the canonical player-ID resolver."""
    player_match_ids = set()
    for row in adapters.player_match_source_rows_for_season(season):
        pid = str(source_player_id(row) or "").strip()
        if pid:
            player_match_ids.add(pid)

    player_season_ids = {
        str(row.get("playerId") or "").strip()
        for row in adapters.player_season_source_rows(season)
        if str(row.get("playerId") or "").strip()
    }

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
        "FPL->player verified/unresolved/ambig/unavail   player-id overlap   "
        "fields team/player/player-season"
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
            f"{p['verified']:4}/{p['unresolved']:<4}/{p['ambiguous']:<3}/{p['unavailable']:<3}                    "
            f"{o['direct_id_overlap']:4}/{o['player_match_only']:<3}/{o['player_season_only']:<3}       "
            f"{c['fixture_team_match']:3}/{c['player_match']:3}/{c['player_season']:3}"
        )

    print()
    print("RELATIONSHIP INTERPRETATION")
    print("- VERIFIED means the shared relationship contract accepted exactly one deterministic identity candidate.")
    print("- UNAVAILABLE means the required evidence is not exposed by the source for that season; it is not a failed identity.")
    print("- UNRESOLVED and AMBIGUOUS relationships remain outside canonical identity.")
    print("- Player-match absence is observational and is not treated as player-identity failure.")
    print("- Field-count differences are source availability/schema differences, not identity failures.")
    print("- Direct player ID overlap is reported as namespace diagnostics, not as an identity decision.")
    print()
    print("No files were written or modified.")
    print("=" * 120)


if __name__ == "__main__":
    print_report(run())
