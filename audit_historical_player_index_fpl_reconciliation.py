"""Read-only evidence audit for historical PL playerId -> FPL element reconciliation.

Evidence chain, per season:
    PL seasonal player index: playerId -> canonical source name
    Player-Match observations: playerId -> season-local team occurrence
    FRL team registry: season-local team -> verified persistent team code
    FPL player rows: normalized player name + persistent team -> element

Only unique bidirectional mappings are VERIFIED. No canonical FRL player ID is
invented or written by this audit.
"""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

import player_identity_audit
import player_research
import query_lab

PL_ROOT = player_identity_audit.PL_ROOT
HISTORICAL_INDEX_DIR = PL_ROOT / "_index"


def normalize_name(value: str | None) -> str:
    if not value:
        return ""
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.casefold().replace("'", "")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def load_historical_index(season: str) -> dict[str, str]:
    path = HISTORICAL_INDEX_DIR / f"{season}_players.json"
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return {str(k).strip(): str(v).strip() for k, v in data.items() if str(k).strip() and str(v).strip()}


def verified_local_to_persistent_team(season: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for row in query_lab.load_identity_registry():
        if row["season"] != season or row["mapping_status"] != "VERIFIED":
            continue
        local_id = str(row.get("local_team_id") or "").strip()
        persistent = str(row.get("persistent_team_code") or "").strip()
        if local_id and persistent:
            mapping[local_id] = persistent
    return mapping


def source_occurrences(season: str) -> dict[str, set[str]]:
    """Return source playerId -> verified persistent team codes for this season."""
    team_map = verified_local_to_persistent_team(season)
    out: dict[str, set[str]] = defaultdict(set)
    for path in player_identity_audit.source_files(season):
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                pid = player_identity_audit.source_player_id(row)
                local_team = str(row.get("team_id") or "").strip()
                persistent = team_map.get(local_team, "")
                if pid and persistent:
                    out[pid].add(persistent)
    return out


def fpl_by_name_team(season: str) -> dict[tuple[str, str], set[str]]:
    out: dict[tuple[str, str], set[str]] = defaultdict(set)
    team_by_name = player_identity_audit.verified_team_codes(season)
    for row in player_research._load_season_rows(season):
        element = str(player_research.seasonal_player_id(row)).strip()
        name = normalize_name(player_research.display_player_name(row))
        club = player_research._row_club(row)
        team_code = str(row.get("team_code") or "").strip() or team_by_name.get(normalize_name(club), "")
        if element and name and team_code:
            out[(name, team_code)].add(element)
    return out


def candidate_rows(season: str) -> list[dict[str, str]]:
    historical = load_historical_index(season)
    occurrences = source_occurrences(season)
    fpl = fpl_by_name_team(season)

    source_to_elements: dict[str, set[str]] = defaultdict(set)
    element_to_sources: dict[str, set[str]] = defaultdict(set)
    rows: list[dict[str, str]] = []

    for source_id, team_codes in occurrences.items():
        source_name = historical.get(source_id, "")
        if not source_name:
            continue
        name_norm = normalize_name(source_name)
        if not name_norm:
            continue
        candidate_elements: set[str] = set()
        for team_code in team_codes:
            candidate_elements.update(fpl.get((name_norm, team_code), set()))

        for element in candidate_elements:
            source_to_elements[source_id].add(element)
            element_to_sources[element].add(source_id)

        rows.append({
            "season": season,
            "source_player_id": source_id,
            "source_name": source_name,
            "source_name_normalized": name_norm,
            "source_team_codes": ";".join(sorted(team_codes)),
            "candidate_fpl_elements": ";".join(sorted(candidate_elements, key=int)),
            "evidence_historical_index": str(HISTORICAL_INDEX_DIR / f"{season}_players.json"),
            "evidence_player_match": ";".join(str(p) for p in player_identity_audit.source_files(season)),
            "method": "HISTORICAL_INDEX_NAME_PLUS_VERIFIED_TEAM",
        })

    for row in rows:
        sid = row["source_player_id"]
        elements = source_to_elements.get(sid, set())
        if len(elements) == 1:
            element = next(iter(elements))
            inverse = element_to_sources.get(element, set())
            if len(inverse) == 1:
                row["status"] = "VERIFIED_CANDIDATE"
                row["fpl_element"] = element
                row["confidence"] = "VERIFIED"
                row["evidence_basis"] = (
                    "historical PL player index supplies source identity; Player-Match supplies "
                    "season/team occurrence; verified team registry supplies persistent team; "
                    "FPL seasonal data yields exactly one element and the element maps back to "
                    "exactly one source playerId"
                )
            else:
                row["status"] = "REVIEW"
                row["fpl_element"] = ""
                row["confidence"] = "REVIEW"
                row["evidence_basis"] = "FPL element is not bidirectionally unique for this source player"
        elif len(elements) > 1:
            row["status"] = "REVIEW"
            row["fpl_element"] = ""
            row["confidence"] = "REVIEW"
            row["evidence_basis"] = "source player maps to multiple FPL elements"
        else:
            row["status"] = "UNRESOLVED"
            row["fpl_element"] = ""
            row["confidence"] = "UNRESOLVED"
            row["evidence_basis"] = "no FPL element found for historical index name plus verified team"

    return rows


def run() -> dict:
    seasons = tuple(
        season for season in player_identity_audit.SEASONS
        if (HISTORICAL_INDEX_DIR / f"{season}_players.json").exists()
    )
    all_rows: list[dict[str, str]] = []
    for season in seasons:
        all_rows.extend(candidate_rows(season))

    verified = [r for r in all_rows if r["status"] == "VERIFIED_CANDIDATE"]
    review = [r for r in all_rows if r["status"] == "REVIEW"]
    unresolved = [r for r in all_rows if r["status"] == "UNRESOLVED"]

    # Compare against the current verified registry so we can measure genuinely new edges.
    existing: set[tuple[str, str, str]] = set()
    registry = Path("player_identity_registry.csv")
    if registry.exists():
        with registry.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                existing.add((str(row.get("season") or ""), str(row.get("fpl_element") or ""), str(row.get("source_player_id") or "")))

    new_verified = [
        r for r in verified
        if (r["season"], r["fpl_element"], r["source_player_id"]) not in existing
    ]

    return {
        "seasons": seasons,
        "rows": all_rows,
        "counts": {
            "source_player_season_rows": len(all_rows),
            "verified_candidates": len(verified),
            "new_verified_edges": len(new_verified),
            "review": len(review),
            "unresolved": len(unresolved),
        },
        "new_verified": new_verified,
    }


def print_report(result: dict) -> None:
    c = result["counts"]
    print("=" * 108)
    print("FRL HISTORICAL PL PLAYER INDEX -> FPL ELEMENT RECONCILIATION")
    print("READ ONLY - EVIDENCE AUDIT - NO CANONICAL PROMOTION")
    print("=" * 108)
    print(f"Seasons audited:                 {len(result['seasons']):,}")
    print(f"Source player-season rows:       {c['source_player_season_rows']:,}")
    print(f"Verified candidate edges:        {c['verified_candidates']:,}")
    print(f"New verified edges vs registry:  {c['new_verified_edges']:,}")
    print(f"Review edges:                    {c['review']:,}")
    print(f"Unresolved edges:                {c['unresolved']:,}")
    print()
    print("NEW VERIFIED SAMPLE")
    for row in result["new_verified"][:50]:
        print(
            f"  {row['season']} | source={row['source_player_id']} | "
            f"element={row['fpl_element']} | {row['source_name']} | "
            f"teams={row['source_team_codes']}"
        )
    print()
    print("No files were written or modified.")
    print("=" * 108)


if __name__ == "__main__":
    print_report(run())
