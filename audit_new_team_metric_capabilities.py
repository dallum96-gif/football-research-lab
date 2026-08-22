"""Compare newly discovered live team metrics against the local FRL field universe.

Evidence-first only. Reads local FRL CSV headers when available and records whether
each source metric appears to exist, is obviously derivable, or represents a new
source capability requiring review. No canonical promotion.
"""
from __future__ import annotations
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DISCOVERED = ROOT / "data" / "live_collision_semantic_review.csv"
OUT = ROOT / "data" / "new_team_metric_capability_audit.csv"

FIELDS = [
    "goalConversion", "ownGoalsAccrued", "pointsDroppedFromWinningPositions",
    "pointsGainedFromLosingPositions", "shotsOnConcededInsideBox",
    "shotsOnConcededOutsideBox", "successfulOpenPlayPasses",
    "totalShotsConceded", "unsuccessfulPassesOppositionHalf",
]
DERIVABLE = {
    "totalShotsConceded": ("shotsOnConcededInsideBox", "shotsOnConcededOutsideBox"),
}

def collect_local_fields() -> set[str]:
    fields: set[str] = set()
    for path in ROOT.rglob("*.csv"):
        if "data\" in str(path) or "data/" in str(path):
            if path.name.startswith("live_") or path.name.startswith("new_team_"):
                continue
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as fh:
                reader = csv.reader(fh)
                header = next(reader, [])
                fields.update(x.strip() for x in header if x.strip())
        except Exception:
            continue
    return fields

def run() -> list[dict[str,str]]:
    local = collect_local_fields()
    rows=[]
    for field in FIELDS:
        if field in local:
            status="EXISTING_FIELD"
            reason="Exact native field name appears in local FRL CSV headers."
        elif field in DERIVABLE and all(x in local for x in DERIVABLE[field]):
            status="DERIVABLE"
            reason="Metric has an explicitly documented arithmetic dependency on locally present fields."
        elif field in DERIVABLE:
            status="REVIEW"
            reason="Potentially derivable, but dependency fields are not all present in local headers."
        else:
            status="NEW_SOURCE_CAPABILITY"
            reason="No exact native field found in scanned local CSV headers."
        rows.append({"field_name":field,"status":status,"reason":reason})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer=csv.DictWriter(fh, fieldnames=["field_name","status","reason"])
        writer.writeheader(); writer.writerows(rows)
    return rows

if __name__ == "__main__":
    rows=run()
    print("FRL NEW TEAM METRIC CAPABILITY AUDIT")
    print("="*90)
    for r in rows:
        print(f"  {r['status']:22s} {r['field_name']}")
    print(f"Output: {OUT}")
    print("Evidence/derivability audit only; no semantic or canonical promotion.")
