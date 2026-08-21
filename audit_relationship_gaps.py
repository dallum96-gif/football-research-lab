"""Read-only relationship gap classification for all available FRL seasons.

Separates source unavailability from genuine relationship failures. Does not
promote identities, mutate canonical data, or write research outputs.
"""
from __future__ import annotations

from pathlib import Path
import player_identity_audit
import source_family_adapters as adapters

SEASONS = tuple(player_identity_audit.SEASONS)


def classify_player_relationship(season: str) -> dict:
    report = player_identity_audit.audit_season(season)
    # For the first four seasons the FPL source rows have no usable team
    # context; this makes the identity relationship unavailable rather than
    # unresolved. Later seasons have usable team context and can be evaluated.
    team_context = any(
        str(row.get("team") or row.get("team_code") or player_identity_audit.normalize_name(str(row.get("_club") or "").strip()))
        for row in player_identity_audit.player_research._load_season_rows(season)
    ) if hasattr(player_identity_audit, "player_research") else False
    status = "TESTABLE" if team_context else "UNAVAILABLE_SOURCE_TEAM_CONTEXT"
    return {"status": status, **report}


def fixture_gap(season: str) -> dict:
    fixtures = adapters.season_fixtures(season)
    missing = []
    for fixture in fixtures:
        fid = str(fixture.get("fixture_id") or "").strip()
        try:
            adapters.resolve_source_match(season, fid)
        except ValueError:
            missing.append(fid)
    return {"canonical_fixtures": len(fixtures), "missing_source_matches": missing}


def player_id_overlap(season: str) -> dict:
    pm = {str(r.get("playerId") or r.get("pl_code") or r.get("player_id") or "").strip()
          for r in adapters.player_match_source_rows_for_season(season)
          if str(r.get("playerId") or r.get("pl_code") or r.get("player_id") or "").strip()}
    ps = {str(r.get("playerId") or "").strip()
          for r in adapters.player_season_source_rows(season)
          if str(r.get("playerId") or "").strip()}
    return {
        "player_match_source_ids": len(pm),
        "player_season_source_ids": len(ps),
        "direct_id_overlap": len(pm & ps),
        "player_match_only": len(pm - ps),
        "player_season_only": len(ps - pm),
    }


def run() -> dict:
    out = {}
    for season in SEASONS:
        pr = classify_player_relationship(season)
        out[season] = {
            "player_relationship_status": pr["status"],
            "player_relationship": {
                "fpl_candidates": pr["fpl_candidates"],
                "source_candidates": pr["source_candidates"],
                "exact": len(pr["exact"]),
                "missing": len(pr["missing"]),
                "ambiguous": len(pr["ambiguous"]),
            },
            "fixture_gap": fixture_gap(season),
            "player_id_overlap": player_id_overlap(season),
        }
    return out


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
            print(f"    fixture_ids={f['missing_source_matches'][:10]}")
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
