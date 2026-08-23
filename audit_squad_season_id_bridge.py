"""Audit Pulselive squad seasonId -> FRL season mapping using local evidence only.

No mapping is promoted unless an explicit local source/season signal supports it.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "data" / "live_pl_api_cache" / "team_squad.json"


def seasons_from_local_csvs() -> set[str]:
    values: set[str] = set()
    for path in ROOT.rglob("*.csv"):
        if path.is_file():
            try:
                with path.open("r", encoding="utf-8-sig", newline="") as h:
                    reader = csv.DictReader(h)
                    if not reader.fieldnames:
                        continue
                    if "season" in reader.fieldnames:
                        for row in reader:
                            value = str(row.get("season") or "").strip()
                            if value and "-" in value:
                                values.add(value)
            except (OSError, UnicodeDecodeError, csv.Error):
                continue
    return values


def main() -> None:
    print("FRL SQUAD SEASON-ID BRIDGE AUDIT")
    print("=" * 96)
    if not CACHE.is_file():
        print("team_squad.json: MISSING")
        return
    payload = json.loads(CACHE.read_text(encoding="utf-8"))
    squad = payload.get("payload") or {}
    season_id = str((squad.get("id") or {}).get("seasonId") or "").strip()
    team_id = str((squad.get("team") or {}).get("id") or "").strip()
    team_name = str((squad.get("team") or {}).get("name") or "").strip()
    print(f"Pulselive seasonId: {season_id}")
    print(f"Pulselive team: {team_id} ({team_name})")
    print(f"Explicit payload season name: {squad.get('season')!r}")
    print("LOCAL CSV SEASON SIGNALS")
    for season in sorted(seasons_from_local_csvs()):
        print(f"  {season}")
    print()
    print("INTERPRETATION")
    print("  seasonId -> FRL season is NOT promoted by numeric resemblance.")
    print("  A promotion requires an explicit local source mapping or equivalent temporal evidence.")


if __name__ == "__main__":
    main()
