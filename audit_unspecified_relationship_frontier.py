"""Profile variables whose relationship metadata is still unspecified.

Evidence-first only. Reads the existing relationship metadata frontier and the
master variable universe/dictionary, then groups the 192 variables with
UNKNOWN relationship_kind and UNSPECIFIED identity_contract by source surface,
resource, grain and source identity requirements. No joins or identity claims
are inferred.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
FRONTIER = DATA / "relationship_metadata_review_frontier.csv"
OUT = DATA / "unspecified_relationship_frontier.csv"


def load(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def val(row: dict[str, str], *keys: str) -> str:
    for key in keys:
        v = str(row.get(key) or "").strip()
        if v:
            return v
    return ""


def main() -> list[dict[str, str]]:
    rows = load(FRONTIER)
    unknown = [
        r for r in rows
        if val(r, "relationship_kind") in {"", "UNKNOWN"}
        and val(r, "identity_contract") in {"", "UNSPECIFIED"}
    ]

    out = []
    for r in unknown:
        out.append({
            "field_name": val(r, "field_name"),
            "source_surface": val(r, "source_surface"),
            "grain": val(r, "grain"),
            "resource": val(r, "resource"),
            "source_identity_required": val(r, "source_identity_required"),
            "relationship_note": val(r, "relationship_note"),
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    cols = list(out[0]) if out else ["field_name"]
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(out)
    return out


if __name__ == "__main__":
    rows = main()
    print("FRL UNSPECIFIED RELATIONSHIP FRONTIER")
    print("=" * 100)
    print(f"Variables with UNKNOWN relationship kind + UNSPECIFIED identity contract: {len(rows)}")

    for label, fn in [
        ("SOURCE SURFACE", lambda r: r["source_surface"] or "UNKNOWN"),
        ("GRAIN", lambda r: r["grain"] or "UNKNOWN"),
        ("RESOURCE", lambda r: r["resource"] or "UNKNOWN"),
        ("SOURCE IDENTITY REQUIRED", lambda r: r["source_identity_required"] or "UNSPECIFIED"),
    ]:
        counts = Counter(fn(r) for r in rows)
        print(f"\n{label}")
        for key, value in counts.most_common(20):
            print(f"  {value:5d}  {key}")

    print(f"\nOutput: {OUT}")
    print("Evidence-only profiling; no inferred identity or relationship claims.")
