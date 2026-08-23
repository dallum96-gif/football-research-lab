"""Profile the unspecified relationship frontier by source context.

Evidence-only. Reads the relationship frontier produced in frl-source-audit and
looks for contextual signals in resource names, field names and source identity
metadata. It never creates identity contracts or infers joins.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
INPUT = DATA / "unspecified_relationship_frontier.csv"
OUT = DATA / "unspecified_relationship_context.csv"


def rows():
    with INPUT.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def classify(row: dict[str, str]) -> tuple[str, str]:
    surface = row.get("source_surface", "").lower()
    resource = row.get("resource", "").lower()
    field = row.get("field_name", "").lower()
    grain = row.get("grain", "").lower()

    if surface == "fpl" and resource == "bootstrap-static.json":
        return "FPL_BOOTSTRAP_CONTEXT", "Bootstrap-static structural/configuration context; entity identity should not be inferred from grain alone."
    if surface == "fpl" and resource == "element":
        return "FPL_ELEMENT_CONTEXT", "Element resource context; inspect player/fixture-bearing paths before deciding canonical attachment."
    if surface == "fpl" and resource == "squad":
        return "FPL_SQUAD_CONTEXT", "Squad/registration context; likely relationship-rich rather than a standalone player statistic."
    if surface == "fpl" and resource == "player_season":
        return "FPL_PLAYER_SEASON_CONTEXT", "Player-season resource; player relationship should be validated against the player-season identity contract."
    if surface == "fpl" and resource == "player_match":
        return "FPL_PLAYER_MATCH_CONTEXT", "Player-match resource; player and fixture attachment require the existing player-match relationship contract."
    if surface == "frl_local_csv":
        return "FRL_LOCAL_CSV_REVIEW", "Local FRL evidence; inspect existing relationship/identity contract before any promotion."
    return "REVIEW", "Insufficient contextual evidence for a stronger classification."


def main():
    source = rows()
    out = []
    for r in source:
        cls, basis = classify(r)
        out.append({
            "field_name": r.get("field_name", ""),
            "source_surface": r.get("source_surface", ""),
            "resource": r.get("resource", ""),
            "grain": r.get("grain", ""),
            "source_identity_required": r.get("source_identity_required", ""),
            "context_class": cls,
            "basis": basis,
        })
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        cols = list(out[0]) if out else ["field_name"]
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader(); w.writerows(out)
    return out


if __name__ == "__main__":
    rows_out = main()
    print("FRL UNSPECIFIED RELATIONSHIP CONTEXT AUDIT")
    print("=" * 100)
    print(f"Variables reviewed: {len(rows_out)}")
    counts = Counter(r["context_class"] for r in rows_out)
    for k, v in counts.most_common():
        print(f"  {v:5d}  {k}")
    print(f"\nOutput: {OUT}")
    print("Evidence-only contextual classification; no identity inference and no canonical promotion.")
