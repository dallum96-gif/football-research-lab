"""Audit semantic overlap between live player-season discoveries and FRL grains.

Evidence-first, fail-closed. Compares the distinct analytical player-season live
fields against the row-based FRL variable dictionary and preserves FRL grain evidence.
No semantic or canonical promotion.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CLASS = ROOT / "data" / "player_season_live_universe_classification.csv"
DICT = ROOT / "data" / "frl_variable_dictionary.csv"
OUT = ROOT / "data" / "player_season_semantic_overlap_audit.csv"

PLAYER_GRAINS = {"player", "player_season", "player_match", "squad"}


def load_candidates() -> list[str]:
    fields: set[str] = set()
    with CLASS.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if row.get("category") == "ANALYTICAL_CANDIDATE" or row.get("candidate_family") == "ANALYTICAL_CANDIDATE" or row.get("status") == "ANALYTICAL_CANDIDATE":
                field = row.get("field_name", "").strip()
                if field:
                    fields.add(field)
    return sorted(fields)


def normalise_field(row: dict[str, str]) -> str:
    for key in ("field_name", "field", "variable", "name"):
        value = row.get(key, "").strip()
        if value:
            return value
    return ""


def row_grain(row: dict[str, str]) -> str:
    for key in ("decomposed_grain", "grain", "resolved_grain", "original_grain"):
        value = row.get(key, "").strip()
        if value:
            return value
    return ""


def load_dictionary() -> dict[str, set[str]]:
    by_field: dict[str, set[str]] = {}
    with DICT.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            field = normalise_field(row)
            if field:
                by_field.setdefault(field, set()).add(row_grain(row) or "UNKNOWN")
    return by_field


def run() -> list[dict[str, str]]:
    candidates = load_candidates()
    by_field = load_dictionary()
    rows: list[dict[str, str]] = []
    for field in candidates:
        grains = sorted(by_field.get(field, set()))
        if not grains:
            status = "GENUINELY_NEW_BY_NAME"
            reason = "No exact field-name row found in the FRL variable dictionary."
        elif "player_season" in grains:
            status = "PLAYER_SEASON_GRAIN_MATCH_REVIEW"
            reason = "Exact field exists at player-season grain; semantics still require explicit equivalence review."
        elif any(g in PLAYER_GRAINS for g in grains):
            status = "PLAYER_NONSEASON_GRAIN"
            reason = "Exact field exists only at a player-related non-season grain."
        else:
            status = "NAME_MATCH_NONPLAYER_GRAIN"
            reason = "Exact field exists only at non-player grains."
        rows.append({
            "field_name": field,
            "frl_grains": " | ".join(grains),
            "semantic_status": status,
            "reason": reason,
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["field_name", "frl_grains", "semantic_status", "reason"])
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__":
    rows = run()
    totals: dict[str, int] = {}
    for row in rows:
        totals[row["semantic_status"]] = totals.get(row["semantic_status"], 0) + 1
    print("FRL PLAYER-SEASON SEMANTIC OVERLAP AUDIT")
    print("=" * 90)
    print(f"Distinct analytical candidates: {len(rows)}")
    for key, value in sorted(totals.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {value:4d}  {key}")
    print(f"Output: {OUT}")
    print("Evidence-only grain/semantic review; no canonical promotion.")
