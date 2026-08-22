"""Audit the 21 FRL_LOCAL_CSV relationship-review variables against existing contracts.

Evidence-first only. Reads local frl-source-audit artefacts when executed there.
It identifies source files/columns, candidate identity-bearing columns, and existing
FRL relationship/identity contracts. It never invents joins or promotes identities.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
FRONTIER = DATA / "relationship_metadata_review_frontier.csv"
OUT = DATA / "local_csv_relationship_contract_audit.csv"

KEYWORDS = (
    "player", "player_id", "player_code", "pl_code", "team", "team_id", "team_code",
    "club", "club_id", "fixture", "fixture_id", "match", "match_id", "source_match_id",
    "season", "name", "canonical", "relationship", "identity"
)


def load(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> list[dict[str, str]]:
    frontier = [r for r in load(FRONTIER) if r.get("source_surface") == "FRL_LOCAL_CSV"]
    universe = load(DATA / "master_variable_universe_decomposed.csv")
    dictionary = load(DATA / "frl_variable_dictionary.csv")

    by_field = {r.get("field_name", ""): r for r in universe if r.get("field_name")}
    dict_by_field = {r.get("field_name", ""): r for r in dictionary if r.get("field_name")}

    rows = []
    for f in frontier:
        field = f.get("field_name", "")
        u = by_field.get(field, {})
        d = dict_by_field.get(field, {})
        source_surface = u.get("source_surface", f.get("source_surface", ""))
        resource = u.get("resource", f.get("resource", ""))
        grain = u.get("decomposed_grain", u.get("grain", f.get("grain", "")))
        candidates = []
        for path in sorted(ROOT.rglob("*.csv")):
            try:
                with path.open("r", encoding="utf-8-sig", newline="") as fh:
                    cols = fh.readline().strip().split(",")
            except Exception:
                continue
            hits = [c for c in cols if any(k in c.lower() for k in KEYWORDS)]
            if hits:
                candidates.append(f"{path.relative_to(ROOT)}::{ '|'.join(hits[:20]) }")

        explicit_contract = " | ".join(x for x in (
            d.get("canonical_attachment", ""), d.get("relationship_kind", ""),
            d.get("identity_contract", ""), d.get("source_identity_required", ""),
            d.get("relationship_note", "")
        ) if x)

        rows.append({
            "field_name": field,
            "resource": resource,
            "grain": grain,
            "existing_contract": explicit_contract,
            "identity_candidate_files": " || ".join(candidates[:15]),
            "resolution": "REVIEW_REQUIRED",
            "basis": "Local CSV relationship frontier; source file/identifier context must be inspected before any canonical attachment claim."
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    cols = list(rows[0]) if rows else ["field_name"]
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader(); writer.writerows(rows)
    return rows

if __name__ == "__main__":
    rows = main()
    print("FRL LOCAL CSV RELATIONSHIP CONTRACT AUDIT")
    print("=" * 100)
    print(f"Local CSV frontier variables: {len(rows)}")
    print(f"Output: {OUT}")
    print("Evidence-only; no inferred joins and no canonical promotion.")
