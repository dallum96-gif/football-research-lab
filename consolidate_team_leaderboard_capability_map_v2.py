"""Consolidate the Team Leaderboard 63-field discovery into a conservative capability map.

Evidence-first only. Consumes existing audit artefacts generated in frl-source-audit:
- team_leaderboard_capability_map.csv
- team_leaderboard_fixture_semantic_audit.csv
- team_leaderboard_source_relationships_full.csv
- team_leaderboard_team_grain_semantic_decisions.csv
- team_season_capability_delta.csv

No canonical promotion. The script deliberately distinguishes source redundancy,
Team-Match-only evidence, unresolved specialist capabilities, and exact-name
collisions that are not Team equivalences.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

FILES = {
    "cap": DATA / "team_leaderboard_capability_map.csv",
    "fixture": DATA / "team_leaderboard_fixture_semantic_audit.csv",
    "relationships": DATA / "team_leaderboard_source_relationships_full.csv",
    "team_grain": DATA / "team_leaderboard_team_grain_semantic_decisions.csv",
    "delta": DATA / "team_season_capability_delta.csv",
}
OUT = DATA / "team_leaderboard_capability_map_v2.csv"

REL_EXACT = {"duels", "goalsConceded", "aerialDuels"}
TEAM_MATCH_ONLY = {
    "expectedAssists", "expectedGoals", "expectedGoalsFreekick",
    "expectedGoalsOnTarget", "expectedGoalsOnTargetConceded",
    "possessionPercentage", "touchesInOppBox",
}


def load(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def index(rows: list[dict[str, str]], key: str = "field_name") -> dict[str, dict[str, str]]:
    return {r.get(key, "").strip(): r for r in rows if r.get(key, "").strip()}


def main() -> list[dict[str, str]]:
    cap = index(load(FILES["cap"]))
    fixture = index(load(FILES["fixture"]))
    rel = index(load(FILES["relationships"]))
    team_grain = index(load(FILES["team_grain"]))
    delta = index(load(FILES["delta"]))

    rows: list[dict[str, str]] = []
    for field in sorted(cap):
        c = cap[field]
        f = fixture.get(field, {})
        r = rel.get(field, {})
        tg = team_grain.get(field, {})
        d = delta.get(field, {})

        if field in TEAM_MATCH_ONLY:
            capability_class = "TEAM_MATCH_ONLY_REVIEW"
            basis = "Existing FRL evidence is Team-Match, not Team-Season; aggregation/definition equivalence remains open."
        elif field in REL_EXACT:
            capability_class = "SOURCE_RELATIONSHIP_VERIFIED_REDUNDANT"
            basis = "Source-side arithmetic identity tested exactly across all cached observations discovered by the full audit."
        elif f.get("fixture_concept_status") == "TEAM_FIXTURE_CONCEPT_MATCH":
            capability_class = "TEAM_FIXTURE_CONCEPT_REVIEW"
            basis = "A Team-Fixture concept counterpart is recognised; semantic identity and Team-Season aggregation remain open."
        elif f.get("fixture_concept_status") == "MAPPED_CONCEPT_NOT_PRESENT_IN_CURRENT_FILE":
            capability_class = "CONCEPTUAL_FIXTURE_REVIEW"
            basis = "A semantic counterpart was proposed but is not exposed by the current fixture_match_stats schema."
        elif f.get("fixture_concept_status") == "NO_OBVIOUS_TEAM_FIXTURE_EQUIVALENT":
            capability_class = "SPECIALIST_TEAM_SEASON_REVIEW"
            basis = "No conservative Team-Fixture counterpart was established in the current evidence layer."
        elif tg.get("decision") == "TEAM_MATCH_NOT_EQUIVALENT":
            capability_class = "TEAM_MATCH_NOT_EQUIVALENT"
            basis = "Existing FRL representation is Team-Match and was explicitly rejected as a direct Team-Season equivalent."
        else:
            capability_class = "REVIEW"
            basis = "Evidence is insufficient for a stronger classification."

        rows.append({
            "field_name": field,
            "family": c.get("family", ""),
            "source_grain": c.get("grain", ""),
            "live_status": c.get("status", ""),
            "prior_team_season_delta": d.get("team_season_delta", ""),
            "fixture_semantic_status": f.get("fixture_concept_status", ""),
            "source_relationship_status": r.get("relationship_status", ""),
            "team_grain_status": tg.get("decision", ""),
            "capability_class": capability_class,
            "basis": basis,
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    columns = list(rows[0]) if rows else ["field_name"]
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__":
    rows = main()
    counts: dict[str, int] = {}
    for row in rows:
        key = row["capability_class"]
        counts[key] = counts.get(key, 0) + 1
    print("FRL TEAM LEADERBOARD CAPABILITY MAP V2")
    print("=" * 90)
    print(f"Concepts consolidated: {len(rows)}")
    for key, value in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {value:4d}  {key}")
    print(f"Output: {OUT}")
    print("Evidence-first consolidation only; no canonical promotion.")
