"""Read-only audit of the FPL -> player-season source relationship.

This module does not promote identities or write canonical data. It measures
whether distinct season/FPL-element identities can be reconciled to the
player-season source using explicit evidence, while keeping the source-native
playerId namespace separate.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import re
import unicodedata

import player_research
import query_lab
from source_family_adapters import player_season_source_rows
from player_identity_crosswalk import SEASONS


@dataclass(frozen=True)
class FPLIdentity:
    season: str
    element: str
    name: str
    team_code: str


def normalize_name(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.casefold().replace("'", "")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def normalize_team(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.casefold().replace("'", "")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    aliases = {
        "man city": "manchester city",
        "mancity": "manchester city",
        "man utd": "manchester united",
        "man united": "manchester united",
        "manutd": "manchester united",
        "spurs": "tottenham hotspur",
        "tottenham": "tottenham hotspur",
        "a villa": "aston villa",
        "c palace": "crystal palace",
        "nottm forest": "nottingham forest",
        "west ham": "west ham united",
        "west brom": "west bromwich albion",
        "leeds": "leeds united",
        "newcastle": "newcastle united",
        "wolves": "wolverhampton wanderers",
        "brighton": "brighton and hove albion",
        "sheffield utd": "sheffield united",
        "leicester": "leicester city",
        "ipswich": "ipswich town",
        "norwich": "norwich city",
    }
    text = " ".join(text.split())
    return aliases.get(text, text)


def distinct_fpl_identities(seasons: tuple[str, ...] = SEASONS) -> tuple[FPLIdentity, ...]:
    rows: dict[tuple[str, str], FPLIdentity] = {}
    for season in seasons:
        for row in player_research._load_season_rows(season):
            element = str(row.get("element") or row.get("player_code") or "").strip()
            if not element:
                continue
            name = player_research.display_player_name(row)
            team_code = str(row.get("team_code") or "").strip()
            rows.setdefault(
                (season, element),
                FPLIdentity(season, element, name, team_code),
            )
    return tuple(rows.values())


def player_season_rows(seasons: tuple[str, ...] = SEASONS) -> tuple[dict, ...]:
    rows: list[dict] = []
    for season in seasons:
        rows.extend(player_season_source_rows(season))
    return tuple(rows)


def verified_team_names() -> dict[tuple[str, str], str]:
    return {
        (row["season"], str(row["persistent_team_code"]).strip()): row["canonical_name"]
        for row in query_lab.load_identity_registry()
        if row["mapping_status"] == "VERIFIED"
    }


def audit(seasons: tuple[str, ...] = SEASONS) -> dict:
    fpl = distinct_fpl_identities(seasons)
    source_rows = player_season_rows(seasons)

    by_name: dict[tuple[str, str], set[str]] = defaultdict(set)
    by_name_rows: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in source_rows:
        sid = str(row.get("playerId") or "").strip()
        name = normalize_name(row.get("playerName"))
        season = str(row.get("season") or "").strip()
        if not sid or not name or not season:
            continue
        by_name[(season, name)].add(sid)
        by_name_rows[(season, name)].append(row)

    team_names = verified_team_names()
    outcomes = []
    for identity in fpl:
        candidates = sorted(by_name.get((identity.season, normalize_name(identity.name)), set()))
        if not candidates:
            status = "NO_NAME_CANDIDATE"
        elif len(candidates) > 1:
            status = "AMBIGUOUS_NAME"
        else:
            status = "UNIQUE_NAME_CANDIDATE"

        source_team_values = set()
        for sid in candidates:
            for row in by_name_rows[(identity.season, normalize_name(identity.name))]:
                if str(row.get("playerId") or "").strip() != sid:
                    continue
                for value in (row.get("team_name"), row.get("team_id")):
                    if value not in (None, ""):
                        source_team_values.add(str(value).strip())

        fpl_team_name = team_names.get((identity.season, identity.team_code), "")
        team_matches = {
            value for value in source_team_values
            if fpl_team_name and normalize_team(value) == normalize_team(fpl_team_name)
        }

        outcomes.append({
            "season": identity.season,
            "element": identity.element,
            "fpl_name": identity.name,
            "fpl_team_code": identity.team_code,
            "fpl_team_name": fpl_team_name,
            "candidate_source_player_ids": candidates,
            "status": status,
            "source_team_values": sorted(source_team_values),
            "team_evidence_match": bool(team_matches),
        })

    return {
        "distinct_fpl_identities": len(fpl),
        "source_player_season_rows": len(source_rows),
        "no_name_candidate": sum(x["status"] == "NO_NAME_CANDIDATE" for x in outcomes),
        "unique_name_candidate": sum(x["status"] == "UNIQUE_NAME_CANDIDATE" for x in outcomes),
        "ambiguous_name": sum(x["status"] == "AMBIGUOUS_NAME" for x in outcomes),
        "unique_with_team_evidence": sum(
            x["status"] == "UNIQUE_NAME_CANDIDATE" and x["team_evidence_match"]
            for x in outcomes
        ),
        "unique_without_team_evidence": sum(
            x["status"] == "UNIQUE_NAME_CANDIDATE" and not x["team_evidence_match"]
            for x in outcomes
        ),
        "outcomes": outcomes,
    }


def print_report(report: dict) -> None:
    print("=" * 96)
    print("FRL FPL -> PLAYER-SEASON SOURCE BRIDGE AUDIT")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 96)
    print(f"Distinct FPL season/element identities: {report['distinct_fpl_identities']:,}")
    print(f"Player-season source rows:              {report['source_player_season_rows']:,}")
    print(f"No name candidate:                      {report['no_name_candidate']:,}")
    print(f"Unique name candidate:                  {report['unique_name_candidate']:,}")
    print(f"Ambiguous name candidate:               {report['ambiguous_name']:,}")
    print(f"Unique + team evidence:                 {report['unique_with_team_evidence']:,}")
    print(f"Unique without team evidence:          {report['unique_without_team_evidence']:,}")

    ambiguous = [x for x in report["outcomes"] if x["status"] == "AMBIGUOUS_NAME"]
    if ambiguous:
        print("\nAMBIGUOUS SAMPLE:")
        for row in ambiguous[:20]:
            print(
                f"  {row['season']} | element={row['element']} | "
                f"{row['fpl_name']} | candidates={row['candidate_source_player_ids']}"
            )

    no_team = [
        x for x in report["outcomes"]
        if x["status"] == "UNIQUE_NAME_CANDIDATE" and not x["team_evidence_match"]
    ]
    if no_team:
        print("\nUNIQUE NAME / NO VERIFIED TEAM-EVIDENCE SAMPLE:")
        for row in no_team[:20]:
            print(
                f"  {row['season']} | element={row['element']} | "
                f"{row['fpl_name']} | FPL team={row['fpl_team_name']} | "
                f"source teams={row['source_team_values']}"
            )

    print("\nNo files were written or modified.")
    print("=" * 96)


if __name__ == "__main__":
    print_report(audit())
