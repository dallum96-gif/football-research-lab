"""Crosswalk live Premier League API fields against historical PL/PulseLive fields.

Exact native field-name comparison. No semantic equivalence or canonical promotion.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LIVE = ROOT / "data" / "live_premier_league_api_surface.csv"
HIST = ROOT / "data" / "upstream_pl_stats_schema_by_season.csv"
OUT = ROOT / "data" / "live_api_vs_longitudinal_pl.csv"


def load_live(path: Path = LIVE) -> set[tuple[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return {
            (r.get("resource", ""), r.get("field_name", ""))
            for r in csv.DictReader(fh)
            if r.get("resource") and r.get("field_name")
        }


def load_hist(path: Path = HIST) -> set[tuple[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return {
            (r.get("grain", ""), r.get("field_name", ""))
            for r in csv.DictReader(fh)
            if r.get("grain") and r.get("field_name")
        }


def compare(live: set[tuple[str, str]], hist: set[tuple[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for resource, field in sorted(live | hist):
        in_live = (resource, field) in live
        in_hist = (resource, field) in hist
        if in_live and in_hist:
            state = "BOTH"
        elif in_live:
            state = "LIVE_ONLY"
        else:
            state = "HISTORICAL_ONLY"
        rows.append({"resource_or_grain": resource, "field_name": field, "state": state})
    return rows


def main() -> None:
    live = load_live()
    hist = load_hist()
    rows = compare(live, hist)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["resource_or_grain", "field_name", "state"])
        writer.writeheader()
        writer.writerows(rows)

    counts = Counter(r["state"] for r in rows)
    print("FRL LIVE API VS LONGITUDINAL PL/PULSELIVE CROSSWALK")
    print("=" * 90)
    print(f"Live API variables:          {len(live)}")
    print(f"Historical variables:        {len(hist)}")
    print(f"BOTH:                         {counts['BOTH']}")
    print(f"LIVE_ONLY:                    {counts['LIVE_ONLY']}")
    print(f"HISTORICAL_ONLY:              {counts['HISTORICAL_ONLY']}")
    print("\nLIVE_ONLY BY RESOURCE")
    live_only = [r for r in rows if r["state"] == "LIVE_ONLY"]
    by_resource = Counter(r["resource_or_grain"] for r in live_only)
    for resource, count in by_resource.most_common():
        print(f"  {count:4d}  {resource}")
    print(f"\nOutput: {OUT}")
    print("Exact native field-name comparison; no semantic promotion.")


if __name__ == "__main__":
    main()
