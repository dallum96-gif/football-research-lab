"""Finalize the team-season capability delta from the live leaderboard audit.

Evidence-first. Consumes the existing capability map and grain/semantics audit and
records whether each discovered field is already available at team-season grain.
No semantic/canonical promotion.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CAP = ROOT / "data" / "team_leaderboard_capability_map.csv"
GRAIN = ROOT / "data" / "team_leaderboard_overlap_grain_semantics.csv"
DECISIONS = ROOT / "data" / "team_leaderboard_team_grain_semantic_decisions.csv"
OUT = ROOT / "data" / "team_season_capability_delta.csv"


def load(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def run() -> list[dict[str, str]]:
    cap = {r.get("field_name", ""): r for r in load(CAP)}
    grain_rows = {r.get("field_name", ""): r for r in load(GRAIN)}
    decision_rows = {r.get("field_name", ""): r for r in load(DECISIONS)}

    rows: list[dict[str, str]] = []
    for field, c in sorted(cap.items()):
        g = grain_rows.get(field, {})
        d = decision_rows.get(field, {})
        frl_grains = g.get("frl_grains", "")

        if "team_season" in {x.strip() for x in frl_grains.split("|") if x.strip()}:
            delta = "ALREADY_TEAM_SEASON"
            reason = "FRL dictionary records an explicit team_season grain."
        else:
            delta = "NEW_TEAM_SEASON_CAPABILITY"
            reason = "No explicit team_season FRL grain exists for this native concept; any existing representation is at another grain or absent."

        rows.append({
            "field_name": field,
            "family": c.get("family", ""),
            "live_status": c.get("status", ""),
            "frl_grains": frl_grains,
            "prior_semantic_status": g.get("semantic_status", ""),
            "team_grain_decision": d.get("decision", ""),
            "team_season_delta": delta,
            "reason": reason,
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        cols = list(rows[0]) if rows else ["field_name"]
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__":
    rows = run()
    totals: dict[str, int] = {}
    for r in rows:
        k = r["team_season_delta"]
        totals[k] = totals.get(k, 0) + 1
    print("FRL TEAM-SEASON CAPABILITY DELTA")
    print("=" * 90)
    print(f"Fields reviewed: {len(rows)}")
    for k, v in sorted(totals.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {v:4d}  {k}")
    print(f"Output: {OUT}")
    print("Evidence-first delta only; no semantic/canonical promotion.")
