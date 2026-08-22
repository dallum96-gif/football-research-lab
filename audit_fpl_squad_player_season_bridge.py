"""Read-only audit of the FPL -> squad -> player-season source bridge.

The audit deliberately does not promote identities. It uses:
- season-scoped FPL element + player identity attributes;
- squad display name + source-file club partition as team evidence;
- the empirically verified direct (season, squad.playerId) ->
  (season, player_season.playerId) relationship.

The player-season ``team_name`` field is not used as team evidence because
source inspection shows it is not consistently the Premier League club
partition represented by the source file.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import re
import unicodedata

import player_research
import query_lab
from player_identity_crosswalk import SEASONS
from player_metadata_source import source_rows as squad_rows
from source_family_adapters import player_season_source_rows


@dataclass(frozen=True)
class FPLIdentity:
    season: str
    element: str
    name: str
    team_name: str


def normalize_name(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.casefold().replace("'", "")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def normalize_team(value: object) -> str:
    text = normalize_name(value)
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
    return aliases.get(text, text)


def fpl_team_name(row: dict, season: str) -> str:
    club = player_research._row_club({**row, "_season": season})
    if club:
        return str(club).strip()
    team_code = str(row.get("team_code") or "").strip()
    if not team_code:
        return ""
    for registry in query_lab.load_identity_registry():
        if (
            registry["season"] == season
            and registry["mapping_status"] == "VERIFIED"
            and str(registry["persistent_team_code"]).strip() == team_code
        ):
            return registry["canonical_name"].replace("_", " ")
    return team_code


def distinct_fpl_identities(seasons: tuple[str, ...] = SEASONS) -> tuple[FPLIdentity, ...]:
    rows: dict[tuple[str, str], FPLIdentity] = {}
    for season in seasons:
        for row in player_research._load_season_rows(season):
            element = str(row.get("element") or row.get("player_code") or "").strip()
            if not element:
                continue
            rows.setdefault(
                (season, element),
                FPLIdentity(
                    season=season,
                    element=element,
                    name=player_research.display_player_name(row),
                    team_name=fpl_team_name(row, season),
                ),
            )
    return tuple(rows.values())


def squad_club_from_source_file(value: object) -> str:
    path = Path(str(value or ""))
    parts = list(path.parts)
    try:
        index = parts.index("squad")
    except ValueError:
        return ""
    if index == 0:
        return ""
    folder = parts[index - 1]
    match = re.match(r"^(.*)_([0-9]+)$", folder)
    return match.group(1) if match else folder


def squad_records(seasons: tuple[str, ...] = SEASONS) -> tuple[dict, ...]:
    rows = []
    for season in seasons:
        for row in squad_rows(season):
            item = dict(row)
            item["_season"] = season
            item["_source_club"] = squad_club_from_source_file(row.get("_source_file"))
            rows.append(item)
    return tuple(rows)


def player_season_ids(seasons: tuple[str, ...] = SEASONS) -> set[tuple[str, str]]:
    return {
        (str(row.get("season") or "").strip(), str(row.get("playerId") or "").strip())
        for season in seasons
        for row in player_season_source_rows(season)
        if str(row.get("season") or "").strip() and str(row.get("playerId") or "").strip()
    }


def audit(seasons: tuple[str, ...] = SEASONS) -> dict:
    fpl = distinct_fpl_identities(seasons)
    squad = squad_records(seasons)
    ps_ids = player_season_ids(seasons)

    by_name_team: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    for row in squad:
        sid = str(row.get("playerId") or "").strip()
        if not sid:
            continue
        key = (
            str(row.get("_season") or "").strip(),
            normalize_name(row.get("displayName")),
            normalize_team(row.get("_source_club")),
        )
        if all(key):
            by_name_team[key].add(sid)

    results = []
    for identity in fpl:
        key = (
            identity.season,
            normalize_name(identity.name),
            normalize_team(identity.team_name),
        )
        candidates = sorted(by_name_team.get(key, set())) if key[2] else []
        if not identity.team_name:
            status = "NO_FPL_TEAM_CONTEXT"
        elif not candidates:
            status = "NO_UNIQUE_SQUAD_CANDIDATE"
        elif len(candidates) > 1:
            status = "AMBIGUOUS_SQUAD_CANDIDATE"
        else:
            sid = candidates[0]
            status = "SQUAD_CANDIDATE_WITH_PLAYER_SEASON" if (identity.season, sid) in ps_ids else "SQUAD_CANDIDATE_NO_PLAYER_SEASON"
        results.append({"identity": identity, "candidates": candidates, "status": status})

    return {
        "fpl_identities": len(fpl),
        "squad_rows": len(squad),
        "player_season_ids": len(ps_ids),
        "no_fpl_team_context": sum(r["status"] == "NO_FPL_TEAM_CONTEXT" for r in results),
        "no_unique_squad_candidate": sum(r["status"] == "NO_UNIQUE_SQUAD_CANDIDATE" for r in results),
        "ambiguous_squad_candidate": sum(r["status"] == "AMBIGUOUS_SQUAD_CANDIDATE" for r in results),
        "squad_candidate_with_player_season": sum(r["status"] == "SQUAD_CANDIDATE_WITH_PLAYER_SEASON" for r in results),
        "squad_candidate_no_player_season": sum(r["status"] == "SQUAD_CANDIDATE_NO_PLAYER_SEASON" for r in results),
        "results": results,
    }


def print_report(report: dict) -> None:
    print("=" * 96)
    print("FRL FPL -> SQUAD -> PLAYER-SEASON BRIDGE AUDIT")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 96)
    print(f"Distinct FPL season/element identities: {report['fpl_identities']:,}")
    print(f"Squad source rows:                       {report['squad_rows']:,}")
    print(f"Player-season identity keys:             {report['player_season_ids']:,}")
    print(f"No FPL team context:                     {report['no_fpl_team_context']:,}")
    print(f"No unique squad candidate:               {report['no_unique_squad_candidate']:,}")
    print(f"Ambiguous squad candidate:               {report['ambiguous_squad_candidate']:,}")
    print(f"Squad candidate + player-season:         {report['squad_candidate_with_player_season']:,}")
    print(f"Squad candidate without player-season:   {report['squad_candidate_no_player_season']:,}")
    print("\nNO UNIQUE CANDIDATE SAMPLE:")
    shown = 0
    for result in report["results"]:
        if result["status"] == "NO_UNIQUE_SQUAD_CANDIDATE":
            identity = result["identity"]
            print(f"  {identity.season} | element={identity.element} | {identity.name} | team={identity.team_name!r}")
            shown += 1
            if shown >= 20:
                break
    print("\nNo files were written or modified.")
    print("=" * 96)


if __name__ == "__main__":
    print_report(audit())
