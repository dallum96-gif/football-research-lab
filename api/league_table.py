from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

import query_api


router = APIRouter()
ROOT = Path(__file__).resolve().parents[1]
SEASON_RELEASE_ROOT = ROOT / "data" / "season_releases"
LeagueTableView = Literal["overall", "home", "away", "last5"]


class LeagueTableRow(BaseModel):
    position: int
    persistent_team_code: str
    display_name: str
    local_team_id: str
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int
    form: list[Literal["W", "D", "L"]] = Field(default_factory=list)


class LeagueTableResult(BaseModel):
    season: str
    competition: str
    view: LeagueTableView = "overall"
    rows: list[LeagueTableRow]
    completed_fixtures: int
    scheduled_fixtures: int
    total_fixtures: int
    latest_completed_kickoff: str | None = None
    information_available_as_of: str | None = None
    source_release_sha: str | None = None
    query_version: str
    limitations: list[str] = Field(default_factory=list)


def _release_metadata(
    season: str,
    completed_fixtures: int,
    total_fixtures: int,
) -> tuple[str | None, str | None]:
    register = SEASON_RELEASE_ROOT / season / "capability_gap_register.json"
    if not register.is_file():
        return None, None

    payload = json.loads(register.read_text(encoding="utf-8"))
    results_capability = next(
        (
            item
            for item in payload.get("capabilities", [])
            if item.get("capability") == "results_scores"
        ),
        None,
    )
    expected_coverage = f"{completed_fixtures}/{total_fixtures} completed"

    # A living-season fixture master can move beyond a previously pinned
    # release. Never attach an older release boundary to newer standings.
    if (
        results_capability is None
        or str(results_capability.get("coverage") or "").strip()
        != expected_coverage
    ):
        return None, None

    return (
        str(payload.get("information_available_as_of") or "") or None,
        str(payload.get("source_release_sha") or "") or None,
    )


def _completed_fixture_context(
    season: str,
) -> tuple[list[dict], int, int, str | None]:
    payload = query_api.fixtures(season=season, limit=1000)
    fixtures = list(payload.get("results") or [])
    completed_fixtures: list[dict] = []
    latest_completed_kickoff: str | None = None

    for fixture in fixtures:
        home_score = fixture.get("home_score")
        away_score = fixture.get("away_score")
        if home_score in (None, "") or away_score in (None, ""):
            continue

        completed_fixtures.append(fixture)
        kickoff = str(fixture.get("kickoff_time") or "").strip()
        if kickoff and (latest_completed_kickoff is None or kickoff > latest_completed_kickoff):
            latest_completed_kickoff = kickoff

    return (
        completed_fixtures,
        len(completed_fixtures),
        len(fixtures),
        latest_completed_kickoff,
    )


def _result(goals_for: int, goals_against: int) -> Literal["W", "D", "L"]:
    if goals_for > goals_against:
        return "W"
    if goals_for < goals_against:
        return "L"
    return "D"


def _team_observations(fixtures: list[dict]) -> dict[str, list[dict]]:
    observations: dict[str, list[dict]] = {}

    for fixture in fixtures:
        home_id = str(fixture.get("home_team_id") or "").strip()
        away_id = str(fixture.get("away_team_id") or "").strip()
        home_score = int(fixture["home_score"])
        away_score = int(fixture["away_score"])
        kickoff = str(fixture.get("kickoff_time") or "").strip()
        fixture_id = int(str(fixture.get("fixture_id") or "0"))

        observations.setdefault(home_id, []).append(
            {
                "kickoff": kickoff,
                "fixture_id": fixture_id,
                "venue": "home",
                "goals_for": home_score,
                "goals_against": away_score,
                "result": _result(home_score, away_score),
            }
        )
        observations.setdefault(away_id, []).append(
            {
                "kickoff": kickoff,
                "fixture_id": fixture_id,
                "venue": "away",
                "goals_for": away_score,
                "goals_against": home_score,
                "result": _result(away_score, home_score),
            }
        )

    for rows in observations.values():
        rows.sort(key=lambda row: (row["kickoff"], row["fixture_id"]))

    return observations


def _selected_observations(
    observations: list[dict],
    view: LeagueTableView,
) -> list[dict]:
    if view == "home":
        return [row for row in observations if row["venue"] == "home"]
    if view == "away":
        return [row for row in observations if row["venue"] == "away"]
    if view == "last5":
        return observations[-5:]
    return observations


def _split_table_rows(
    base_rows: list[dict],
    fixtures: list[dict],
    view: LeagueTableView,
) -> list[dict]:
    observations = _team_observations(fixtures)
    rows: list[dict] = []

    for base in base_rows:
        team_id = str(base["team_id"])
        selected = _selected_observations(observations.get(team_id, []), view)
        wins = sum(row["result"] == "W" for row in selected)
        draws = sum(row["result"] == "D" for row in selected)
        losses = sum(row["result"] == "L" for row in selected)
        goals_for = sum(int(row["goals_for"]) for row in selected)
        goals_against = sum(int(row["goals_against"]) for row in selected)

        rows.append(
            {
                "team_id": team_id,
                "persistent_team_code": str(base.get("persistent_team_code") or ""),
                "team": str(base["team"]),
                "played": len(selected),
                "wins": wins,
                "draws": draws,
                "losses": losses,
                "goals_for": goals_for,
                "goals_against": goals_against,
                "goal_difference": goals_for - goals_against,
                "points": wins * 3 + draws,
                "form": [row["result"] for row in selected[-5:]],
            }
        )

    rows.sort(
        key=lambda item: (
            -item["points"],
            -item["goal_difference"],
            -item["goals_for"],
            item["team"].casefold(),
        )
    )

    for position, row in enumerate(rows, start=1):
        row["position"] = position

    return rows


def _overall_rows_with_form(
    base_rows: list[dict],
    fixtures: list[dict],
) -> list[dict]:
    observations = _team_observations(fixtures)
    rows: list[dict] = []

    for base in base_rows:
        row = dict(base)
        team_id = str(base["team_id"])
        row["form"] = [
            item["result"]
            for item in observations.get(team_id, [])[-5:]
        ]
        rows.append(row)

    return rows


@router.get("/api/v1/league-table/{season}", response_model=LeagueTableResult)
def get_league_table(
    season: str,
    view: LeagueTableView = "overall",
) -> LeagueTableResult:
    try:
        table = query_api.league_table(season)
        fixtures, completed, total, latest_completed_kickoff = _completed_fixture_context(season)
        information_available_as_of, source_release_sha = _release_metadata(
            season,
            completed,
            total,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="League table failed safely.") from exc

    base_rows = list(table.get("teams", []))
    selected_rows = (
        _overall_rows_with_form(base_rows, fixtures)
        if view == "overall"
        else _split_table_rows(base_rows, fixtures, view)
    )

    rows = [
        LeagueTableRow(
            position=int(row["position"]),
            persistent_team_code=str(row.get("persistent_team_code") or ""),
            display_name=str(row["team"]),
            local_team_id=str(row["team_id"]),
            played=int(row["played"]),
            wins=int(row["wins"]),
            draws=int(row["draws"]),
            losses=int(row["losses"]),
            goals_for=int(row["goals_for"]),
            goals_against=int(row["goals_against"]),
            goal_difference=int(row["goal_difference"]),
            points=int(row["points"]),
            form=list(row.get("form") or []),
        )
        for row in selected_rows
    ]

    view_note = {
        "overall": "Overall includes every completed league fixture represented for the season.",
        "home": "Home includes only each club's completed home league fixtures.",
        "away": "Away includes only each club's completed away league fixtures.",
        "last5": "Last 5 includes each club's five most recent completed league fixtures, or fewer where five have not yet been played.",
    }[view]

    return LeagueTableResult(
        season=season,
        competition="Premier League",
        view=view,
        rows=rows,
        completed_fixtures=completed,
        scheduled_fixtures=max(total - completed, 0),
        total_fixtures=total,
        latest_completed_kickoff=latest_completed_kickoff,
        information_available_as_of=information_available_as_of,
        source_release_sha=source_release_sha,
        query_version=str(table.get("query_version") or "unknown"),
        limitations=[
            view_note,
            "The table is derived only from completed fixtures represented in the canonical fixture master.",
            "Scheduled fixtures do not contribute points, goals or form until a completed result is represented.",
            "A living-season table is partial-season state, not a completed-season comparison.",
            "No historical information-availability reconstruction is asserted unless an explicit release boundary is shown.",
        ],
    )
