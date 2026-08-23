"""Read-only inspection of the local team_squad payload shape.

Checks team identity, player identity keys, temporal/request context, and
candidate compatibility with the existing team-season registry without
promoting any relationship.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "data" / "live_pl_api_cache" / "team_squad.json"
TEAM_SEASONS = ROOT / "identity" / "team_seasons.csv"


def _walk(value, prefix=""):
    if isinstance(value, dict):
        for k, v in value.items():
            path = f"{prefix}.{k}" if prefix else k
            yield path, v
            yield from _walk(v, path)
    elif isinstance(value, list) and value:
        yield from _walk(value[0], f"{prefix}[0]")


def main() -> None:
    print("FRL SQUAD PAYLOAD IDENTITY / TEMPORAL CONTEXT AUDIT")
    print("=" * 96)
    print(f"FILE: {CACHE}")
    if not CACHE.is_file():
        print("EXISTS=False")
        return
    payload = json.loads(CACHE.read_text(encoding="utf-8"))
    print(f"EXISTS=True type={type(payload).__name__}")
    print(f"TOP_KEYS={list(payload)[:20] if isinstance(payload, dict) else []}")

    paths = list(_walk(payload))
    wanted = ("team", "teamId", "teamCode", "season", "seasonId", "playerId", "id", "name", "player")
    print("\nIDENTITY / TEMPORAL PATHS")
    seen = set()
    for path, value in paths:
        if any(token.lower() in path.lower() for token in wanted):
            key = (path, type(value).__name__, str(value)[:120])
            if key in seen:
                continue
            seen.add(key)
            print(f"  {path} :: {type(value).__name__} :: {str(value)[:120]}")

    print("\nTEAM-SEASON REGISTRY AVAILABILITY")
    print(f"registry_exists={TEAM_SEASONS.is_file()}")
    if TEAM_SEASONS.is_file():
        import csv
        with TEAM_SEASONS.open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            rows = list(reader)
        print(f"registry_rows={len(rows)}")
        print(f"registry_columns={reader.fieldnames or []}")

    print("\nINTERPRETATION")
    print("Evidence only. No season inferred from a live/current squad payload.")
    print("No team identity promoted unless an explicit season-local team key is present and compatible with the existing registry.")
    print("No player identity promoted from name alone.")


if __name__ == "__main__":
    main()
