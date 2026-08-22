"""Audit season-aware Team-Match -> team-season identity route.

Evidence-only. Does not promote any identity contract.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
TEAM_MATCH = DATA / "fixture_match_stats.csv"
TEAM_SEASONS = ROOT / "identity" / "team_seasons.csv"
OUT = DATA / "team_match_team_identity_route_audit.csv"


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def norm(v):
    return str(v).strip() if v is not None else ""


def main():
    tm = read_csv(TEAM_MATCH)
    ts = read_csv(TEAM_SEASONS)

    # Candidate mappings from known registry fields.
    local_map = defaultdict(set)
    persistent_map = defaultdict(set)
    club_map = defaultdict(set)
    for r in ts:
        season = norm(r.get("season"))
        if season:
            if norm(r.get("local_team_id")):
                local_map[(season, norm(r["local_team_id"]))].add(norm(r.get("team_season_id")))
            if norm(r.get("persistent_team_code")):
                persistent_map[(season, norm(r["persistent_team_code"]))].add(norm(r.get("team_season_id")))
            if norm(r.get("club_id")):
                club_map[(season, norm(r["club_id"]))].add(norm(r.get("team_season_id")))

    print("FRL TEAM-MATCH TEAM IDENTITY ROUTE AUDIT")
    print("=" * 100)
    print(f"Team-Match rows: {len(tm)}")
    print(f"Team-season registry rows: {len(ts)}")

    # fixture_id+season is a fixture key; team_match contains only core match stats,
    # so this audit checks whether its rows can expose a side/team key directly.
    cols = set(tm[0]) if tm else set()
    candidate_team_cols = [c for c in sorted(cols) if any(t in c.lower() for t in ("team", "club")) and not c.endswith("possession")]
    print("Candidate team columns:", ", ".join(candidate_team_cols) if candidate_team_cols else "NONE")

    # Registry coverage of common source team IDs using the fixture registries as the
    # evidence that connects the two sides of a fixture to the season-aware team registry.
    fixtures = read_csv(ROOT / "fixtures_master.csv")
    key_counts = Counter()
    mapping_counts = Counter()
    ambiguous = Counter()

    fixture_seen = 0
    for f in fixtures:
        season = norm(f.get("season"))
        for side in ("home", "away"):
            raw = norm(f.get(f"{side}_team_id"))
            if not season or not raw:
                continue
            fixture_seen += 1
            key_counts[side] += 1
            matches = local_map.get((season, raw), set())
            if len(matches) == 1:
                mapping_counts[side] += 1
            elif len(matches) > 1:
                ambiguous[side] += 1

    print("\nFIXTURE-SIDE -> TEAM-SEASON REGISTRY")
    for side in ("home", "away"):
        print(f"  {side:5} observations={key_counts[side]:5d} unique_mapping={mapping_counts[side]:5d} ambiguous={ambiguous[side]:5d}")

    print("\nTEAM-MATCH TEMPORAL IDENTITY INTERPRETATION")
    print("  Fixture identity: fixture_id + season (or source_match_id)")
    print("  Team identity route candidate: season + local_team_id -> team_season_id")
    print("  This audit does NOT promote the route; it only measures registry determinism.")

    rows = []
    for key in sorted(set(key_counts) | set(mapping_counts) | set(ambiguous)):
        rows.append({
            "side": key,
            "fixture_side_observations": key_counts[key],
            "unique_team_season_mapping": mapping_counts[key],
            "ambiguous_team_season_mapping": ambiguous[key],
        })

    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        fields = ["side", "fixture_side_observations", "unique_team_season_mapping", "ambiguous_team_season_mapping"]
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print(f"\nOutput: {OUT}")


if __name__ == "__main__":
    main()
