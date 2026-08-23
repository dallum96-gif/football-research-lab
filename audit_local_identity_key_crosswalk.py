"""Crosswalk local-grain identity-like keys against existing FRL registries.

Read-only/evidence-first. Never assigns canonical identity and never creates a
new relationship contract. It reports whether observed local key vocabularies
have deterministic-looking counterparts in the existing registry artifacts.
"""
from __future__ import annotations

import csv
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = DATA / "local_identity_key_crosswalk.csv"


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def norm(v):
    return str(v or "").strip()


def variants(v):
    s = norm(v)
    if not s:
        return set()
    out = {s, s.lower()}
    if s.isdigit():
        out.add(str(int(s)))
    return out


def values(rows, *names):
    result = set()
    for r in rows:
        for name in names:
            result |= variants(r.get(name))
    return result


def registry_inventory():
    team = read_csv(ROOT / "identity" / "team_seasons.csv")
    player = read_csv(DATA / "identity" / "player_identity_registry.csv")
    fixtures = read_csv(ROOT / "fixtures_master.csv")
    match = read_csv(DATA / "fixture_match_stats.csv")
    return {
        "team_seasons": {
            "team_season_id": values(team, "team_season_id"),
            "local_team_id": values(team, "local_team_id"),
            "club_id": values(team, "club_id"),
            "persistent_team_code": values(team, "persistent_team_code"),
        },
        "player_registry": {
            "source_player_id": values(player, "source_player_id"),
            "team_code": values(player, "team_code"),
        },
        "fixtures_master": {
            "fixture_id": values(fixtures, "fixture_id"),
            "fixture_code": values(fixtures, "fixture_code"),
            "source_match_id": values(match, "source_match_id"),
        },
    }


def source_inventory():
    sources = [
        ("team_match", DATA / "fixture_match_stats.csv", ["fixture_id", "source_match_id", "season"]),
        ("squad", DATA / "live_pl_api_cache" / "team_squad.json", []),
        ("player_season", DATA / "player_season_capability_map.csv", ["field_name"]),
    ]
    out = []
    for grain, path, hinted in sources:
        rows = read_csv(path) if path.suffix.lower() == ".csv" else []
        cols = list(rows[0]) if rows else []
        if path.suffix.lower() == ".json":
            import json
            try:
                obj = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(obj, dict):
                    for v in obj.values():
                        if isinstance(v, list) and v and isinstance(v[0], dict):
                            cols = list(v[0])
                            break
                    if not cols:
                        cols = list(obj)[:100]
                elif isinstance(obj, list) and obj and isinstance(obj[0], dict):
                    cols = list(obj[0])
            except Exception:
                pass
        identity_cols = [c for c in cols if any(t in c.lower() for t in ("id", "code", "team", "club", "player", "fixture", "match", "season"))]
        out.append({"grain": grain, "file": str(path.relative_to(ROOT)), "columns": " | ".join(identity_cols[:40]), "row_count": len(rows)})
    return out


def main():
    inv = registry_inventory()
    src = source_inventory()
    rows = []
    for r in src:
        grain = r["grain"]
        candidates = []
        if grain == "team_match":
            candidates = [
                ("fixture_id", "fixtures_master", inv["fixtures_master"]["fixture_id"]),
                ("source_match_id", "fixture_match_stats", inv["fixtures_master"]["source_match_id"]),
            ]
        elif grain == "squad":
            candidates = [
                ("team_id/code-like", "team_seasons", inv["team_seasons"]["local_team_id"] | inv["team_seasons"]["persistent_team_code"]),
            ]
        elif grain == "player_season":
            candidates = [
                ("source_player_id", "player_registry", inv["player_registry"]["source_player_id"]),
                ("team_code", "player_registry", inv["player_registry"]["team_code"]),
            ]
        for source_key, registry_name, reg_values in candidates:
            rows.append({
                "grain": grain,
                "source_key_candidate": source_key,
                "registry": registry_name,
                "registry_values_present": len(reg_values),
                "potential_key_overlap": "PRESENT" if reg_values else "NONE",
                "canonical_assignment": "NOT_PERFORMED",
            })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        cols = list(rows[0]) if rows else ["grain"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader(); w.writerows(rows)

    print("FRL LOCAL IDENTITY KEY CROSSWALK")
    print("=" * 100)
    print("TEAM_MATCH -> fixture IDs / source match IDs crosswalk against fixture registries")
    print("SQUAD      -> team identity key vocabulary crosswalk against team-season registry")
    print("PLAYER_SEASON -> source player/team keys crosswalk against player registry")
    for r in rows:
        print(f"  {r['grain']:12} {r['source_key_candidate']:24} -> {r['registry']:22} {r['potential_key_overlap']}")
    print(f"\nOutput: {OUT}")
    print("Evidence-only crosswalk; no canonical identity assignment and no contract promotion.")

if __name__ == "__main__":
    main()
