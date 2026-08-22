"""Audit semantic overlap between live team-leaderboard discoveries and FRL fields.

Evidence-first, fail-closed. Scans the local FRL CSV universe when run locally and
uses the live discovery capability map as the source list. Does not promote or merge.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CAP = ROOT / "data" / "team_leaderboard_capability_map.csv"
UNIVERSE = ROOT / "data" / "team_leaderboard_universe_audit.csv"
OUT = ROOT / "data" / "team_leaderboard_semantic_overlap_audit.csv"

# Native-name matches can be misleading. These families are known to need grain review
# unless the exact FRL dictionary evidence says otherwise.
TEAM_GRAIN_HINTS = {
    "team_match", "team_season", "player_match", "player_season", "team", "fixture"
}

def load_capability_fields() -> list[dict[str, str]]:
    with CAP.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))

def local_field_evidence() -> dict[str, set[str]]:
    evidence: dict[str, set[str]] = {}
    for path in ROOT.rglob("*.csv"):
        if path.resolve() in {CAP.resolve(), UNIVERSE.resolve(), OUT.resolve()}:
            continue
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as fh:
                reader = csv.reader(fh)
                header = next(reader, [])
            for field in (h.strip() for h in header if h.strip()):
                evidence.setdefault(field, set()).add(str(path.relative_to(ROOT)))
        except Exception:
            continue
    return evidence

def run() -> list[dict[str, str]]:
    caps = load_capability_fields()
    local = local_field_evidence()
    rows: list[dict[str, str]] = []
    for row in caps:
        field = row.get("field_name", "")
        family = row.get("family", "")
        exact = field in local
        if not exact:
            status = "GENUINELY_NEW_BY_NAME"
            reason = "No exact native field header found in local FRL CSV universe."
        else:
            paths = sorted(local[field])
            grainish = any(any(g in p.lower() for g in TEAM_GRAIN_HINTS) for p in paths)
            if grainish:
                status = "SUPERFICIAL_NAME_MATCH_REVIEW"
                reason = "Exact name exists, but local evidence must be checked for matching team-season grain and semantics."
            else:
                status = "NAME_MATCH_NONTEAM_GRAIN"
                reason = "Exact name exists only in evidence files whose path does not establish team-season equivalence."
        rows.append({
            "field_name": field,
            "family": family,
            "live_status": row.get("status", ""),
            "frl_exact_name_match": str(exact),
            "frl_evidence_paths": " | ".join(sorted(local.get(field, set()))),
            "semantic_status": status,
            "reason": reason,
        })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]) if rows else ["field_name"])
        writer.writeheader(); writer.writerows(rows)
    return rows

if __name__ == "__main__":
    rows = run()
    totals: dict[str, int] = {}
    for r in rows: totals[r["semantic_status"]] = totals.get(r["semantic_status"], 0) + 1
    print("FRL TEAM LEADERBOARD SEMANTIC OVERLAP AUDIT")
    print("=" * 90)
    print(f"Fields inspected: {len(rows)}")
    for k,v in sorted(totals.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {v:4d}  {k}")
    print(f"Output: {OUT}")
    print("Evidence-only semantic overlap audit; no canonical promotion.")
