"""Read-only audit: FPL season element -> historical PL playerId.

Evidence chain, per season:
  FPL seasonal identity: element + display name
      -> historical PL seasonal index: playerId + display name
      -> Player-Match occurrence: same playerId is present in that season

This deliberately does not use cross-season continuity, numeric-code equality,
or fuzzy matching. Duplicate historical names remain REVIEW.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import json
import re
import unicodedata

import player_identity_audit
import player_research

PL_ROOT = player_identity_audit.PL_ROOT
INDEX_DIR = PL_ROOT / "_index"


def norm(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.casefold().replace("'", "")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def historical_name_index(season: str) -> dict[str, set[str]]:
    path = INDEX_DIR / f"{season}_players.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, set[str]] = defaultdict(set)
    for source_id, name in data.items():
        n = norm(name)
        if n:
            out[n].add(str(source_id).strip())
    return out


def source_ids_present_in_player_match(season: str) -> set[str]:
    out: set[str] = set()
    for path in player_identity_audit.source_files(season):
        with path.open("r", encoding="utf-8-sig", newline="") as fh:
            import csv
            for row in csv.DictReader(fh):
                sid = player_identity_audit.source_player_id(row)
                if sid:
                    out.add(sid)
    return out


def distinct_fpl(season: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for row in player_research._load_season_rows(season):
        element = str(row.get("element") or row.get("player_code") or "").strip()
        if not element:
            continue
        name = player_research.display_player_name(row).strip()
        if name:
            out.setdefault(element, name)
    return out


def audit() -> dict:
    rows: list[dict[str, str]] = []
    seasons = tuple(player_identity_audit.SEASONS)
    for season in seasons:
        names = historical_name_index(season)
        present = source_ids_present_in_player_match(season)
        for element, fpl_name in distinct_fpl(season).items():
            candidates = sorted(names.get(norm(fpl_name), set()), key=lambda v: int(v))
            present_candidates = [sid for sid in candidates if sid in present]

            if len(present_candidates) == 1:
                status = "VERIFIED_CANDIDATE"
                source_id = present_candidates[0]
                confidence = "HIGH"
                basis = "exact season-local normalized name match to historical PL player index + source playerId present in Player-Match for same season"
            elif len(candidates) == 1 and len(present_candidates) == 0:
                status = "REVIEW"
                source_id = candidates[0]
                confidence = "REVIEW"
                basis = "exact seasonal index name match, but source playerId not observed in Player-Match"
            elif len(candidates) > 1:
                status = "REVIEW"
                source_id = ""
                confidence = "REVIEW"
                basis = "multiple historical PL playerIds share the normalized seasonal name"
            else:
                status = "UNRESOLVED"
                source_id = ""
                confidence = "UNRESOLVED"
                basis = "no exact seasonal index name match"

            rows.append({
                "season": season,
                "fpl_element": element,
                "fpl_name": fpl_name,
                "source_player_id": source_id,
                "status": status,
                "confidence": confidence,
                "evidence_basis": basis,
                "historical_index": str(INDEX_DIR / f"{season}_players.json"),
            })

    return {
        "rows": rows,
        "counts": {
            "fpl_identities": len(rows),
            "verified_candidates": sum(r["status"] == "VERIFIED_CANDIDATE" for r in rows),
            "review": sum(r["status"] == "REVIEW" for r in rows),
            "unresolved": sum(r["status"] == "UNRESOLVED" for r in rows),
        },
    }


def print_report(result: dict) -> None:
    c = result["counts"]
    print("=" * 104)
    print("FRL FPL SEASON ELEMENT -> HISTORICAL PL PLAYER INDEX AUDIT")
    print("READ ONLY - NO CANONICAL PROMOTION")
    print("=" * 104)
    print(f"Distinct FPL season/element identities: {c['fpl_identities']:,}")
    print(f"VERIFIED candidates:                  {c['verified_candidates']:,}")
    print(f"REVIEW:                                {c['review']:,}")
    print(f"UNRESOLVED:                            {c['unresolved']:,}")
    print("\nVERIFIED SAMPLE")
    for row in [r for r in result["rows"] if r["status"] == "VERIFIED_CANDIDATE"][:40]:
        print(f"  {row['season']} | element={row['fpl_element']} | source={row['source_player_id']} | {row['fpl_name']}")
    print("\nNo files were written or modified.")
    print("=" * 104)


if __name__ == "__main__":
    print_report(audit())
