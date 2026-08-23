"""Read-only relationship gap classification for all available FRL seasons.

Separates source unavailability from genuine relationship failures. Does not
promote identities, mutate canonical data, or write research outputs.
"""
from __future__ import annotations

from functools import lru_cache
import player_identity_audit
import source_family_adapters as adapters

SEASONS = tuple(player_identity_audit.SEASONS)

@lru_cache(maxsize=None)
def classify_player_relationship(season: str) -> dict:
    report = player_identity_audit.audit_season(season)
    # Relationship is testable only when FPL rows expose a usable seasonal club
    # or team code. Do not interpret absent source context as failed identity.
    rows = tuple(player_identity_audit.player_research._load_season_rows(season))
    team_context = any(
        str(row.get("team") or row.get("team_code") or row.get("_club") or "").strip()
        for row in rows
    )
    status = "TESTABLE" if team_context else "UNAVAILABLE_SOURCE_TEAM_CONTEXT"
    return {"status": status, **report}

@lru_cache(maxsize=None)
def fixture_gap(season: str) -> dict:
    fixtures = adapters.season_fixtures(season)
    missing = []
    for fixture in fixtures:
        fid = str(fixture.get("fixture_id") or "").strip()
        try:
            adapters.resolve_source_match(season, fid)
        except ValueError:
            missing.append(fid)
    return {"canonical_fixtures": len(fixtures), "missing_source_matches": tuple(missing)}

@lru_cache(maxsize=None)
def player_id_overlap(season: str) -> dict:
    pm_ids = set()
    for row in adapters.player_match_source_rows_for_season(season):
        # Use the repository's canonical source-player ID helper.
        pid = player_identity_audit.source_player_id(row)
        if pid:
            pm_ids.add(str(pid).strip())

    ps_ids = {
        str(row.get("playerId") or "").strip()
        for row in adapters.player_season_source_rows(season)
        if str(row.get("playerId") or "").strip()
    }
    return {
        "player_match_source_ids": len(pm_ids),
        "player_season_source_ids": len(ps_ids),
        "direct_id_overlap": len(pm_ids & ps_ids),
        "player_match_only": len(pm_ids - ps_ids),
        "player_season_only": len(ps_ids - pm_ids),
    }

def run() -> dict:
    return {
        season: {
            "player_relationship_status": classify_player_relationship(season)["status"],
            "player_relationship": {
                "fpl_candidates": classify_player_relationship(season)["fpl_candidates"],
                "source_candidates": classify_player_relationship(season)["source_candidates"],
                "exact": len(classify_player_relationship(season)["exact"]),
                "missing": len(classify_player_relationship(season)["missing"]),
                "ambiguous": len(classify_player_relationship(season)["ambiguous"]),
            },
            "fixture_gap": fixture_gap(season),
            "player_id_overlap": player_id_overlap(season),
        }
        for season in SEASONS
    }

def print_report(results: dict) -> None:
    print("=" * 120)
    print("FRL RELATIONSHIP GAP CLASSIFICATION AUDIT")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 120)
    for season, r in results.items():
        p = r["player_relationship"]
        f = r["fixture_gap"]
        o = r["player_id_overlap"]
        print(f"{season}")
        print(f"  FPL->source player relationship: {r['player_relationship_status']}")
        print(f"    candidates={p['fpl_candidates']} source={p['source_candidates']} exact={p['exact']} missing={p['missing']} ambiguous={p['ambiguous']}")
        print(f"  fixture source gaps: {len(f['missing_source_matches'])}")
        if f["missing_source_matches"]:
            print(f"    fixture_ids={list(f['missing_source_matches'])[:10]}")
        print(f"  player-match vs player-season IDs: overlap={o['direct_id_overlap']} match_only={o['player_match_only']} season_only={o['player_season_only']}")
        print()
    print("INTERPRETATION")
    print("- UNAVAILABLE_SOURCE_TEAM_CONTEXT means the relationship is not testable from the exposed FPL schema.")
    print("- TESTABLE relationships are classified as exact, missing, or ambiguous; none are promoted automatically.")
    print("- Fixture gaps and player-ID overlap are independent relationship checks.")
    print("No files were written or modified.")
    print("=" * 120)

if __name__ == "__main__":
    print_report(run())
