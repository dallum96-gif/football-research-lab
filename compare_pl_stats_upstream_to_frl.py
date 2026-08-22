"""Compare sampled upstream PL/PulseLive variables with the FRL local catalog.

Exact grain + native field-name comparison only. No semantic equivalence is inferred.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
UPSTREAM = ROOT / "frl-source-audit" / "data" / "upstream_pl_stats_variable_universe.csv"
FRL_LOCAL = ROOT / "frl-source-audit" / "data" / "master_variable_universe.csv"
OUTPUT = ROOT / "frl-source-audit" / "data" / "pl_stats_vs_frl_catalog.csv"


def load_upstream(path: Path = UPSTREAM) -> set[tuple[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        rows = csv.DictReader(fh)
        return {(r["grain"], r["field_name"]) for r in rows if r.get("grain") and r.get("field_name")}


def load_frl(path: Path = FRL_LOCAL) -> set[tuple[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        rows = csv.DictReader(fh)
        return {(r["grain"], r["field_name"]) for r in rows if r.get("grain") and r.get("field_name")}


def compare(upstream: set[tuple[str, str]], frl: set[tuple[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for grain, field in sorted(upstream | frl):
        in_upstream = (grain, field) in upstream
        in_frl = (grain, field) in frl
        if in_upstream and in_frl:
            state = "BOTH"
        elif in_upstream:
            state = "UPSTREAM_ONLY"
        else:
            state = "FRL_ONLY"
        rows.append({"grain": grain, "field_name": field, "state": state})
    return rows


def main() -> None:
    upstream = load_upstream()
    frl = load_frl()
    rows = compare(upstream, frl)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["grain", "field_name", "state"])
        writer.writeheader()
        writer.writerows(rows)

    counts = Counter(r["state"] for r in rows)
    print("FRL VS UPSTREAM PL_STATS VARIABLE CROSSWALK")
    print("=" * 90)
    print(f"Upstream sampled variables: {len(upstream)}")
    print(f"FRL local variables:        {len(frl)}")
    print(f"BOTH:                       {counts['BOTH']}")
    print(f"UPSTREAM_ONLY:              {counts['UPSTREAM_ONLY']}")
    print(f"FRL_ONLY:                   {counts['FRL_ONLY']}")
    print(f"Output: {OUTPUT}")
    print("Exact grain + native field-name comparison; no semantic promotion.")


if __name__ == "__main__":
    main()
