from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field

import player_match_stats
import query_api

router = APIRouter()


class CanonicalFixtureRef(BaseModel):
    model_config = ConfigDict(frozen=True)
    season: str
    fixture_id: str


class ResearchPopulation(BaseModel):
    label: str
    sample_size: int
    filters: dict[str, str | int | bool]
    exclusions: list[str] = Field(default_factory=list)


class ResearchScope(BaseModel):
    competition: str | None = None
    season: str | None = None
    as_of: str | None = None


class ResearchProvenance(BaseModel):
    source: str
    transformation_version: str


class ResearchMethodology(BaseModel):
    metric_version: str
    notes: list[str] = Field(default_factory=list)


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


class FixturePlayerMatchEvidence(BaseModel):
    source_match_id: str
    source_player_id: str | None = None
    source_name: str | None = None
    position: str | None = None
    side: Literal["home", "away"] | None = None
    participation: Literal["starting", "sub_in", "bench", "unknown"]
    minutes: float | None = None


class FixtureDetailResult(BaseModel):
    fixture: FixtureResultRow
    stats: FixtureDetailStats | None = None
    player_match: list[FixturePlayerMatchEvidence] = Field(default_factory=list)
    player_match_status: Literal["AVAILABLE", "UNAVAILABLE", "KNOWN_EXCEPTION"]
    provenance: ResearchProvenance
    limitations: list[str] = Field(default_factory=list)


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


def _normalise_int(value: str | int | float | None) -> int | None:
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


def _flatten_fixture_stats(stats: dict | None) -> FixtureDetailStats | None:
    if not stats or stats.get("status") != "AVAILABLE":
        return None
    home_core = stats.get("home", {}).get("core", {})
    home_optional = stats.get("home", {}).get("optional", {})
    away_core = stats.get("away", {}).get("core", {})
    away_optional = stats.get("away", {}).get("optional", {})
    return FixtureDetailStats(
        home_possession=_normalise_float(home_core.get("Possession")),
        away_possession=_normalise_float(away_core.get("Possession")),
        home_shots_on_target=_normalise_int(home_core.get("Shots on target")),
        away_shots_on_target=_normalise_int(away_core.get("Shots on target")),
        home_shots=_normalise_int(home_core.get("Shots")),
        away_shots=_normalise_int(away_core.get("Shots")),
        home_corners=_normalise_int(home_core.get("Corners")),
        away_corners=_normalise_int(away_core.get("Corners")),
        home_fouls=_normalise_int(home_core.get("Fouls conceded")),
        away_fouls=_normalise_int(away_core.get("Fouls conceded")),
        home_yellow_cards=_normalise_int(home_core.get("Yellow cards")),
        away_yellow_cards=_normalise_int(away_core.get("Yellow cards")),
        attendance=_normalise_int(home_optional.get("Attendance")) if home_optional.get("Attendance") is not None else _normalise_int(away_optional.get("Attendance")),
    )


def _source_player_name(row: dict) -> str | None:
    explicit = row.get("playerName") or row.get("name") or row.get("player")
    if explicit:
        value = str(explicit).strip()
        if value:
            return value.replace("_", " ")
    first = str(row.get("first_name") or "").strip()
    second = str(row.get("second_name") or "").strip()
    combined = " ".join(part for part in (first, second) if part)
    return combined or None


def _fixture_player_match_evidence(fixture: dict) -> tuple[list[FixturePlayerMatchEvidence], str, str | None]:
    try:
        source_match_id = player_match_stats.player_match_id_for_fixture(fixture)
    except FileNotFoundError:
        return [], "UNAVAILABLE", None
    except ValueError as exc:
        message = str(exc)
        if str(fixture.get("season")) == "2019-20" and str(fixture.get("fixture_id")) == "275":
            return [], "KNOWN_EXCEPTION", message
        raise
    if source_match_id is None:
        status = "KNOWN_EXCEPTION" if str(fixture.get("season")) == "2019-20" and str(fixture.get("fixture_id")) == "275" else "UNAVAILABLE"
        return [], status, None
    rows = player_match_stats.fixture_player_match_rows(fixture)
    evidence: list[FixturePlayerMatchEvidence] = []
    for row in rows:
        venue = str(row.get("venue") or "").strip().lower()
        side: Literal["home", "away"] | None = None
        if venue == "home":
            side = "home"
        elif venue == "away":
            side = "away"
        evidence.append(
            FixturePlayerMatchEvidence(
                source_match_id=source_match_id,
                source_player_id=player_match_stats.source_player_id(row),
                source_name=_source_player_name(row),
                position=str(row.get("position") or row.get("positionText") or "").strip() or None,
                side=side,
                participation=player_match_stats.classify_participation(row),
                minutes=_normalise_float(row.get("minutesPlayed")),
            )
        )
    return evidence, "AVAILABLE", None


@router.get("/api/v1/seasons")
def get_seasons() -> dict[str, list[str]]:
    try:
        seasons = list(query_api.list_seasons())
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Season list failed safely.") from exc
    return {"seasons": sorted(seasons, reverse=True)}


@router.get("/api/v1/teams/{season}", response_model=list[TeamOption])
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


@router.get("/api/v1/team-seasons", response_model=list[TeamSeasonOption])
def get_team_seasons(persistent_team_code: str = Query(..., min_length=1)) -> list[TeamSeasonOption]:
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
        match = next((option for option in options if option.persistent_team_code == requested_code), None)
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


@router.get("/api/v1/fixtures/{season}", response_model=FixtureResearchResult)
def get_fixtures(
    season: str,
    team: str = Query(..., min_length=1),
    opponent: str | None = Query(None),
    venue: Literal["home", "away"] | None = Query(None),
    result: Literal["W", "D", "L", "UNPLAYED"] | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
) -> FixtureResearchResult:
    try:
        payload = query_api.fixtures(season=season, team=team, opponent=opponent, venue=venue, result=result, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Fixture query failed safely.") from exc

    rows = [_row_for_api(row, team) for row in payload["results"]]
    references = {"fixtures": [CanonicalFixtureRef(season=season, fixture_id=row.fixture_id) for row in rows]}
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
        population=ResearchPopulation(label=f"{team} Premier League fixtures in {season}", sample_size=len(rows), filters=active_filters),
        scope=ResearchScope(competition="Premier League", season=season, as_of=None),
        references=references,
        provenance=ResearchProvenance(source="query_api.fixtures → fixtures_master_corrected.csv", transformation_version=str(payload.get("query_version", "unknown"))),
        methodology=ResearchMethodology(metric_version="fixture-results-v1", notes=["Fixture identity is represented as (season, fixture_id).", "Team identity is resolved by the existing trusted query layer."]),
        limitations=["No historical as-of information-availability snapshot is asserted by this endpoint yet.", "The frontend must not infer canonical identity from display names or provider-local IDs."],
    )


@router.get("/api/v1/fixtures/{season}/{fixture_id}", response_model=FixtureDetailResult)
def get_fixture_detail(season: str, fixture_id: str) -> FixtureDetailResult:
    try:
        detail = query_api.fixture_detail(season=season, fixture_id=fixture_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Fixture detail query failed safely.") from exc

    fixture = detail["fixture"]
    fixture_row = FixtureResultRow(
        fixture_id=str(fixture["fixture_id"]),
        season=str(fixture["season"]),
        gameweek=int(fixture["gameweek"]) if fixture.get("gameweek") not in (None, "") else None,
        kickoff_time=str(fixture["kickoff_time"]) if fixture.get("kickoff_time") else None,
        home_team_id=str(fixture["home_team_id"]),
        away_team_id=str(fixture["away_team_id"]),
        home_team_name=str(fixture["home_team_name"]),
        away_team_name=str(fixture["away_team_name"]),
        home_score=_normalise_int(fixture.get("home_score")),
        away_score=_normalise_int(fixture.get("away_score")),
    )

    try:
        player_match, player_match_status, player_match_note = _fixture_player_match_evidence(fixture)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Player-match evidence failed safely.") from exc

    limitations = [
        "Managers are not supplied because the approved FRL manager-data boundary does not currently expose them.",
        "Event timeline details are not yet part of the trusted fixture-detail seam.",
        "No historical as-of information-availability snapshot is asserted by this endpoint yet.",
    ]
    if player_match_status != "AVAILABLE":
        limitations.append("Player-match evidence is unavailable for this fixture in the current approved source boundary.")
    if player_match_note:
        limitations.append(player_match_note)

    return FixtureDetailResult(
        fixture=fixture_row,
        stats=_flatten_fixture_stats(detail.get("stats")),
        player_match=player_match,
        player_match_status=player_match_status,
        provenance=ResearchProvenance(source="query_api.fixture_detail → query_lab.fixture_detail → canonical fixture + match statistics; player-match evidence via player_match_stats", transformation_version=str(detail.get("query_version", "unknown"))),
        limitations=limitations,
    )
