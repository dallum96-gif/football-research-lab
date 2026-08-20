from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import query_api


class CanonicalFixtureRef(BaseModel):
    model_config = ConfigDict(frozen=True)

    season: str
    fixture_id: str


class ResearchPopulation(BaseModel):
    label: str
    sample_size: int
    filters: dict[str, str | int | bool]
    exclusions: list[str] = []


class ResearchScope(BaseModel):
    competition: str | None = None
    season: str | None = None
    as_of: str | None = None


class ResearchProvenance(BaseModel):
    source: str
    transformation_version: str


class ResearchMethodology(BaseModel):
    metric_version: str
    notes: list[str] = []


class FixtureResultRow(BaseModel):
    fixture_id: str
    season: str
    gameweek: int | None = None
    kickoff_time: str | None = None
    home_team_id: str
    away_team_id: str
    home_team_name: str
    away_team_name: str
    home_score: int | None = None
    away_score: int | None = None
    venue: Literal["Home", "Away"] | None = None
    result: Literal["W", "D", "L", "UNPLAYED"] | None = None


class FixtureResearchResult(BaseModel):
    result_id: str
    title: str
    description: str
    data: list[FixtureResultRow]
    population: ResearchPopulation
    scope: ResearchScope
    references: dict[str, list[CanonicalFixtureRef]]
    provenance: ResearchProvenance
    methodology: ResearchMethodology
    limitations: list[str]


app = FastAPI(title="Football Research Laboratory API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


def _normalise_int(value: str | int | None) -> int | None:
    if value in (None, ""):
        return None
    return int(value)


def _row_for_api(row: dict, team_filter: str | None) -> FixtureResultRow:
    home = str(row["home_team_name"])
    away = str(row["away_team_name"])
    home_score = _normalise_int(row.get("home_score"))
    away_score = _normalise_int(row.get("away_score"))
    venue = None
    result = None

    if team_filter:
        if home.casefold() == team_filter.casefold():
            venue = "Home"
            if home_score is not None and away_score is not None:
                result = "W" if home_score > away_score else "D" if home_score == away_score else "L"
            else:
                result = "UNPLAYED"
        elif away.casefold() == team_filter.casefold():
            venue = "Away"
            if home_score is not None and away_score is not None:
                result = "W" if away_score > home_score else "D" if away_score == home_score else "L"
            else:
                result = "UNPLAYED"

    return FixtureResultRow(
        fixture_id=str(row["fixture_id"]),
        season=str(row["season"]),
        gameweek=int(row["gameweek"]) if row.get("gameweek") not in (None, "") else None,
        kickoff_time=str(row["kickoff_time"]) if row.get("kickoff_time") else None,
        home_team_id=str(row["home_team_id"]),
        away_team_id=str(row["away_team_id"]),
        home_team_name=home,
        away_team_name=away,
        home_score=home_score,
        away_score=away_score,
        venue=venue,
        result=result,
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "football-research-lab-api"}


@app.get("/api/v1/fixtures/{season}", response_model=FixtureResearchResult)
def get_fixtures(
    season: str,
    team: str = Query(..., min_length=1),
    opponent: str | None = Query(None),
    venue: Literal["home", "away"] | None = Query(None),
    result: Literal["W", "D", "L", "UNPLAYED"] | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
) -> FixtureResearchResult:
    try:
        payload = query_api.fixtures(
            season=season,
            team=team,
            opponent=opponent,
            venue=venue,
            result=result,
            limit=limit,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Fixture query failed safely.") from exc

    rows = [_row_for_api(row, team) for row in payload["results"]]
    references = {
        "fixtures": [
            CanonicalFixtureRef(season=season, fixture_id=row.fixture_id)
            for row in rows
        ]
    }

    active_filters: dict[str, str | int | bool] = {"team": team}
    if opponent:
        active_filters["opponent"] = opponent
    if venue:
        active_filters["venue"] = venue
    if result:
        active_filters["result"] = result

    return FixtureResearchResult(
        result_id=f"fixtures:{season}:{team}:{opponent or 'all'}:{venue or 'all'}:{result or 'all'}",
        title=f"{team} fixtures",
        description="Chronological fixture results returned by the trusted FRL fixture query seam.",
        data=rows,
        population=ResearchPopulation(
            label=f"{team} Premier League fixtures in {season}",
            sample_size=len(rows),
            filters=active_filters,
        ),
        scope=ResearchScope(
            competition="Premier League",
            season=season,
            as_of=None,
        ),
        references=references,
        provenance=ResearchProvenance(
            source="query_api.fixtures → fixtures_master_corrected.csv",
            transformation_version=str(payload.get("query_version", "unknown")),
        ),
        methodology=ResearchMethodology(
            metric_version="fixture-results-v1",
            notes=[
                "Fixture identity is represented as (season, fixture_id).",
                "Team identity is resolved by the existing trusted query layer.",
            ],
        ),
        limitations=[
            "No historical as-of information-availability snapshot is asserted by this endpoint yet.",
            "The frontend must not infer canonical identity from display names or provider-local IDs.",
        ],
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.frl_api:app",
        host=os.getenv("FRL_API_HOST", "127.0.0.1"),
        port=int(os.getenv("FRL_API_PORT", "8000")),
        reload=True,
    )
