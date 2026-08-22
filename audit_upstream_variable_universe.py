"""Audit the upstream variable universe against the published FRL-facing CSV shapes.

READ ONLY: this script does not write data. It inspects the public upstream
repository and, when requested, the official FPL API schemas exposed by the
upstream scraper design.
"""
from __future__ import annotations

import json
import urllib.request
from collections import defaultdict
from typing import Any

UPSTREAM_REPO = "https://raw.githubusercontent.com/imadeddine-belkat/Premier-League-Stats/main/"
FPL_API = "https://fantasy.premierleague.com/api/"


def fetch_json(url: str) -> Any:
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.load(response)


def classify_fpl_bootstrap(bootstrap: dict[str, Any]) -> dict[str, list[str]]:
    """Compare bootstrap element/team fields with fields retained by the CSV path."""
    elements = bootstrap.get("elements") or []
    teams = bootstrap.get("teams") or []

    element_fields = set().union(*(row.keys() for row in elements[:20])) if elements else set()
    team_fields = set().union(*(row.keys() for row in teams[:20])) if teams else set()

    # Fields explicitly injected by scrape_players.py / retained in player CSVs.
    retained_player = {
        "element", "position", "player_code", "first_name", "second_name",
        "fixture_code", "total_points", "minutes", "goals_scored", "assists",
        "clean_sheets", "goals_conceded", "own_goals", "penalties_saved",
        "penalties_missed", "yellow_cards", "red_cards", "saves", "bonus",
        "bps", "influence", "creativity", "threat", "ict_index",
        "clearances_blocks_interceptions", "recoveries", "tackles",
        "defensive_contribution", "starts", "expected_goals", "expected_assists",
        "expected_goal_involvements", "expected_goals_conceded", "value",
        "transfers_balance", "selected", "transfers_in", "transfers_out", "team_code",
    }

    retained_team = {"id", "name", "short_name", "code"}
    dropped_element = sorted(element_fields - retained_player)
    dropped_team = sorted(team_fields - retained_team)

    return {
        "bootstrap_element_fields": sorted(element_fields),
        "bootstrap_team_fields": sorted(team_fields),
        "element_fields_not_retained": dropped_element,
        "team_fields_not_retained": dropped_team,
    }


def fixture_source_gap() -> dict[str, list[str]]:
    # scrape_teams.py explicitly drops these upstream fixture fields before CSV output.
    return {"dropped_by_upstream_scraper": ["stats", "pulse_id"]}


def run() -> dict[str, Any]:
    bootstrap = fetch_json(FPL_API + "bootstrap-static/")
    return {
        "upstream_repository": "imadeddine-belkat/Premier-League-Stats",
        "fpl": classify_fpl_bootstrap(bootstrap),
        "fixtures": fixture_source_gap(),
        "published_architecture": {
            "historical_families": [
                "team_match", "player_match", "player_season", "squad"
            ],
            "additional_fpl_family": "player_gameweek",
            "note": "Published CSVs are not the full upstream variable universe.",
        },
    }


def print_report(report: dict[str, Any]) -> None:
    fpl = report["fpl"]
    print("=" * 104)
    print("FRL UPSTREAM VARIABLE UNIVERSE / LINEAGE AUDIT")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 104)
    print(f"Upstream repository: {report['upstream_repository']}")
    print()
    print(f"FPL bootstrap element fields observed: {len(fpl['bootstrap_element_fields'])}")
    print(f"FPL bootstrap team fields observed:    {len(fpl['bootstrap_team_fields'])}")
    print(f"Element fields not retained by scraper:  {len(fpl['element_fields_not_retained'])}")
    print(f"Team fields not retained by scraper:     {len(fpl['team_fields_not_retained'])}")
    print()
    print("FIXTURE FIELDS DROPPED BY UPSTREAM SCRAPER")
    for field in report["fixtures"]["dropped_by_upstream_scraper"]:
        print(f"  {field}")
    print()
    print("FPL ELEMENT FIELDS NOT RETAINED")
    for field in fpl["element_fields_not_retained"]:
        print(f"  {field}")
    print()
    print("FPL TEAM FIELDS NOT RETAINED")
    for field in fpl["team_fields_not_retained"]:
        print(f"  {field}")
    print()
    print("INTERPRETATION")
    print("- The FRL CSV universe is a published-data universe, not the complete upstream API universe.")
    print("- Fields dropped before CSV publication remain candidate variables for FRL review.")
    print("- Candidate availability does not imply semantic/canonical promotion.")
    print("- The full FRL variable taxonomy should ultimately include retained and upstream-only candidates.")
    print("=" * 104)


if __name__ == "__main__":
    print_report(run())
