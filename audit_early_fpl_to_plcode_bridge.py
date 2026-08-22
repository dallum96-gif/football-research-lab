"""Read-only audit of the early-season FPL -> PL player-code bridge.

No identity promotion or canonical writes occur here.
"""
from __future__ import annotations

from collections import defaultdict
import csv
from pathlib import Path

import player_research
from player_identity_crosswalk import SEASONS

ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = ROOT.parent / "Premier-League-Stats" / "pl_stats"
MERGED_PLAYER_DIR = SOURCE_ROOT / "_merged" / "players"


def load_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def norm(value: object) -> str:
    return " ".join(str(value or "").strip().casefold().replace("_", " ").split())


def distinct_fpl(season: str) -> list[dict]:
    rows: dict[str, dict] = {}
    for row in player_research._load_season_rows(season):
        element = str(row.get("element") or row.get("player_code") or "").strip()
        if element:
            rows.setdefault(element, row)
    return list(rows.values())


def audit_season(season: str) -> dict:
    path = MERGED_PLAYER_DIR / f"{season}_players_stats.csv"
    merged = load_csv(path)
    fpl = distinct_fpl(season)

    by_pl_code: dict[str, set[str]] = defaultdict(set)
    by_name: dict[str, set[str]] = defaultdict(set)
    by_id: dict[str, dict] = {}
    for row in merged:
        sid = str(row.get("playerId") or "").strip()
        pl = str(row.get("pl_code") or "").strip()
        name = norm(row.get("playerName"))
        if sid:
            by_id[sid] = row
        if pl and sid:
            by_pl_code[pl].add(sid)
        if name and sid:
            by_name[name].add(sid)

    plcode_matches = 0
    plcode_ambiguous = 0
    plcode_missing = 0
    examples = []

    for row in fpl:
        element = str(row.get("element") or row.get("player_code") or "").strip()
        candidates = sorted(by_pl_code.get(element, set()))
        if not candidates:
            plcode_missing += 1
        elif len(candidates) == 1:
            plcode_matches += 1
        else:
            plcode_ambiguous += 1
            if len(examples) < 10:
                examples.append((element, candidates))

    return {
        "season": season,
        "fpl": len(fpl),
        "merged": len(merged),
        "plcode_matches": plcode_matches,
        "plcode_ambiguous": plcode_ambiguous,
        "plcode_missing": plcode_missing,
        "examples": examples,
    }


def main() -> None:
    print("=" * 96)
    print("FRL EARLY-SEASON FPL -> PL_CODE -> PLAYER_ID BRIDGE AUDIT")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 96)
    totals = {"fpl": 0, "merged": 0, "matches": 0, "ambiguous": 0, "missing": 0}
    for season in SEASONS[:4]:
        result = audit_season(season)
        totals["fpl"] += result["fpl"]
        totals["merged"] += result["merged"]
        totals["matches"] += result["plcode_matches"]
        totals["ambiguous"] += result["plcode_ambiguous"]
        totals["missing"] += result["plcode_missing"]
        print(f"{season}: FPL={result['fpl']} merged={result['merged']}")
        print(f"  PL_CODE_MATCH={result['plcode_matches']} AMBIGUOUS={result['plcode_ambiguous']} MISSING={result['plcode_missing']}")
        if result["examples"]:
            print(f"  ambiguous sample={result['examples']}")
    print("\nTOTALS:")
    print(f"  FPL identities:   {totals['fpl']:,}")
    print(f"  Merged players:   {totals['merged']:,}")
    print(f"  PL_CODE matches:  {totals['matches']:,}")
    print(f"  Ambiguous:        {totals['ambiguous']:,}")
    print(f"  Missing:          {totals['missing']:,}")
    print("\nNo files were written or modified.")
    print("=" * 96)


if __name__ == "__main__":
    main()
