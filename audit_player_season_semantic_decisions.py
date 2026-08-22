"""Resolve player-season live candidates against FRL Player-Season evidence.

Evidence-first only. No semantic or canonical promotion.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LIVE = ROOT / "data" / "player_season_semantic_overlap_audit.csv"
DICT = ROOT / "data" / "frl_variable_dictionary.csv"
OUT = ROOT / "data" / "player_season_semantic_decisions.csv"

PLAYER_SEASON_GRAINS = {"player_season"}


def load_dictionary() -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    with DICT.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            field = row.get("field_name", "").strip()
            grain = row.get("grain", "").strip() or row.get("decomposed_grain", "").strip()
            if field:
                out.setdefault(field, set()).add(grain or "UNKNOWN")
    return out


def run() -> list[dict[str, str]]:
    dictionary = load_dictionary()
    rows: list[dict[str, str]] = []
    with LIVE.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            field = row.get("field_name", "").strip()
            grains = sorted(dictionary.get(field, set()))
            if grains and all(g in PLAYER_SEASON_GRAINS for g in grains):
                status = "PLAYER_SEASON_EQUIVALENT_REVIEW"
                reason = "FRL evidence is already exclusively player_season; verify metric semantics/provenance before treating as equivalent."
            elif any(g in PLAYER_SEASON_GRAINS for g in grains):
                status = "MIXED_GRAIN_REVIEW"
                reason = "FRL contains player_season plus other grains; semantic equivalence remains unresolved."
            else:
                status = "NON_PLAYER_SEASON_FRL"
                reason = "FRL field exists, but dictionary evidence does not establish player_season grain."
            rows.append({
                "field_name": field,
                "live_endpoint": row.get("live_endpoint", ""),
                "frl_grains": " | ".join(grains),
                "decision_status": status,
                "reason": reason,
            })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        cols = ["field_name", "live_endpoint", "frl_grains", "decision_status", "reason"]
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__":
    rows = run()
    totals: dict[str, int] = {}
    for row in rows:
        totals[row["decision_status"]] = totals.get(row["decision_status"], 0) + 1
    print("FRL PLAYER-SEASON SEMANTIC DECISIONS")
    print("=" * 90)
    print(f"Fields reviewed: {len(rows)}")
    for key, value in sorted(totals.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {value:4d}  {key}")
    print(f"Output: {OUT}")
    print("Evidence-only semantic decisioning; no canonical promotion.")
