"""Read-only audit for the FRL FPL ↔ player-match player identity bridge.

This module does not write files and does not create canonical identities.
It tests whether the existing FPL player records can be deterministically
matched to the external players_match_stats player records by season, club,
and normalized name, while surfacing ambiguity rather than guessing.
"""

from __future__ import annotations

import csv
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

import player_research


PL_ROOT = Path(
    r"C:\Users\dlall\football_database\Premier-League-Stats\pl_stats"
)

SEASONS = tuple(player_research.available_seasons())


def normalize_name(value: str | None) -> str:
    """Return a conservative comparison form for footballer names."""
    if not value:
        return ""

    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(
        char for char in text
        if not unicodedata.combining(char)
    )
    text = text.casefold()
    text = text.replace("'", "")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def source_player_name(row: dict) -> str:
    return str(
        row.get("playerName")
        or row.get("player_name")
        or row.get("name")
        or ""
    ).strip()


def source_player_id(row: dict) -> str:
    return str(
        row.get("playerId")
        or row.get("pl_code")
        or row.get("player_id")
        or ""
    ).strip()


def open_csv(path: Path):
    last_error = None
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            handle = path.open(
                "r",
                encoding=encoding,
                newline="",
            )
            reader = csv.DictReader(handle)
            _ = reader.fieldnames
            return handle, reader
        except UnicodeDecodeError as exc:
            last_error = exc
            try:
                handle.close()
            except Exception:
                pass
    raise ValueError(f"Could not decode CSV: {path}") from last_error


def source_files(season: str) -> tuple[Path, ...]:
    expected = f"{season}_players_match_stats.csv"
    return tuple(sorted(PL_ROOT.rglob(expected)))


def fpl_player_index(season: str) -> dict[tuple[str, str], list[dict]]:
    """Index existing FRL/FPL players by normalized name and club."""
    index: dict[tuple[str, str], list[dict]] = defaultdict(list)

    for row in player_research._load_season_rows(season):
        name = normalize_name(
            player_research.display_player_name(row)
        )
        club = normalize_name(
            player_research._row_club(row)
        )
        if name and club:
            index[(name, club)].append(row)

    return index


def source_player_index(season: str) -> dict[tuple[str, str], set[tuple[str, str]]]:
    """Index source players by normalized name and club.

    Values are (source_player_id, source_name) pairs so ID continuity and
    name variants can both be inspected.
    """
    index: dict[tuple[str, str], set[tuple[str, str]]] = defaultdict(set)

    for path in source_files(season):
        handle, reader = open_csv(path)
        for row in reader:
            name = normalize_name(source_player_name(row))
            club = normalize_name(str(row.get("team") or ""))
            pid = source_player_id(row)
            display = source_player_name(row)
            if name and club and pid:
                index[(name, club)].add((pid, display))
        handle.close()

    return index


def audit_season(season: str) -> dict:
    fpl = fpl_player_index(season)
    source = source_player_index(season)

    exact = []
    missing = []
    ambiguous = []
    duplicate_source_ids = defaultdict(set)

    for key, fpl_rows in fpl.items():
        source_rows = source.get(key, set())

        fpl_ids = {
            player_research.seasonal_player_id(row)
            for row in fpl_rows
            if player_research.seasonal_player_id(row)
        }

        source_ids = {
            pid
            for pid, _ in source_rows
            if pid
        }

        if len(source_rows) == 1 and len(fpl_rows) == 1:
            pid, display = next(iter(source_rows))
            exact.append({
                "fpl_name": player_research.display_player_name(fpl_rows[0]),
                "source_name": display,
                "fpl_player_code": next(iter(fpl_ids), ""),
                "source_player_id": pid,
                "club": key[1],
            })
        elif not source_rows:
            missing.append({
                "name": key[0],
                "club": key[1],
                "fpl_rows": len(fpl_rows),
                "fpl_ids": sorted(fpl_ids),
            })
        else:
            ambiguous.append({
                "name": key[0],
                "club": key[1],
                "fpl_rows": len(fpl_rows),
                "source_rows": len(source_rows),
                "fpl_ids": sorted(fpl_ids),
                "source_ids": sorted(source_ids),
                "source_names": sorted({name for _, name in source_rows}),
            })

    source_id_to_names: dict[str, set[str]] = defaultdict(set)
    for (name, club), values in source.items():
        for pid, display in values:
            source_id_to_names[pid].add(name)
    for pid, names in source_id_to_names.items():
        if len(names) > 1:
            duplicate_source_ids[pid].update(names)

    return {
        "season": season,
        "fpl_candidates": len(fpl),
        "source_candidates": len(source),
        "exact": exact,
        "missing": missing,
        "ambiguous": ambiguous,
        "source_ids_with_multiple_names": duplicate_source_ids,
    }


def run_audit() -> dict:
    """Return the full read-only audit report."""
    seasons = {
        season: audit_season(season)
        for season in SEASONS
    }

    totals = {
        "exact": sum(len(report["exact"]) for report in seasons.values()),
        "missing": sum(len(report["missing"]) for report in seasons.values()),
        "ambiguous": sum(len(report["ambiguous"]) for report in seasons.values()),
    }

    return {
        "seasons": seasons,
        "totals": totals,
    }


def print_report(report: dict) -> None:
    print("=" * 96)
    print("FRL / FPL ↔ PLAYER-MATCH PLAYER IDENTITY AUDIT")
    print("READ ONLY — NO FILES WILL BE WRITTEN")
    print("=" * 96)
    print()

    for season, result in report["seasons"].items():
        print(f"  {season}")
        print(f"    FPL player name+club candidates: {result['fpl_candidates']}")
        print(f"    Source player name+club candidates: {result['source_candidates']}")
        print(f"    exact 1:1 matches: {len(result['exact'])}")
        print(f"    missing source match: {len(result['missing'])}")
        print(f"    ambiguous match: {len(result['ambiguous'])}")

        if result["missing"]:
            print("    MISSING SAMPLE:")
            for item in result["missing"][:10]:
                print(
                    f"      name={item['name']} club={item['club']} "
                    f"fpl_ids={item['fpl_ids']}"
                )

        if result["ambiguous"]:
            print("    AMBIGUOUS SAMPLE:")
            for item in result["ambiguous"][:10]:
                print(
                    f"      name={item['name']} club={item['club']} "
                    f"fpl_ids={item['fpl_ids']} "
                    f"source_ids={item['source_ids']} "
                    f"source_names={item['source_names']}"
                )
        print()

    totals = report["totals"]
    print("=" * 96)
    print("TOTAL")
    print("=" * 96)
    print(f"Exact 1:1 matches:  {totals['exact']:,}")
    print(f"Missing:            {totals['missing']:,}")
    print(f"Ambiguous:          {totals['ambiguous']:,}")
    print()
    print("No files were written or modified.")
    print("=" * 96)


if __name__ == "__main__":
    print_report(run_audit())
