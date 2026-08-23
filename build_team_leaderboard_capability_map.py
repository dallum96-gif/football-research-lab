"""Build an evidence-first capability map for the live team_leaderboard.stats universe.

Reads existing local audit artefacts only. No network access and no canonical promotion.
Status meanings:
- EXISTING_FIELD: exact native field name is present in the FRL local variable universe.
- DERIVABLE_WITHIN_SOURCE: source-side arithmetic relationship is explicitly recognised.
- NEW_SOURCE_CAPABILITY: no exact FRL field match and no safe derivation rule.
- REVIEW: field requires semantic review before capability can be trusted.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CLASSIFICATION = ROOT / "data" / "team_leaderboard_universe_classification.csv"
FAMILIES = ROOT / "data" / "team_leaderboard_discovery_families.csv"
VALUES = ROOT / "data" / "team_leaderboard_candidate_values.csv"
OUT = ROOT / "data" / "team_leaderboard_capability_map.csv"

DERIVATION_RULES = {
    "duels": "duelsWon + duelsLost",
    "goalsConceded": "goalsConcededInsideBox + goalsConcededOutsideBox",
}

REVIEW_FIELDS = {
    "gamesPlayed": "Scope-sensitive aggregate; retain only with explicit team-season semantics.",
    "goals": "Potentially canonical/derived elsewhere; exact local equivalence must be checked before adoption.",
    "goalsConceded": "Potentially derivable/source-native; retain source evidence and validate against FRL fixture aggregation.",
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def local_field_names() -> set[str]:
    names: set[str] = set()
    for candidate in (
        ROOT / "data" / "master_variable_universe_decomposed.csv",
        ROOT / "data" / "frl_variable_dictionary.csv",
        ROOT / "data" / "frl_variable_dictionary_profile.csv",
    ):
        if not candidate.exists():
            continue
        for row in read_rows(candidate):
            for key in ("field_name", "variable", "native_field", "source_field"):
                value = row.get(key, "").strip()
                if value:
                    names.add(value)
    return names


def run() -> list[dict[str, str]]:
    classification = {r["field_name"]: r for r in read_rows(CLASSIFICATION)}
    family = {r["field_name"]: r.get("family", r.get("category", "Review")) for r in read_rows(FAMILIES)}
    values = {r["field_name"]: r for r in read_rows(VALUES)}
    local = local_field_names()

    rows: list[dict[str, str]] = []
    for field in sorted(classification):
        c = classification[field]
        if c.get("category") != "ANALYTICAL_CANDIDATE":
            continue

        if field in local:
            status = "EXISTING_FIELD"
            reason = "Exact native field name appears in the local FRL variable universe."
        elif field in DERIVATION_RULES:
            status = "DERIVABLE_WITHIN_SOURCE"
            reason = f"Recognised source-side relationship: {DERIVATION_RULES[field]}."
        elif field in REVIEW_FIELDS:
            status = "REVIEW"
            reason = REVIEW_FIELDS[field]
        else:
            status = "NEW_SOURCE_CAPABILITY"
            reason = "No exact FRL field match and no safe derivation rule recognised."

        v = values.get(field, {})
        rows.append({
            "field_name": field,
            "family": family.get(field, "Review"),
            "field_type": v.get("field_type", ""),
            "sample_values": v.get("sample_values", ""),
            "status": status,
            "reason": reason,
            "grain": "team_season_candidate",
            "source_surface": "pulselive_live_api",
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    cols = ["field_name", "family", "field_type", "sample_values", "status", "reason", "grain", "source_surface"]
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__":
    rows = run()
    print("FRL TEAM LEADERBOARD CAPABILITY MAP")
    print("=" * 90)
    totals: dict[str, int] = {}
    families: dict[str, int] = {}
    for row in rows:
        totals[row["status"]] = totals.get(row["status"], 0) + 1
        families[row["family"]] = families.get(row["family"], 0) + 1
    print(f"Analytical candidates mapped: {len(rows)}")
    print("\nSTATUS")
    for key, value in sorted(totals.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {value:3d}  {key}")
    print("\nFAMILY")
    for key, value in sorted(families.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {value:3d}  {key}")
    print(f"\nOutput: {OUT}")
    print("Evidence-first capability mapping only; no semantic or canonical promotion.")
