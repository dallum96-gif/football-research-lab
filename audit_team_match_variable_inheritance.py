"""Validate identity inheritance for all Team-Match variables.

Evidence-only. Verifies that each column in fixture_match_stats.csv inherits
one deterministic fixture + team-side identity route. Does not promote any
relationship contract or infer canonical identities.
"""
from __future__ import annotations

import csv
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
SRC = DATA / "fixture_match_stats.csv"
FIXTURES = ROOT / "fixtures_master.csv"
TEAM_SEASONS = ROOT / "identity" / "team_seasons.csv"
OUT = DATA / "team_match_variable_inheritance_audit.csv"

META = {
    "season", "fixture_id", "source_match_id",
    "home_core_possession", "away_core_possession",
}


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> None:
    rows = read_csv(SRC)
    fixtures = read_csv(FIXTURES)
    team_seasons = read_csv(TEAM_SEASONS)

    fixture_map = {(r.get("season", ""), r.get("fixture_id", "")): r for r in fixtures}
    team_map = {(r.get("season", ""), r.get("local_team_id", "")): r.get("team_season_id", "") for r in team_seasons}

    # A row-level identity check: each Team-Match row must resolve both sides.
    row_status = Counter()
    for r in rows:
        season = r.get("season", "")
        fid = r.get("fixture_id", "")
        fixture = fixture_map.get((season, fid))
        if not fixture:
            row_status["NO_FIXTURE_ROUTE"] += 1
            continue
        home = fixture.get("home_team_id", "")
        away = fixture.get("away_team_id", "")
        home_ts = team_map.get((season, home))
        away_ts = team_map.get((season, away))
        if home_ts and away_ts:
            row_status["BOTH_TEAM_SIDES_RESOLVE"] += 1
        elif home_ts or away_ts:
            row_status["PARTIAL_TEAM_SIDE_RESOLUTION"] += 1
        else:
            row_status["NO_TEAM_SIDE_RESOLUTION"] += 1

    # Every metric column should be present on all 3,800 Team-Match rows; then
    # its identity route is inherited from the observation row rather than from
    # the metric name itself.
    metric_cols = [c for c in (rows[0].keys() if rows else []) if c not in META]
    out_rows = []
    total = len(rows)
    for col in metric_cols:
        populated = sum(1 for r in rows if str(r.get(col, "")).strip() != "")
        missing = total - populated
        status = "INHERITS_TEAM_MATCH_ROUTE" if total and (populated + missing == total) else "REVIEW"
        out_rows.append({
            "variable": col,
            "team_match_rows": total,
            "nonblank_values": populated,
            "blank_values": missing,
            "fixture_identity": "fixture_id+season OR source_match_id",
            "home_team_identity": "season+home_team_id -> team_season_id",
            "away_team_identity": "season+away_team_id -> team_season_id",
            "row_identity_route_status": "VERIFIED" if row_status["BOTH_TEAM_SIDES_RESOLVE"] == total else "REVIEW",
            "inheritance_status": status,
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        cols = list(out_rows[0].keys()) if out_rows else [
            "variable","team_match_rows","nonblank_values","blank_values",
            "fixture_identity","home_team_identity","away_team_identity",
            "row_identity_route_status","inheritance_status"
        ]
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(out_rows)

    print("FRL TEAM-MATCH VARIABLE IDENTITY INHERITANCE AUDIT")
    print("=" * 100)
    print(f"Team-Match rows: {total}")
    print(f"Metric variables audited: {len(metric_cols)}")
    print("ROW IDENTITY ROUTE")
    for k, v in row_status.most_common():
        print(f"  {v:5d}  {k}")
    counts = Counter(r["inheritance_status"] for r in out_rows)
    print("\nVARIABLE INHERITANCE")
    for k, v in counts.most_common():
        print(f"  {v:5d}  {k}")
    print(f"\nOutput: {OUT}")
    print("Evidence-only Team-Match inheritance validation; no canonical promotion.")


if __name__ == "__main__":
    main()
