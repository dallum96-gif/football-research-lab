"""Audit semantic overlap between live team-leaderboard discoveries and FRL fields.

Evidence-first, fail-closed. Compares discovered native field names against the
row-based FRL variable dictionary when available, preserving FRL grain evidence.
No semantic/canonical promotion is performed.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CAP = ROOT / "data" / "team_leaderboard_capability_map.csv"
OUT = ROOT / "data" / "team_leaderboard_semantic_overlap_audit.csv"

DICTIONARY_CANDIDATES = (
    ROOT / "data" / "frl_variable_dictionary.csv",
    ROOT / "data" / "master_variable_universe_decomposed.csv",
    ROOT / "data" / "master_variable_universe.csv",
)

TEAM_GRAINS = {"team", "team_season", "team_match", "squad"}


def first_existing_dictionary() -> Path | None:
    for path in DICTIONARY_CANDIDATES:
        if path.exists():
            return path
    return None


def load_capability_fields() -> list[dict[str, str]]:
    with CAP.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def load_dictionary() -> tuple[Path | None, list[dict[str, str]]]:
    path = first_existing_dictionary()
    if not path:
        return None, []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return path, list(csv.DictReader(fh))


def normalise_field(row: dict[str, str]) -> str:
    for key in ("field_name", "field", "variable", "name"):
        value = row.get(key, "")
        if value:
            return value.strip()
    return ""


def row_grain(row: dict[str, str]) -> str:
    for key in ("decomposed_grain", "grain", "resolved_grain", "original_grain"):
        value = row.get(key, "")
        if value:
            return value.strip()
    return ""


def run() -> list[dict[str, str]]:
    caps = load_capability_fields()
    dictionary_path, dictionary_rows = load_dictionary()
    by_field: dict[str, set[str]] = {}
    for row in dictionary_rows:
        field = normalise_field(row)
        if field:
            by_field.setdefault(field, set()).add(row_grain(row) or "UNKNOWN")

    rows: list[dict[str, str]] = []
    for row in caps:
        field = row.get("field_name", "")
        family = row.get("family", "")
        grains = sorted(by_field.get(field, set()))
        if not grains:
            status = "GENUINELY_NEW_BY_NAME"
            reason = "No exact field-name row found in the FRL variable dictionary."
        elif any(g in TEAM_GRAINS for g in grains):
            status = "SUPERFICIAL_NAME_MATCH_REVIEW"
            reason = "Exact field exists in FRL with a team-like grain; team-season semantic equivalence still requires explicit verification."
        else:
            status = "NAME_MATCH_NONTEAM_GRAIN"
            reason = "Exact field exists only at non-team grains in the FRL dictionary."
        rows.append({
            "field_name": field,
            "family": family,
            "live_status": row.get("status", ""),
            "frl_dictionary_path": str(dictionary_path) if dictionary_path else "MISSING",
            "frl_grains": " | ".join(grains),
            "semantic_status": status,
            "reason": reason,
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        cols = ["field_name", "family", "live_status", "frl_dictionary_path", "frl_grains", "semantic_status", "reason"]
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__":
    rows = run()
    totals: dict[str, int] = {}
    for row in rows:
        totals[row["semantic_status"]] = totals.get(row["semantic_status"], 0) + 1
    print("FRL TEAM LEADERBOARD SEMANTIC OVERLAP AUDIT")
    print("=" * 90)
    print(f"Fields inspected: {len(rows)}")
    for key, value in sorted(totals.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {value:4d}  {key}")
    print(f"FRL dictionary: {first_existing_dictionary() or 'NOT FOUND'}")
    print(f"Output: {OUT}")
    print("Evidence-only semantic overlap audit; no canonical promotion.")
