"""Summarise the local-CSV relationship-contract frontier.

Evidence-only. Reads data/local_csv_relationship_contract_audit.csv and reports
how the 86 local-CSV frontier variables distribute across existing relationship
contracts, source-local identifiers, grains, resources and unresolved states.
No inferred joins and no canonical promotion.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
INPUT = DATA / "local_csv_relationship_contract_audit.csv"
OUTPUT = DATA / "local_csv_relationship_contract_summary.csv"


def load() -> list[dict[str, str]]:
    with INPUT.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def first(row: dict[str, str], *keys: str) -> str:
    for k in keys:
        v = str(row.get(k) or "").strip()
        if v:
            return v
    return ""


def main() -> list[dict[str, str]]:
    rows = load()
    out: list[dict[str, str]] = []
    for r in rows:
        out.append({
            "field_name": first(r, "field_name"),
            "source_surface": first(r, "source_surface"),
            "resource": first(r, "resource"),
            "grain": first(r, "grain"),
            "source_identifier_status": first(r, "source_identifier_status", "source_identity_status"),
            "relationship_contract_status": first(r, "relationship_contract_status", "contract_status"),
            "identity_contract": first(r, "identity_contract"),
            "relationship_kind": first(r, "relationship_kind"),
            "canonical_attachment": first(r, "canonical_attachment"),
            "relationship_note": first(r, "relationship_note"),
        })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    cols = list(out[0]) if out else ["field_name"]
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        writer.writerows(out)
    return out


def print_counts(rows: list[dict[str, str]], field: str) -> None:
    c = Counter(r.get(field, "") or "UNSPECIFIED" for r in rows)
    print(f"\n{field.upper()}")
    for k, v in c.most_common():
        print(f"  {v:5d}  {k}")


if __name__ == "__main__":
    rows = main()
    print("FRL LOCAL CSV RELATIONSHIP CONTRACT SUMMARY")
    print("=" * 100)
    print(f"Variables summarised: {len(rows)}")
    for field in ("source_surface", "resource", "grain", "source_identifier_status", "relationship_contract_status", "identity_contract", "relationship_kind"):
        print_counts(rows, field)
    print(f"\nOutput: {OUTPUT}")
    print("Evidence-only summary; no inferred joins and no canonical promotion.")
