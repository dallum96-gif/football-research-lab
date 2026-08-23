"""Summarise the local CSV relationship-contract frontier.

Evidence-only. Reads the already-produced audit output when available and groups
frontier variables by resource/grain/relationship metadata so the next audit can
be targeted without inventing contracts.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
INPUT = DATA / "local_csv_relationship_contract_audit.csv"
OUTPUT = DATA / "local_csv_relationship_contract_frontier_summary.csv"


def load() -> list[dict[str, str]]:
    with INPUT.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> None:
    rows = load()
    print("FRL LOCAL CSV RELATIONSHIP CONTRACT FRONTIER")
    print("=" * 100)
    print(f"Variables: {len(rows)}")

    for field in ("resource", "grain", "source_identifier_status", "relationship_contract_status", "identity_contract", "relationship_kind"):
        counts = Counter((r.get(field) or "UNSPECIFIED") for r in rows)
        print(f"\n{field.upper()}")
        for key, value in counts.most_common():
            print(f"  {value:5d}  {key}")

    # Compact resource/grain counts for targeting.
    pairs = Counter((r.get("resource") or "UNSPECIFIED", r.get("grain") or "UNSPECIFIED") for r in rows)
    out = [{"resource": resource, "grain": grain, "variables": count} for (resource, grain), count in sorted(pairs.items(), key=lambda x: (-x[1], x[0]))]
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["resource", "grain", "variables"])
        writer.writeheader()
        writer.writerows(out)
    print(f"\nOutput: {OUTPUT}")
    print("Evidence-only frontier summary; no inferred joins or canonical promotion.")


if __name__ == "__main__":
    main()
