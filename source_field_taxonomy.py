"""Presentation-oriented taxonomy for the broad FRL source-field universe.

This module organises source fields for future FM-style filtering, FBref-style
sections and FotMob-style profiles. It does NOT assert semantic correctness or
promote any field. Taxonomy is a navigation aid; registry status remains the
source of truth for exposure decisions.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from source_field_catalog import build_catalog


CATEGORIES = (
    "Identity & Context",
    "Playing Time",
    "Shooting & Finishing",
    "Chance Creation",
    "Passing & Distribution",
    "Crossing & Set Pieces",
    "Dribbling & Carrying",
    "Possession & Ball Security",
    "Duels & Aerials",
    "Defending",
    "Goalkeeping",
    "Discipline",
    "Team Attack",
    "Team Defence",
    "Tactical & Match Context",
    "Physical & Tracking",
    "Unclassified Review",
)


@dataclass(frozen=True)
class TaxonomyRow:
    family: str
    source_field: str
    primary_category: str
    secondary_category: str | None
    registry_status: str
    coverage_class: str


def _tokens(name: str) -> set[str]:
    spaced = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
    spaced = spaced.replace("_", " ").replace("-", " ").lower()
    return {token for token in spaced.split() if token}


def classify_field(family: str, field: str) -> tuple[str, str | None]:
    tokens = _tokens(field)

    # Explicit field-level exceptions for names that contain generic tokens
    # whose domain is nevertheless clear from the source metric name.
    explicit = {
        "substitute.1": ("Playing Time", None),
        "penaltyConceded": ("Discipline", None),
        "penaltyFaced": ("Discipline", None),
        "penaltiesConceded": ("Discipline", None),
        "penaltyMiss": ("Shooting & Finishing", None),
        "penaltyWon": ("Chance Creation", None),
        "redCardsAgainst": ("Team Defence", None),
        "redCardsFor": ("Team Defence", None),
        "ptsDroppedWinningPos": ("Team Attack", None),
        "ptsGainedLosingPos": ("Team Attack", None),
        "subsMade": ("Playing Time", None),
        "subsGoals": ("Team Attack", None),
    }
    if field in explicit:
        return explicit[field]

    if tokens & {"season", "nationality", "country", "slug", "id", "code", "name"}:
        return "Identity & Context", None

    if tokens & {"appearance", "appearances", "starts", "minutes", "minute", "timeplayed", "substitute", "gamesplayed", "subs"}:
        return "Playing Time", None

    if tokens & {"sprint", "sprinting", "jogging", "running", "walking", "distance", "meters", "metres", "physical"}:
        return "Physical & Tracking", None

    if tokens & {
        "save", "saves", "saved", "smother", "punch", "punches", "keeper",
        "goalkeeper", "distribution", "claim", "catches", "catch", "diving",
        "goalsprevented", "savedshotsfrominsidethebox", "penaltysave", "savesfrompenalty",
        "putthroughblockeddistribution", "putthroughblockeddistributionwon",
    }:
        return "Goalkeeping", None

    if tokens & {
        "yellow", "red", "card", "foul", "fouls", "fouled", "handball", "handballs",
        "penaltyconceded", "penaltiesconceded", "penaltyfaced", "penaltiesfaced",
        "secondyellow", "straightredcards",
    }:
        return "Discipline", None

    if tokens & {"duel", "duels", "aerial", "contest", "challenge"}:
        return "Duels & Aerials", None

    if tokens & {
        "tackle", "interception", "clearance", "block", "blocked", "error", "lastman",
        "defender", "defensive", "posslost", "possessionlost",
    }:
        return "Defending", None

    if tokens & {"dribble", "dribbles", "dribbling", "carry", "carries", "progressive", "progression", "putthrough", "layoff", "flickon", "pullback"}:
        return "Dribbling & Carrying", None

    if tokens & {"touch", "touches", "dispossessed", "recovery", "recoveries", "recover", "poss", "possession"}:
        return "Possession & Ball Security", None

    if tokens & {"cross", "corner", "freekick", "setpiece", "setplay", "deadball", "throwin", "launch", "longball"}:
        return "Crossing & Set Pieces", None

    if tokens & {"assist", "chance", "keypass", "attassist", "bigchance", "throughball", "openthrough"}:
        return "Chance Creation", None

    if tokens & {"pass", "passes", "passing", "backward", "forward", "accurate", "chipped", "fwdpass", "zonepass", "shortpass", "longpass", "oppositionhalf", "ownhalf"}:
        return "Passing & Distribution", None

    if tokens & {"goal", "goals", "shot", "shots", "scoring", "scored", "xg", "expectedgoals", "target", "woodwork", "penaltygoal", "owngoal"}:
        return "Shooting & Finishing", None

    if family == "team_match":
        if tokens & {"posswon", "entries", "entry", "points", "result", "att", "attempt", "attempts"}:
            return "Team Attack", None
        if tokens & {"against", "conceded", "lost", "woncorners", "redcardsagainst", "keepergoals"}:
            return "Team Defence", None
        return "Tactical & Match Context", None

    return "Unclassified Review", None


def build_taxonomy() -> tuple[TaxonomyRow, ...]:
    rows = []
    for item in build_catalog():
        if item["registry_status"] != "UNCATALOGUED":
            continue
        primary, secondary = classify_field(item["family"], item["source_field"])
        rows.append(
            TaxonomyRow(
                family=item["family"],
                source_field=item["source_field"],
                primary_category=primary,
                secondary_category=secondary,
                registry_status=item["registry_status"],
                coverage_class=item["coverage_class"],
            )
        )
    return tuple(rows)


def taxonomy_summary() -> dict[str, int]:
    rows = build_taxonomy()
    return {category: sum(row.primary_category == category for row in rows) for category in CATEGORIES}


if __name__ == "__main__":
    rows = build_taxonomy()
    summary = taxonomy_summary()
    print("=" * 104)
    print("FRL SOURCE-FIELD NAVIGATION TAXONOMY")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 104)
    print(f"Uncatalogued fields classified: {len(rows)}")
    for category in CATEGORIES:
        print(f"  {category:30} {summary[category]}")
    print()
    print("SAMPLE")
    for row in rows[:40]:
        print(f"{row.family:14} | {row.source_field:45} | {row.primary_category}")
    print("=" * 104)
