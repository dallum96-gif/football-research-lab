"""Inventory identity-like keys for the local relationship frontier.

Evidence-only. Reads the generated local frontier and inspects matching local
CSV/JSON evidence plus existing identity registries. It reports available keys
and overlaps; it does not declare a relationship contract or infer canonical
identity.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
FRONTIER = DATA / "local_csv_relationship_contract_audit.csv"
OUT = DATA / "local_grain_identity_key_inventory.csv"

TARGET_RESOURCES = {"team_match", "squad", "player_season"}
KEY_TOKENS = (
    "id", "code", "team", "club", "player", "fixture", "match", "season",
    "source", "pl_code", "canonical"
)


def rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def keys_from_csv(path: Path) -> tuple[list[str], int]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            cols = reader.fieldnames or []
            count = sum(1 for _ in reader)
        return cols, count
    except Exception:
        return [], 0


def keys_from_json(path: Path) -> list[str]:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if isinstance(obj, dict):
        for value in obj.values():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                return list(value[0].keys())
        return list(obj.keys())[:100]
    if isinstance(obj, list) and obj and isinstance(obj[0], dict):
        return list(obj[0].keys())
    return []


def identity_like(cols: list[str]) -> list[str]:
    return sorted(c for c in cols if any(t in c.lower() for t in KEY_TOKENS))


def main():
    frontier = rows(FRONTIER)
    resources = Counter(r.get("resource", "") for r in frontier if r.get("resource") in TARGET_RESOURCES)

    candidates: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.name.startswith("."):
            continue
        low = path.name.lower()
        if path.suffix.lower() == ".csv" and any(x in low for x in ("team", "fixture", "squad", "player", "season", "match")):
            candidates.append(path)
        elif path.suffix.lower() == ".json" and any(x in low for x in ("team", "squad", "fixture", "match", "player", "season")):
            candidates.append(path)

    existing_registries = [
        DATA / "identity" / "player_identity_registry.csv",
        ROOT / "identity" / "team_seasons.csv",
        ROOT / "identity" / "team_seasons_provenance.csv",
        ROOT / "fixtures_master.csv",
        DATA / "fixture_match_stats.csv",
    ]

    seen = set()
    results = []
    for path in candidates + existing_registries:
        path = path.resolve()
        if path in seen or not path.exists():
            continue
        seen.add(path)
        if path.suffix.lower() == ".csv":
            cols, count = keys_from_csv(path)
        else:
            cols, count = keys_from_json(path)
        ids = identity_like(cols)
        if ids:
            results.append({
                "file": str(path.relative_to(ROOT)),
                "resource_hints": ",".join(sorted(k for k in resources if k.split("_")[0] in path.name.lower() or k in path.name.lower())) or "",
                "rows_or_objects": count,
                "identity_like_columns": " | ".join(ids[:40]),
                "column_count": len(cols),
            })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        cols = ["file", "resource_hints", "rows_or_objects", "identity_like_columns", "column_count"]
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(results)

    print("FRL LOCAL GRAIN IDENTITY-KEY INVENTORY")
    print("=" * 100)
    print(f"Frontier variables: {len(frontier)}")
    print("RESOURCE")
    for k, v in resources.most_common():
        print(f"  {v:5d}  {k}")
    print(f"\nEvidence files with identity-like keys: {len(results)}")
    for r in results[:25]:
        print(f"  {r['file']} :: {r['identity_like_columns']}")
    print(f"\nOutput: {OUT}")
    print("Evidence-only key inventory; no identity inference and no contract promotion.")


if __name__ == "__main__":
    main()
