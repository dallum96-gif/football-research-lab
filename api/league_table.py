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
    rows: list[LeagueTableRow]
    completed_fixtures: int
    scheduled_fixtures: int
    total_fixtures: int
    latest_completed_kickoff: str | None = None
    information_available_as_of: str | None = None
    source_release_sha: str | None = None
    query_version: str
    limitations: list[str] = Field(default_factory=list)


def _release_metadata(season: str) -> tuple[str | None, str | None]:
    register = SEASON_RELEASE_ROOT / season / "capability_gap_register.json"
    if not register.is_file():
        return None, None

    payload = json.loads(register.read_text(encoding="utf-8"))
    return (
        str(payload.get("information_available_as_of") or "") or None,
        str(payload.get("source_release_sha") or "") or None,
    )


def _fixture_context(season: str) -> tuple[dict[str, list[str]], int, int, str | None]:
    payload = query_api.fixtures(season=season, limit=1000)
    fixtures = list(payload.get("results") or [])
    form: dict[str, list[tuple[str, int, str]]] = {}
    completed = 0
    latest_completed_kickoff: str | None = None

    for fixture in fixtures:
        home_score = fixture.get("home_score")
        away_score = fixture.get("away_score")
        if home_score in (None, "") or away_score in (None, ""):
            continue

        completed += 1
        home_id = str(fixture.get("home_team_id") or "").strip()
        away_id = str(fixture.get("away_team_id") or "").strip()
        kickoff = str(fixture.get("kickoff_time") or "").strip()
        fixture_id = int(str(fixture.get("fixture_id") or "0"))
        home_value = int(home_score)
        away_value = int(away_score)

        if home_value > away_value:
            home_result, away_result = "W", "L"
        elif away_value > home_value:
            home_result, away_result = "L", "W"
        else:
            home_result = away_result = "D"

        form.setdefault(home_id, []).append((kickoff, fixture_id, home_result))
        form.setdefault(away_id, []).append((kickoff, fixture_id, away_result))

        if kickoff and (latest_completed_kickoff is None or kickoff > latest_completed_kickoff):
            latest_completed_kickoff = kickoff

    compact_form = {
        team_id: [result for _, _, result in sorted(rows, key=lambda row: (row[0], row[1]))[-5:]]
        for team_id, rows in form.items()
    }
    return compact_form, completed, len(fixtures), latest_completed_kickoff


@router.get("/api/v1/league-table/{season}", response_model=LeagueTableResult)
def get_league_table(season: str) -> LeagueTableResult:
    try:
        table = query_api.league_table(season)
        form, completed, total, latest_completed_kickoff = _fixture_context(season)
        information_available_as_of, source_release_sha = _release_metadata(season)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="League table failed safely.") from exc

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
            form=form.get(str(row["team_id"]), []),
        )
        for row in table.get("teams", [])
    ]

    return LeagueTableResult(
        season=season,
        competition="Premier League",
        rows=rows,
        completed_fixtures=completed,
        scheduled_fixtures=max(total - completed, 0),
        total_fixtures=total,
        latest_completed_kickoff=latest_completed_kickoff,
        information_available_as_of=information_available_as_of,
        source_release_sha=source_release_sha,
        query_version=str(table.get("query_version") or "unknown"),
        limitations=[
            "The table is derived only from completed fixtures represented in the canonical fixture master.",
            "Scheduled fixtures do not contribute points, goals or form until a completed result is represented.",
            "A living-season table is partial-season state, not a completed-season comparison.",
            "No historical information-availability reconstruction is asserted unless an explicit release boundary is shown.",
        ],
    )
