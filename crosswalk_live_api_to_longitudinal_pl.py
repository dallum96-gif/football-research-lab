"""Crosswalk live Premier League API fields against historical PL/PulseLive fields.

Exact native/path comparison first. No semantic equivalence or canonical promotion.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LIVE = ROOT / "data" / "live_premier_league_api_surface.csv"
HIST = ROOT / "data" / "upstream_pl_stats_schema_by_season.csv"
OUT = ROOT / "data" / "live_api_vs_longitudinal_pl.csv"


def terminal_name(path: str) -> str:
    if not path:
        return ""
    return path.split(".")[-1].replace("[]", "")


def load_live(path: Path = LIVE) -> set[tuple[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        rows = csv.DictReader(fh)
        return {
            (r.get("endpoint_name", ""), terminal_name(r.get("field_path", "")))
            for r in rows
            if r.get("endpoint_name") and r.get("field_path")
        }


def load_hist(path: Path = HIST) -> set[tuple[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return {
            (r.get("grain", ""), r.get("field_name", ""))
            for r in csv.DictReader(fh)
            if r.get("grain") and r.get("field_name")
        }


def compare(live: set[tuple[str, str]], hist: set[tuple[str, str]]) -> list[dict[str, str]]:
    """Compare on native field name only, retaining endpoint/grain as provenance context."""
    live_fields = {field for _, field in live}
    hist_fields = {field for _, field in hist}
    rows: list[dict[str, str]] = []
    for field in sorted(live_fields | hist_fields):
        in_live = field in live_fields
        in_hist = field in hist_fields
        if in_live and in_hist:
            state = "BOTH"
        elif in_live:
            state = "LIVE_ONLY"
        else:
            state = "HISTORICAL_ONLY"
        live_context = sorted(resource for resource, f in live if f == field)
        hist_context = sorted(grain for grain, f in hist if f == field)
        rows.append({
            "field_name": field,
            "state": state,
            "live_endpoints": " | ".join(live_context),
            "historical_grains": " | ".join(hist_context),
        })
    return rows


def main() -> None:
    live = load_live()
    hist = load_hist()
    rows = compare(live, hist)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["field_name", "state", "live_endpoints", "historical_grains"],
        )
        writer.writeheader()
        writer.writerows(rows)

    counts = Counter(r["state"] for r in rows)
    print("FRL LIVE API VS LONGITUDINAL PL/PULSELIVE CROSSWALK")
    print("=" * 90)
    print(f"Live API native fields:       {len({f for _, f in live})}")
    print(f"Historical native fields:     {len({f for _, f in hist})}")
    print(f"BOTH:                          {counts['BOTH']}")
    print(f"LIVE_ONLY:                     {counts['LIVE_ONLY']}")
    print(f"HISTORICAL_ONLY:               {counts['HISTORICAL_ONLY']}")
    print("\nLIVE_ONLY BY ENDPOINT")
    live_only = [r for r in rows if r["state"] == "LIVE_ONLY"]
    by_endpoint = Counter(
        endpoint
        for row in live_only
        for endpoint in row["live_endpoints"].split(" | ")
        if endpoint
    )
    for endpoint, count in by_endpoint.most_common():
        print(f"  {count:4d}  {endpoint}")
    print(f"\nOutput: {OUT}")
    print("Native field-name comparison; endpoint/grain provenance retained; no semantic promotion.")


if __name__ == "__main__":
    main()
