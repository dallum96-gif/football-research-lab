"""Audit whether squad-grain variables inherit a deterministic Team-Season identity route.

Evidence-only. No canonical relationship promotion.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
FRONTIER = DATA / "local_csv_relationship_contract_audit.csv"
TEAM_SEASONS = ROOT / "identity" / "team_seasons.csv"
OUT = DATA / "squad_variable_inheritance_audit.csv"


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def main():
    frontier = [r for r in read_csv(FRONTIER) if r.get("resource") == "squad"]
    registry = read_csv(TEAM_SEASONS)

    # We do not guess the underlying squad evidence file. The prior audit proved
    # the identity vocabulary but did not expose a single squad CSV. This audit
    # therefore validates inheritance at the contract/grain level from the
    # frontier's declared resource and registry coverage rather than inventing
    # row-level matches.
    registry_keys = {(r.get("season", ""), r.get("local_team_id", "")) for r in registry}
    populated_registry_keys = {k for k in registry_keys if all(k)}

    print("FRL SQUAD VARIABLE IDENTITY INHERITANCE AUDIT")
    print("=" * 100)
    print(f"Squad frontier variables: {len(frontier)}")
    print(f"Team-season registry rows: {len(registry)}")
    print(f"Season + local_team_id registry keys: {len(populated_registry_keys)}")
    print("\nROUTE")
    print("  candidate: season + local_team_id -> team_season_id")
    print("  status: ROW_LEVEL_EVIDENCE_NOT_AVAILABLE")
    print("\nVARIABLE INHERITANCE")
    print(f"  {len(frontier):5d}  INHERITANCE_REQUIRES_SQUAD_ROW_EVIDENCE")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    cols = ["field_name", "resource", "grain", "identity_route", "inheritance_status", "reason"]
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in frontier:
            w.writerow({
                "field_name": r.get("field_name", ""),
                "resource": "squad",
                "grain": "squad",
                "identity_route": "season + local_team_id -> team_season_id",
                "inheritance_status": "INHERITANCE_REQUIRES_SQUAD_ROW_EVIDENCE",
                "reason": "No single squad row evidence source was identified by the prior audit; no row-level inheritance claim is made.",
            })

    print(f"\nOutput: {OUT}")
    print("Evidence-only Squad inheritance audit; no canonical promotion.")


if __name__ == "__main__":
    main()
