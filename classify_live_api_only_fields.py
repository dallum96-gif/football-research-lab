"""Classify live-API-only fields into evidence families without semantic promotion."""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "live_api_vs_longitudinal_pl.csv"
OUTPUT = ROOT / "data" / "live_api_only_field_classification.csv"

CONTENT_ENDPOINTS = {"broadcast_match_events", "player_profile_content"}
CONFIG_ENDPOINTS = {"current_gameweek_config", "clubs_metadata"}
CONTEXT_ENDPOINTS = {
    "competition", "competition_teams", "season_teams", "standings", "season_structure",
    "season_awards", "team_squad", "player_directory", "player_basic", "player_career",
    "player_season_info", "match_officials",
}
FOOTBALL_ENDPOINTS = {
    "matches", "match_detail", "match_events", "match_lineups", "match_stats", "match_commentary",
    "team_form", "team_stats", "player_season_stats", "player_leaderboard", "team_leaderboard",
}


def family(endpoint: str) -> str:
    if endpoint in CONTENT_ENDPOINTS:
        return "CONTENT_MEDIA"
    if endpoint in CONFIG_ENDPOINTS:
        return "CONFIGURATION"
    if endpoint in CONTEXT_ENDPOINTS:
        return "IDENTITY_CONTEXT"
    if endpoint in FOOTBALL_ENDPOINTS:
        return "FOOTBALL_RESEARCH"
    return "UNCLASSIFIED_REVIEW"


def run() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with INPUT.open("r", encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            if r.get("state") != "LIVE_ONLY":
                continue
            endpoints = [x.strip() for x in (r.get("live_endpoints", "").split(" | ")) if x.strip()]
            candidate_families = sorted({family(endpoint) for endpoint in endpoints})
            rows.append({
                **r,
                "candidate_family": ";".join(candidate_families) if candidate_families else "UNCLASSIFIED_REVIEW",
                "review_status": "OPEN",
            })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    base_columns = ["field_name", "state", "live_endpoints", "historical_grains"]
    extra_columns = sorted({
        key
        for row in rows
        for key in row
        if key not in base_columns and key not in {"candidate_family", "review_status"}
    })
    cols = base_columns + extra_columns + ["candidate_family", "review_status"]
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__":
    rows = run()
    c = Counter(r["candidate_family"] for r in rows)
    print("FRL LIVE-ONLY API FIELD CLASSIFICATION")
    print("=" * 90)
    print(f"LIVE_ONLY fields inspected: {len(rows)}")
    for k, v in c.most_common():
        print(f"  {v:4d}  {k}")
    by = defaultdict(int)
    for r in rows:
        for endpoint in [x.strip() for x in r["live_endpoints"].split(" | ") if x.strip()]:
            by[(endpoint, r["candidate_family"])] += 1
    print("\nBY ENDPOINT")
    for (endpoint, fam), n in sorted(by.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {n:4d}  {endpoint:28s}  {fam}")
    print(f"\nOutput: {OUTPUT}")
    print("Candidate family only; no semantic/canonical promotion.")
