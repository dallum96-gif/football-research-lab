"""Read-only diagnostic for FPL player/team context coverage.

This deliberately uses the existing Player Research loader and reports which
team-related fields are actually present on the canonical FPL rows. It does
not alter identity mappings or canonical data.
"""
from collections import Counter

import player_research
from player_identity_crosswalk import SEASONS


def audit(seasons=SEASONS):
    rows = []
    for season in seasons:
        rows.extend(player_research._load_season_rows(season))

    counters = Counter()
    examples = {}
    for row in rows:
        for field in ("team", "team_code", "_club"):
            value = str(row.get(field) or "").strip()
            counters[(field, "present" if value else "blank")] += 1
            if value and (field, "present") not in examples:
                examples[(field, "present")] = (row.get("_season"), row.get("element"), row.get("name"), value)
        team = str(row.get("team") or "").strip()
        team_code = str(row.get("team_code") or "").strip()
        club = str(row.get("_club") or "").strip()
        if team or team_code or club:
            counters["any_team_context_present"] += 1
        else:
            counters["all_team_context_blank"] += 1
            if "blank_example" not in examples:
                examples["blank_example"] = (row.get("_season"), row.get("element"), row.get("name"))

    return counters, examples, len(rows)


def main():
    counters, examples, total = audit()
    print("=" * 96)
    print("FRL FPL TEAM-CONTEXT COVERAGE DIAGNOSTIC")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 96)
    print(f"Loaded FPL rows: {total:,}")
    for field in ("team", "team_code", "_club"):
        print(f"{field} present: {counters[(field, 'present')]:,}")
        print(f"{field} blank:   {counters[(field, 'blank')]:,}")
    print(f"Any team context present: {counters['any_team_context_present']:,}")
    print(f"All team context blank:  {counters['all_team_context_blank']:,}")
    print("\nEXAMPLES:")
    for key in (("team", "present"), ("team_code", "present"), ("_club", "present"), "blank_example"):
        if key in examples:
            print(f"  {key}: {examples[key]}")
    print("\nNo files were written or modified.")
    print("=" * 96)


if __name__ == "__main__":
    main()
