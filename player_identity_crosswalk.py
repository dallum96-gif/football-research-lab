"""Read-only builder/auditor for the FRL FPL element -> source playerId crosswalk.

The historical FPL files use season-local ``element`` values. The external
player-match source provides a longitudinal ``playerId``. This module builds
only evidence-backed candidate mappings and never writes canonical data.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import csv
import unicodedata
import re

import player_identity_audit
import query_lab
import player_research

SEASONS = tuple(player_identity_audit.SEASONS)
PL_ROOT = player_identity_audit.PL_ROOT


def normalize_name(value: str | None) -> str:
    if not value:
        return ""
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.casefold().replace("'", "")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def open_csv(path: Path):
    last = None
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            f = path.open("r", encoding=enc, newline="")
            return f, csv.DictReader(f)
        except UnicodeDecodeError as exc:
            last = exc
            try:
                f.close()
            except Exception:
                pass
    raise ValueError(f"Could not decode {path}") from last


def source_files(season: str) -> tuple[Path, ...]:
    return tuple(sorted(PL_ROOT.rglob(f"{season}_players_match_stats.csv")))


def verified_team_codes(season: str) -> dict[str, str]:
    return {
        normalize_name(row["canonical_name"]): str(row["persistent_team_code"])
        for row in query_lab.load_identity_registry()
        if row["season"] == season and row["mapping_status"] == "VERIFIED"
    }


def fpl_records(season: str):
    team_codes = verified_team_codes(season)
    for row in player_research._load_season_rows(season):
        element = str(row.get("element") or "").strip()
        if not element:
            continue
        name = player_research.display_player_name(row)
        club = player_research._row_club(row)
        team_code = str(row.get("team_code") or "").strip() or team_codes.get(normalize_name(club), "")
        yield {
            "season": season,
            "element": element,
            "name": name,
            "name_norm": normalize_name(name),
            "club": club,
            "team_code": team_code,
        }


def source_records(season: str):
    seen = set()
    for path in source_files(season):
        f, r = open_csv(path)
        for row in r:
            pid = str(row.get("playerId") or row.get("pl_code") or row.get("player_id") or "").strip()
            name = str(row.get("playerName") or row.get("player_name") or row.get("name") or "").strip()
            team = str(row.get("team_id") or "").strip()
            key = (pid, team, normalize_name(name))
            if pid and key not in seen:
                seen.add(key)
                yield {
                    "season": season,
                    "source_player_id": pid,
                    "name": name,
                    "name_norm": normalize_name(name),
                    "team_code": team,
                }
        f.close()


def exact_name_team_candidates(season: str):
    fpl = defaultdict(set)
    src = defaultdict(set)
    for rec in fpl_records(season):
        if rec["team_code"]:
            fpl[(rec["name_norm"], rec["team_code"])].add(rec["element"])
    for rec in source_records(season):
        src[(rec["name_norm"], rec["team_code"])].add(rec["source_player_id"])

    out = []
    for key, elements in fpl.items():
        ids = src.get(key, set())
        if len(elements) == 1 and len(ids) == 1:
            out.append({
                "season": season,
                "element": next(iter(elements)),
                "source_player_id": next(iter(ids)),
                "name_norm": key[0],
                "team_code": key[1],
                "method": "EXACT_NAME_TEAM",
                "status": "VERIFIED_CANDIDATE",
            })
    return out


def build_crosswalk_candidates():
    rows = []
    for season in SEASONS:
        rows.extend(exact_name_team_candidates(season))
    return rows


def summarize():
    candidates = build_crosswalk_candidates()
    by_fpl = defaultdict(set)
    by_source = defaultdict(set)
    for row in candidates:
        by_fpl[(row["season"], row["element"])].add(row["source_player_id"])
        by_source[row["source_player_id"]].add((row["season"], row["element"]))

    confirmed = []
    review = []
    for row in candidates:
        fpl_key = (row["season"], row["element"])
        ids = by_fpl[fpl_key]
        if len(ids) == 1:
            confirmed.append(row)
        else:
            review.append({**row, "status": "AMBIGUOUS_FPL_RECORD"})

    source_multi = {
        sid: sorted(keys)
        for sid, keys in by_source.items()
        if len({season for season, _ in keys}) > 1
    }

    return {
        "candidate_rows": len(candidates),
        "confirmed_rows": len(confirmed),
        "review_rows": len(review),
        "source_ids_spanning_seasons": len(source_multi),
        "confirmed": confirmed,
        "review": review,
        "source_multi": source_multi,
    }


def print_report(report):
    print("=" * 96)
    print("FRL FPL ELEMENT -> SOURCE PLAYER CROSSWALK AUDIT")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 96)
    print(f"Candidate exact name+team rows: {report['candidate_rows']:,}")
    print(f"Confirmed candidate rows:        {report['confirmed_rows']:,}")
    print(f"Review rows:                     {report['review_rows']:,}")
    print(f"Source IDs spanning seasons:     {report['source_ids_spanning_seasons']:,}")
    print("\nCONFIRMED SAMPLE:")
    for row in report["confirmed"][:25]:
        print(f"  {row['season']} | element={row['element']} | team={row['team_code']} | source={row['source_player_id']} | {row['method']}")
    print("\nNo files were written or modified.")
    print("=" * 96)


if __name__ == "__main__":
    print_report(summarize())
