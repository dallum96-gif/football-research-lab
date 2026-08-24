from __future__ import annotations

import csv
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


class FixtureDetailStats(BaseModel):
    home_possession: float | None = None
    away_possession: float | None = None
    home_shots_on_target: int | None = None
    away_shots_on_target: int | None = None
    home_shots: int | None = None
    away_shots: int | None = None
    home_corners: int | None = None
    away_corners: int | None = None
    home_fouls: int | None = None
    away_fouls: int | None = None
    home_yellow_cards: int | None = None
    away_yellow_cards: int | None = None
    attendance: int | None = None


class FixtureDetailResult(BaseModel):
    fixture: FixtureResultRow
    stats: FixtureDetailStats | None = None
    provenance: ResearchProvenance
    limitations: list[str]


class TeamOption(BaseModel):
    persistent_team_code: str | None = None
    display_name: str
    season: str
    local_team_id: str


class TeamSeasonOption(BaseModel):
    persistent_team_code: str
    display_name: str
    season: str
    local_team_id: str


app = FastAPI(title="Football Research Laboratory API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"] ,
)


def _normalise_int(value: str | int | None) -> int | None:
    if value in (None, ""):
        return None
    return int(value)


def _normalise_float(value: str | float | int | None) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


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


def _load_fixture_detail(season: str, fixture_id: str) -> tuple[dict, dict | None]:
    fixture_rows = [
        row
        for row in query_api._load_csv(query_api.FIXTURE_FILE)
        if row.get("season") == season and str(row.get("fixture_id")) == fixture_id
    ]
    if not fixture_rows:
        raise ValueError(f"Fixture {season}/{fixture_id} was not found in the canonical fixture master.")

    stats_file = ROOT / "data" / "fixture_match_stats.csv"
    stats_rows = [
        row
        for row in query_api._load_csv(stats_file)
        if row.get("season") == season and str(row.get("fixture_id")) == fixture_id
    ] if stats_file.is_file() else []

    return fixture_rows[0], (stats_rows[0] if stats_rows else None)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "football-research-laboratory-api"}


@app.get("/api/v1/seasons")
def get_seasons() -> dict[str, list[str]]:
    try:
        seasons = list(query_api.list_seasons())
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Season list failed safely.") from exc

    return {"seasons": sorted(seasons, reverse=True)}


@app.get("/api/v1/teams/{season}", response_model=list[TeamOption])
def get_teams(season: str) -> list[TeamOption]:
    try:
        table = query_api.league_table(season)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Team list failed safely.") from exc

    return [
        TeamOption(
            persistent_team_code=row.get("persistent_team_code") or None,
            display_name=str(row["team"]),
            season=season,
            local_team_id=str(row["team_id"]),
        )
        for row in sorted(table["teams"], key=lambda item: item["team"].casefold())
    ]


@app.get("/api/v1/team-seasons", response_model=list[TeamSeasonOption])
def get_team_seasons(
    persistent_team_code: str = Query(..., min_length=1),
) -> list[TeamSeasonOption]:
    try:
        seasons = list(query_api.list_seasons())
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Season list failed safely.") from exc

    requested_code = persistent_team_code.strip()
    if not requested_code:
        raise HTTPException(status_code=400, detail="Persistent team code is required.")

    available: list[TeamSeasonOption] = []
    for season in seasons:
        try:
            options = get_teams(season)
        except HTTPException:
            continue
        match = next(
            (option for option in options if option.persistent_team_code == requested_code),
            None,
        )
        if match is not None:
            available.append(
                TeamSeasonOption(
                    persistent_team_code=requested_code,
                    display_name=match.display_name,
                    season=match.season,
                    local_team_id=match.local_team_id,
                )
            )

    available.sort(key=lambda item: item.season, reverse=True)
    return available


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


@app.get("/api/v1/fixtures/{season}/{fixture_id}", response_model=FixtureDetailResult)
def get_fixture_detail(season: str, fixture_id: str) -> FixtureDetailResult:
    try:
        row, stats = _load_fixture_detail(season, fixture_id)
        by_local_id, _, _ = query_api._team_lookup(season)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Fixture detail query failed safely.") from exc

    home_id = str(row.get("home_team_id", "")).strip()
    away_id = str(row.get("away_team_id", "")).strip()
    if home_id not in by_local_id or away_id not in by_local_id:
        raise HTTPException(status_code=500, detail="Fixture identity could not be resolved safely.")

    fixture = FixtureResultRow(
        fixture_id=fixture_id,
        season=season,
        gameweek=int(row["gameweek"]) if row.get("gameweek") not in (None, "") else None,
        kickoff_time=str(row["kickoff_time"]) if row.get("kickoff_time") else None,
        home_team_id=home_id,
        away_team_id=away_id,
        home_team_name=str(by_local_id[home_id]["team"]),
        away_team_name=str(by_local_id[away_id]["team"]),
        home_score=_normalise_int(row.get("home_score")),
        away_score=_normalise_int(row.get("away_score")),
    )

    detail_stats = None
    if stats is not None:
        home_fouls = _normalise_int(stats.get("away_core_fouls_won"))
        away_fouls = _normalise_int(stats.get("home_core_fouls_won"))
        attendance = _normalise_int(stats.get("home_optional_attendance"))
        if attendance is None:
            attendance = _normalise_int(stats.get("away_optional_attendance"))

        detail_stats = FixtureDetailStats(
            home_possession=_normalise_float(stats.get("home_core_possession")),
            away_possession=_normalise_float(stats.get("away_core_possession")),
            home_shots_on_target=_normalise_int(stats.get("home_core_shots_on_target")),
            away_shots_on_target=_normalise_int(stats.get("away_core_shots_on_target")),
            home_shots=_normalise_int(stats.get("home_core_shots")),
            away_shots=_normalise_int(stats.get("away_core_shots")),
            home_corners=_normalise_int(stats.get("home_core_corners")),
            away_corners=_normalise_int(stats.get("away_core_corners")),
            home_fouls=home_fouls,
            away_fouls=away_fouls,
            home_yellow_cards=_normalise_int(stats.get("home_core_yellow_cards")),
            away_yellow_cards=_normalise_int(stats.get("away_core_yellow_cards")),
            attendance=attendance,
        )

    limitations = [
        "Managers are not supplied because the approved FRL manager-data boundary does not currently expose them.",
        "Event timeline and player starting-lineup details are not yet part of this fixture-detail API contract.",
        "No historical as-of information-availability snapshot is asserted by this endpoint yet.",
    ]

    return FixtureDetailResult(
        fixture=fixture,
        stats=detail_stats,
        provenance=ResearchProvenance(
            source=(
                "fixtures_master_corrected.csv + data/fixture_match_stats.csv"
                if stats is not None
                else "fixtures_master_corrected.csv"
            ),
            transformation_version="fixture-detail-v1",
        ),
        limitations=limitations,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.frl_api:app",
        host=os.getenv("FRL_API_HOST", "127.0.0.1"),
        port=int(os.getenv("FRL_API_PORT", "8000")),
        reload=True,
    )
