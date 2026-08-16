"""Read-only audit of FPL player identity fields by season.

The audit keeps FPL ``element`` and ``player_code`` separate and tests their
actual population, within-season uniqueness, cross-season reuse and relationship.
It does not modify data or promote any identity mapping.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

import player_research

PL_ROOT = Path(r"C:\Users\dlall\football_database\Premier-League-Stats\pl_stats")
SEASONS = tuple(player_research.available_seasons())


def open_csv(path: Path):
    last = None
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            handle = path.open("r", encoding=encoding, newline="")
            reader = csv.DictReader(handle)
            _ = reader.fieldnames
            return handle, reader
        except UnicodeDecodeError as exc:
            last = exc
            try:
                handle.close()
            except Exception:
                pass
    raise ValueError(f"Could not decode {path}") from last


def season_rows(season: str):
    # Use the existing Player Research loader so the audit sees the same FPL
    # source files the application already treats as authoritative.
    return player_research._load_season_rows(season)


def norm(value) -> str:
    return str(value or "").strip()


def audit_season(season: str) -> dict:
    rows = list(season_rows(season))

    element_values = [norm(row.get("element")) for row in rows if norm(row.get("element"))]
    player_code_values = [norm(row.get("player_code")) for row in rows if norm(row.get("player_code"))]

    element_counts = Counter(element_values)
    player_code_counts = Counter(player_code_values)

    relationship = Counter()
    code_to_elements = defaultdict(set)
    element_to_codes = defaultdict(set)

    for row in rows:
        element = norm(row.get("element"))
        code = norm(row.get("player_code"))
        if element and code:
            code_to_elements[code].add(element)
            element_to_codes[element].add(code)
            relationship["both"] += 1
        elif element:
            relationship["element_only"] += 1
        elif code:
            relationship["player_code_only"] += 1
        else:
            relationship["neither"] += 1

    return {
        "season": season,
        "rows": len(rows),
        "element_populated": len(element_values),
        "element_unique": len(set(element_values)),
        "element_duplicate_values": sorted(k for k, v in element_counts.items() if v > 1),
        "player_code_present": "player_code" in (rows[0].keys() if rows else []),
        "player_code_populated": len(player_code_values),
        "player_code_unique": len(set(player_code_values)),
        "player_code_duplicate_values": sorted(k for k, v in player_code_counts.items() if v > 1),
        "relationship": dict(relationship),
        "code_to_elements_multi": {
            code: sorted(elements)
            for code, elements in code_to_elements.items()
            if len(elements) > 1
        },
        "element_to_codes_multi": {
            element: sorted(codes)
            for element, codes in element_to_codes.items()
            if len(codes) > 1
        },
    }


def cross_season(results: dict[str, dict]) -> dict:
    element_seasons = defaultdict(set)
    code_seasons = defaultdict(set)

    # Reload rows to retain actual values across the ten historical seasons.
    for season in SEASONS:
        for row in season_rows(season):
            element = norm(row.get("element"))
            code = norm(row.get("player_code"))
            if element:
                element_seasons[element].add(season)
            if code:
                code_seasons[code].add(season)

    return {
        "element_reused_across_seasons": {
            value: sorted(seasons)
            for value, seasons in element_seasons.items()
            if len(seasons) > 1
        },
        "player_code_reused_across_seasons": {
            value: sorted(seasons)
            for value, seasons in code_seasons.items()
            if len(seasons) > 1
        },
    }


def run_audit() -> dict:
    seasons = {season: audit_season(season) for season in SEASONS}
    return {
        "seasons": seasons,
        "cross_season": cross_season(seasons),
    }


def print_report(report: dict) -> None:
    print("=" * 96)
    print("FRL / FPL PLAYER IDENTITY SCHEMA AUDIT")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 96)
    print()

    for season, result in report["seasons"].items():
        print(f"{season}")
        print(f"  rows:                         {result['rows']:,}")
        print(f"  element populated:           {result['element_populated']:,}")
        print(f"  element unique:              {result['element_unique']:,}")
        print(f"  element duplicate values:    {len(result['element_duplicate_values']):,}")
        print(f"  player_code column present:  {result['player_code_present']}")
        print(f"  player_code populated:       {result['player_code_populated']:,}")
        print(f"  player_code unique:          {result['player_code_unique']:,}")
        print(f"  player_code duplicate values:{len(result['player_code_duplicate_values']):,}")
        print(f"  relationship:                 {result['relationship']}")
        print(f"  code -> multiple elements:   {len(result['code_to_elements_multi']):,}")
        print(f"  element -> multiple codes:   {len(result['element_to_codes_multi']):,}")
        print()

    cross = report["cross_season"]
    print("CROSS-SEASON")
    print(f"  element values reused across seasons:     {len(cross['element_reused_across_seasons']):,}")
    print(f"  player_code values reused across seasons: {len(cross['player_code_reused_across_seasons']):,}")

    print()
    print("SAMPLE CROSS-SEASON REUSE")
    for value, seasons in list(cross["element_reused_across_seasons"].items())[:15]:
        print(f"  element={value} seasons={seasons}")
    for value, seasons in list(cross["player_code_reused_across_seasons"].items())[:15]:
        print(f"  player_code={value} seasons={seasons}")

    print()
    print("No files were written or modified.")
    print("=" * 96)


if __name__ == "__main__":
    print_report(run_audit())
