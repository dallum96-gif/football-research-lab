"""Resolve the seven team-grain live discoveries against the FRL analytical layout.

Evidence-first only. Compares the live team-leaderboard candidates with the FRL
variable dictionary and analytical layout contract. No canonical promotion.
"""
from __future__ import annotations
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "team_leaderboard_team_grain_matches.csv"
DICT = ROOT / "data" / "frl_variable_dictionary.csv"
OUT = ROOT / "data" / "team_leaderboard_team_grain_semantic_decisions.csv"


def main() -> list[dict[str, str]]:
    with INPUT.open("r", encoding="utf-8-sig", newline="") as fh:
        live_rows = list(csv.DictReader(fh))
    with DICT.open("r", encoding="utf-8-sig", newline="") as fh:
        dict_rows = list(csv.DictReader(fh))

    by_field: dict[str, list[dict[str, str]]] = {}
    for row in dict_rows:
        field = row.get("field_name", "").strip()
        if field:
            by_field.setdefault(field, []).append(row)

    out: list[dict[str, str]] = []
    for row in live_rows:
        field = row.get("field_name", "")
        matches = by_field.get(field, [])
        grains = sorted({(m.get("decomposed_grain") or m.get("grain") or "").strip() for m in matches if (m.get("decomposed_grain") or m.get("grain"))})
        # Conservative: team_match is a related team grain, but not equivalent to team_season.
        if "team_season" in grains:
            status = "TEAM_SEASON_EQUIVALENT_REVIEW"
            reason = "FRL already records the field at Team–Season grain; explicit semantic comparison still required."
        elif "team_match" in grains:
            status = "TEAM_MATCH_NOT_EQUIVALENT"
            reason = "FRL representation is Team–Fixture, while live discovery is Team–Season. Aggregation semantics differ."
        else:
            status = "OTHER_TEAM_GRAIN_REVIEW"
            reason = "A team-like FRL representation exists but grain/meaning is not a direct Team–Season match."
        out.append({
            "field_name": field,
            "live_family": row.get("family", ""),
            "frl_grains": " | ".join(grains),
            "decision": status,
            "reason": reason,
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["field_name","live_family","frl_grains","decision","reason"])
        writer.writeheader(); writer.writerows(out)
    return out

if __name__ == "__main__":
    rows = main()
    totals: dict[str, int] = {}
    for row in rows:
        totals[row["decision"]] = totals.get(row["decision"], 0) + 1
    print("FRL TEAM LEADERBOARD TEAM-GRAIN SEMANTIC DECISIONS")
    print("=" * 90)
    print(f"Fields reviewed: {len(rows)}")
    for key, value in sorted(totals.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {value:4d}  {key}")
    print(f"Output: {OUT}")
    print("Evidence-only decisioning; no semantic/canonical promotion.")
