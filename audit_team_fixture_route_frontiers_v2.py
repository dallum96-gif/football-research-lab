from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
MATRIX = DATA / "variable_entity_route_verification.csv"
OUT = DATA / "team_fixture_route_frontiers_v2.csv"

def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        r = csv.DictReader(fh)
        return list(r), r.fieldnames or []

def n(v):
    return str(v or "").strip()

def main():
    rows, cols = read_csv(MATRIX)
    frontier = []
    for row in rows:
        for entity in ("TEAM", "FIXTURE"):
            status = n(row.get(f"{entity.lower()}_route_verification")).upper()
            if status == "GRAIN_ROUTE_EVIDENCE_REQUIRED":
                item = dict(row)
                item["target_entity"] = entity
                item["verification_status"] = status
                item["route_evidence_basis"] = n(row.get(f"{entity.lower()}_route_evidence_basis"))
                frontier.append(item)

    print("FRL TEAM / FIXTURE ROUTE EVIDENCE FRONTIER V2")
    print("=" * 100)
    print(f"Variables reviewed: {len(rows)}")
    print(f"Frontier rows: {len(frontier)}")

    by_entity = Counter(n(r.get("target_entity")) for r in frontier)
    print("\nENTITY")
    for k, v in by_entity.most_common(): print(f"{v:5} {k}")

    by = Counter((n(r.get("target_entity")), n(r.get("grain")) or "<blank>") for r in frontier)
    print("\nGRAIN")
    for (e, g), c in sorted(by.items(), key=lambda x: (x[0][0], -x[1], x[0][1])):
        print(f"{e:8} {c:5} grain={g}")

    resources = Counter((n(r.get("target_entity")), n(r.get("resource")) or "<blank>") for r in frontier)
    print("\nRESOURCE")
    for (e, resource), c in sorted(resources.items(), key=lambda x: (x[0][0], -x[1], x[0][1])):
        print(f"{e:8} {c:5} {resource}")

    fields = list(dict.fromkeys(cols + ["target_entity", "verification_status", "route_evidence_basis"]))
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(frontier)

    print(f"\nOutput: {OUT}")
    print("Evidence-only frontier profiling; no inferred joins and no canonical promotion.")

if __name__ == "__main__": main()
