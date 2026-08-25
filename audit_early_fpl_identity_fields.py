"""Read-only discovery audit for early-season FPL identity-bearing fields.

Reports populated field counts and candidate overlaps with the PL merged-player
source. It does not promote or persist any identity mapping.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
import re
import unicodedata

import player_research
from player_identity_crosswalk import SEASONS

ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = ROOT.parent / "Premier-League-Stats" / "pl_stats"
MERGED_PLAYER_DIR = SOURCE_ROOT / "_merged" / "players"


def load_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def norm(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.casefold().replace("_", " ").replace("'", "")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def distinct_fpl(season: str) -> list[dict]:
    rows: dict[str, dict] = {}
    for row in player_research._load_season_rows(season):
        element = str(row.get("element") or row.get("player_code") or "").strip()
        if element:
            rows.setdefault(element, row)
    return list(rows.values())


def populated_counts(rows: list[dict]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in rows:
        for key, value in row.items():
            if str(value or "").strip():
                counts[key] += 1
    return counts


def candidate_name_fields(rows: list[dict]) -> list[str]:
    fields = []
    for field in sorted({k for row in rows for k in row}):
        sample = [str(row.get(field) or "").strip() for row in rows[:100]]
        nonempty = [v for v in sample if v]
        if not nonempty:
            continue
        nameish = sum(bool(re.search(r"[A-Za-z]", v)) and len(v) >= 3 for v in nonempty)
        if nameish / len(nonempty) >= 0.7:
            fields.append(field)
    return fields


def audit_season(season: str) -> dict:
    fpl = distinct_fpl(season)
    merged = load_csv(MERGED_PLAYER_DIR / f"{season}_players_stats.csv")
    merged_by_field: dict[str, set[str]] = defaultdict(set)
    for row in merged:
        for field, value in row.items():
            value = str(value or "").strip()
            if value:
                merged_by_field[field].add(norm(value) if field.lower() in {"playername", "player_name", "name", "displayname"} else value.casefold())

    counts = populated_counts(fpl)
    fields = candidate_name_fields(fpl)
    overlaps = []
    for field in fields:
        values = {norm(r.get(field)) for r in fpl if str(r.get(field) or "").strip()}
        merged_names = merged_by_field.get("playerName", set())
        matches = len(values & merged_names)
        if matches:
            overlaps.append((field, matches, len(values)))

    return {
        "season": season,
        "fpl": len(fpl),
        "fields": [(field, counts[field]) for field in sorted(counts, key=lambda x: (-counts[x], x))[:20]],
        "name_fields": fields[:30],
        "overlaps": sorted(overlaps, key=lambda x: (-x[1], x[0])),
    }


def main() -> None:
    print("=" * 96)
    print("FRL EARLY-SEASON FPL IDENTITY-FIELD DISCOVERY AUDIT")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 96)
    for season in SEASONS[:4]:
        result = audit_season(season)
        print(f"\n{season}: distinct FPL identities={result['fpl']}")
        print("TOP POPULATED FIELDS:")
        print("  " + ", ".join(f"{k}={v}" for k, v in result["fields"]))
        print("NAME-LIKE FIELDS:")
        print("  " + (", ".join(result["name_fields"]) or "none"))
        print("OVERLAP WITH merged.playerName (normalised):")
        print("  " + (", ".join(f"{f}:{m}/{n}" for f, m, n in result["overlaps"]) or "none"))
    print("\nNo files were written or modified.")
    print("=" * 96)


if __name__ == "__main__":
    main()
