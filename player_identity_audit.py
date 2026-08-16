"""Read-only audit for the FRL FPL ↔ player-match player identity bridge.

This module does not write files and does not create canonical identities.
It tests whether existing FPL player records can be deterministically matched
with external players_match_stats player identities using the repository's
verified seasonal team identity registry plus conservative normalized names.
"""

from __future__ import annotations

import csv
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

import player_research
import query_lab


PL_ROOT = Path(
    r"C:\Users\dlall\football_database\Premier-League-Stats\pl_stats"
)

SEASONS = tuple(player_research.available_seasons())


def normalize_name(value: str | None) -> str:
    """Return a conservative comparison form for footballer names and clubs."""
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
            handle = path.open("r", encoding=encoding, newline="")
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


def verified_team_codes(season: str) -> dict[str, str]:
    """Return verified persistent team IDs keyed by normalized canonical name."""
    return {
        normalize_name(row["canonical_name"]): str(row["persistent_team_code"])
        for row in query_lab.load_identity_registry()
        if (
            row["season"] == season
            and row["mapping_status"] == "VERIFIED"
        )
    }


def verified_team_names_by_code(season: str) -> dict[str, str]:
    """Return verified persistent team IDs keyed by persistent code."""
    return {
        str(row["persistent_team_code"]): str(row["canonical_name"])
        for row in query_lab.load_identity_registry()
        if (
            row["season"] == season
            and row["mapping_status"] == "VERIFIED"
        )
    }


def fpl_player_index(
    season: str,
) -> dict[tuple[str, str], set[tuple[str, str]]]:
    """Index FPL players by normalized name + verified persistent team code.

    Newer FPL source files expose a persistent ``team_code`` directly. Older
    seasons predate that column, so they fall back to the existing canonical
    club name and the verified seasonal team identity registry.
    """
    index: dict[tuple[str, str], set[tuple[str, str]]] = defaultdict(set)
    code_by_name = verified_team_codes(season)

    for row in player_research._load_season_rows(season):
        name = normalize_name(
            player_research.display_player_name(row)
        )
        team_code = str(row.get("team_code") or "").strip()

        if not team_code:
            team_code = code_by_name.get(
                normalize_name(player_research._row_club(row)),
                "",
            )

        player_code = player_research.seasonal_player_id(row)
        display = player_research.display_player_name(row)

        if name and team_code and player_code:
            index[(name, team_code)].add((player_code, display))

    return index


def source_player_index(
    season: str,
) -> dict[tuple[str, str], set[tuple[str, str]]]:
    """Index source players by normalized name + persistent source team ID."""
    index: dict[tuple[str, str], set[tuple[str, str]]] = defaultdict(set)

    for path in source_files(season):
        handle, reader = open_csv(path)
        for row in reader:
            name = normalize_name(source_player_name(row))
            team_id = str(row.get("team_id") or "").strip()
            pid = source_player_id(row)
            display = source_player_name(row)

            if name and team_id and pid:
                index[(name, team_id)].add((pid, display))
        handle.close()

    return index


def audit_season(season: str) -> dict:
    fpl = fpl_player_index(season)
    source = source_player_index(season)
    verified = verified_team_names_by_code(season)

    exact = []
    missing = []
    ambiguous = []

    for key, fpl_players in fpl.items():
        name, team_code = key
        source_players = source.get(key, set())

        if team_code not in verified:
            missing.append({
                "name": name,
                "team_code": team_code,
                "club": "UNVERIFIED TEAM CODE",
                "fpl_ids": sorted(pid for pid, _ in fpl_players),
            })
            continue

        fpl_ids = sorted(pid for pid, _ in fpl_players)
        source_ids = sorted(pid for pid, _ in source_players)
        source_names = sorted({display for _, display in source_players})

        if len(fpl_players) == 1 and len(source_players) == 1:
            fpl_id, fpl_display = next(iter(fpl_players))
            source_id, source_display = next(iter(source_players))
            exact.append({
                "fpl_name": fpl_display,
                "source_name": source_display,
                "fpl_player_code": fpl_id,
                "source_player_id": source_id,
                "team_code": team_code,
                "club": verified[team_code].replace("_", " "),
            })
        elif not source_players:
            missing.append({
                "name": name,
                "team_code": team_code,
                "club": verified[team_code].replace("_", " "),
                "fpl_ids": fpl_ids,
            })
        else:
            ambiguous.append({
                "name": name,
                "team_code": team_code,
                "club": verified[team_code].replace("_", " "),
                "fpl_ids": fpl_ids,
                "source_ids": source_ids,
                "source_names": source_names,
            })

    source_id_to_names: dict[str, set[str]] = defaultdict(set)
    for (name, _team_code), values in source.items():
        for pid, _display in values:
            source_id_to_names[pid].add(name)

    source_ids_with_multiple_names = {
        pid: sorted(names)
        for pid, names in source_id_to_names.items()
        if len(names) > 1
    }

    return {
        "season": season,
        "fpl_candidates": len(fpl),
        "source_candidates": len(source),
        "exact": exact,
        "missing": missing,
        "ambiguous": ambiguous,
        "source_ids_with_multiple_names": source_ids_with_multiple_names,
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
        print(f"    FPL player name+team candidates: {result['fpl_candidates']}")
        print(f"    Source player name+team candidates: {result['source_candidates']}")
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
