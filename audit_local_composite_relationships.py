"""Audit composite-key and temporal relationships for the local relationship frontier.

Evidence-only and fail-closed. No canonical identity or relationship contract is
created. The audit checks whether the existing local Team-Match and Squad
resources have sufficient keys to distinguish observations and whether their
candidate keys line up with the existing fixture/team-season registries.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = DATA / "local_composite_relationship_audit.csv"


def load(path: Path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def cols(path: Path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh).fieldnames or [])


def unique_count(rows, keys):
    vals = set()
    nonblank = 0
    for r in rows:
        key = tuple((r.get(k) or "").strip() for k in keys)
        if all(key):
            nonblank += 1
            vals.add(key)
    return len(vals), nonblank


def duplicate_count(rows, keys):
    seen = Counter()
    for r in rows:
        key = tuple((r.get(k) or "").strip() for k in keys)
        if all(key):
            seen[key] += 1
    return sum(1 for v in seen.values() if v > 1), max(seen.values(), default=0)


def season_consistency(rows, entity_keys, season_key="season"):
    seen = {}
    contradictions = 0
    for r in rows:
        k = tuple((r.get(x) or "").strip() for x in entity_keys)
        s = (r.get(season_key) or "").strip()
        if not all(k) or not s:
            continue
        prior = seen.setdefault(k, set())
        if prior and s not in prior:
            contradictions += 1
        prior.add(s)
    return contradictions, len(seen)


def main():
    team_match = DATA / "fixture_match_stats.csv"
    team_match_rows = load(team_match)
    team_match_cols = cols(team_match)
    fixtures = ROOT / "fixtures_master.csv"
    fixture_rows = load(fixtures)
    fixture_cols = cols(fixtures)
    teams = ROOT / "identity" / "team_seasons.csv"
    team_rows = load(teams)
    team_cols = cols(teams)

    print("FRL LOCAL COMPOSITE RELATIONSHIP AUDIT")
    print("=" * 100)
    print(f"Team-Match rows: {len(team_match_rows)}")
    print(f"Team-Match columns: {len(team_match_cols)}")

    tm_keys = [
        ("fixture_id",),
        ("source_match_id",),
        ("fixture_id", "season"),
        ("source_match_id", "season"),
    ]

    for keys in tm_keys:
        if all(k in team_match_cols for k in keys):
            u, nb = unique_count(team_match_rows, keys)
            d, mx = duplicate_count(team_match_rows, keys)
            print(f"TEAM_MATCH key={'+'.join(keys):30} unique={u:6d} nonblank={nb:6d} duplicate_keys={d:6d} max_frequency={mx:3d}")

    print("\nFIXTURE REGISTRY")
    print(f"Rows: {len(fixture_rows)} | columns: {', '.join(fixture_cols)}")
    if "fixture_id" in team_match_cols and "fixture_id" in fixture_cols:
        tm_ids = {r.get("fixture_id", "").strip() for r in team_match_rows if r.get("fixture_id", "").strip()}
        fx_ids = {r.get("fixture_id", "").strip() for r in fixture_rows if r.get("fixture_id", "").strip()}
        print(f"fixture_id overlap: {len(tm_ids & fx_ids)}")
        print(f"fixture_id Team-Match-only: {len(tm_ids - fx_ids)}")
        print(f"fixture_id registry-only: {len(fx_ids - tm_ids)}")

    if "source_match_id" in team_match_cols:
        src = {r.get("source_match_id", "").strip() for r in team_match_rows if r.get("source_match_id", "").strip()}
        print(f"source_match_id distinct: {len(src)}")

    print("\nTEMPORAL TEAM-MATCH CHECK")
    contradictions, entities = season_consistency(team_match_rows, ["fixture_id"] if "fixture_id" in team_match_cols else []) if "fixture_id" in team_match_cols else (0,0)
    print(f"fixture_id mapped to multiple seasons within Team-Match: {contradictions}")
    print(f"distinct fixture_id entities observed: {entities}")

    print("\nSQUAD / TEAM-SEASON REGISTRY")
    print(f"team_seasons rows: {len(team_rows)} | columns: {', '.join(team_cols)}")
    squad_candidates = [("team_id",), ("team_id", "season"), ("team_code",), ("team_code", "season"), ("code",), ("code", "season")]
    # Locate squad files locally and inspect only likely squad resources.
    squad_paths = []
    for p in ROOT.rglob("*.csv"):
        if "squad" in p.name.lower() and "team_seasons" not in p.name.lower():
            squad_paths.append(p)
    print(f"candidate squad files: {len(squad_paths)}")
    for p in sorted(squad_paths)[:20]:
        r = load(p)
        c = cols(p)
        print(f"  {p.relative_to(ROOT)} :: rows={len(r)} columns={','.join(c[:20])}")
        for keys in squad_candidates:
            if all(k in c for k in keys):
                u, nb = unique_count(r, keys)
                d, mx = duplicate_count(r, keys)
                print(f"    key={'+'.join(keys):20} unique={u:6d} nonblank={nb:6d} duplicate_keys={d:6d} max_frequency={mx:3d}")

    rows = []
    for keys, status in [
        (("fixture_id",), "FIXTURE_ID_CANDIDATE"),
        (("source_match_id",), "SOURCE_MATCH_ID_CANDIDATE"),
        (("fixture_id", "season"), "FIXTURE_SEASON_COMPOSITE"),
        (("source_match_id", "season"), "SOURCE_MATCH_SEASON_COMPOSITE"),
    ]:
        if all(k in team_match_cols for k in keys):
            u, nb = unique_count(team_match_rows, keys)
            d, mx = duplicate_count(team_match_rows, keys)
            rows.append({"grain":"team_match","candidate_key":"+".join(keys),"status":status,"unique_keys":u,"nonblank_rows":nb,"duplicate_keys":d,"max_frequency":mx})

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["grain","candidate_key","status","unique_keys","nonblank_rows","duplicate_keys","max_frequency"])
        writer.writeheader(); writer.writerows(rows)

    print(f"\nOutput: {OUT}")
    print("Evidence-only composite/temporal audit; no identity inference and no contract promotion.")


if __name__ == "__main__":
    main()
