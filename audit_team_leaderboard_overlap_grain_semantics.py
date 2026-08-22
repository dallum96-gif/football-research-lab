"""Audit team_leaderboard discoveries against FRL dictionary at grain/semantic level.

Evidence-first and fail-closed. Reads local FRL variable dictionary / derived
universe plus the live team-leaderboard capability map. It does NOT promote,
merge, or alter canonical data.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CAP = ROOT / "data" / "team_leaderboard_capability_map.csv"
DICT_CANDIDATES = [
    ROOT / "data" / "frl_variable_dictionary.csv",
    ROOT / "data" / "master_variable_universe_decomposed.csv",
    ROOT / "data" / "master_variable_universe.csv",
]
OUT = ROOT / "data" / "team_leaderboard_overlap_grain_semantics.csv"

TEAM_GRAINS = {"team", "team_season", "team_match"}
NONTEAM_GRAINS = {"player", "player_season", "player_match", "fixture", "event", "squad", "sample_payload"}


def first_existing_dictionary() -> Path | None:
    return next((p for p in DICT_CANDIDATES if p.exists()), None)


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def field_name(row: dict[str, str]) -> str:
    for key in ("field_name", "field", "variable", "name"):
        if row.get(key):
            return row[key].strip()
    return ""


def grain(row: dict[str, str]) -> str:
    for key in ("decomposed_grain", "resolved_grain", "grain", "original_grain"):
        if row.get(key):
            return row[key].strip()
    return "UNKNOWN"


def source_surface(row: dict[str, str]) -> str:
    for key in ("source_surface", "source", "surface"):
        if row.get(key):
            return row[key].strip()
    return "UNKNOWN"


def run() -> list[dict[str, str]]:
    caps = load_rows(CAP)
    dictionary_path = first_existing_dictionary()
    dictionary = load_rows(dictionary_path) if dictionary_path else []

    by_field: dict[str, list[dict[str, str]]] = {}
    for row in dictionary:
        f = field_name(row)
        if f:
            by_field.setdefault(f, []).append(row)

    out: list[dict[str, str]] = []
    for cap in caps:
        f = cap.get("field_name", "").strip()
        matches = by_field.get(f, [])
        grains = sorted({grain(r) for r in matches})
        sources = sorted({source_surface(r) for r in matches})

        if not matches:
            status = "GENUINELY_NEW"
            reason = "No exact FRL dictionary row for this native field name."
        elif any(g in TEAM_GRAINS for g in grains):
            status = "TEAM_GRAIN_MATCH_REVIEW"
            reason = "FRL contains the field at a team-like grain; exact team-season semantic equivalence still requires validation."
        elif all(g in NONTEAM_GRAINS or g == "UNKNOWN" for g in grains):
            status = "NONTEAM_ONLY"
            reason = "FRL exact-name matches exist only at non-team grains."
        else:
            status = "GRAIN_REVIEW"
            reason = "FRL exact-name matches exist, but grain classification is mixed or unresolved."

        out.append({
            "field_name": f,
            "family": cap.get("family", ""),
            "live_capability_status": cap.get("status", ""),
            "frl_dictionary": str(dictionary_path) if dictionary_path else "NOT_FOUND",
            "frl_grains": " | ".join(grains),
            "frl_source_surfaces": " | ".join(sources),
            "semantic_status": status,
            "reason": reason,
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        cols = list(out[0]) if out else ["field_name"]
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        writer.writerows(out)
    return out


if __name__ == "__main__":
    rows = run()
    totals: dict[str, int] = {}
    for r in rows:
        totals[r["semantic_status"]] = totals.get(r["semantic_status"], 0) + 1
    print("FRL TEAM LEADERBOARD OVERLAP GRAIN/SEMANTICS AUDIT")
    print("=" * 90)
    print(f"Fields inspected: {len(rows)}")
    for key, value in sorted(totals.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {value:4d}  {key}")
    print(f"FRL dictionary: {first_existing_dictionary() or 'NOT FOUND'}")
    print(f"Output: {OUT}")
    print("Evidence-only grain/semantic review; no canonical promotion.")
