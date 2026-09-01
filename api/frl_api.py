from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import player_match_stats
import fixture_evidence as fixture_evidence_module
from source_family_adapters import resolve_source_match as xi_resolve_source_match
from pulselive_fixture_evidence import (
    load_snapshot as xi_load_snapshot,
    normalise_lineups as xi_normalise_lineups,
    resource_payload as xi_resource_payload,
)
import query_api
import team_research_stats
import team_analysis_kernel


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


class TeamOverviewResult(BaseModel):
    persistent_team_code: str
    display_name: str
    season: str
    local_team_id: str
    competition: str
    position: int
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int
    provenance: ResearchProvenance
    limitations: list[str] = Field(default_factory=list)



class TeamStatsMetric(BaseModel):
    key: str
    label: str
    value: float
    unit: str
    rank: int
    out_of: int
    percentile: float
    higher_is_better: bool


class TeamStatsSplit(BaseModel):
    label: str
    matches: int
    points_per_match: float | None = None
    goals_for_per_match: float | None = None
    goals_against_per_match: float | None = None


class TeamStatsTrendPoint(BaseModel):
    fixture_id: str
    kickoff_time: str | None = None
    home: bool
    points: int
    goals_for: float | None = None
    goals_against: float | None = None
    shots: float | None = None
    shots_on_target: float | None = None
    possession: float | None = None


class TeamStatsAvailability(BaseModel):
    key: str
    label: str
    status: Literal["AVAILABLE", "PARTIAL", "UNAVAILABLE", "REVIEW_REQUIRED"]
    observed_matches: int
    eligible_matches: int
    representation: str
    note: str | None = None


class TeamStatsOverviewResult(BaseModel):
    persistent_team_code: str
    display_name: str
    season: str
    matches: int
    metrics: list[TeamStatsMetric]
    pass_accuracy: float | None = None
    clean_sheet_rate: float | None = None
    failed_to_score_rate: float | None = None
    expected_goals_per_match: float | None = None
    xg_overperformance: float | None = None
    splits: list[TeamStatsSplit]
    trend: list[TeamStatsTrendPoint]
    availability: list[TeamStatsAvailability] = Field(default_factory=list)
    provenance: ResearchProvenance
    limitations: list[str] = Field(default_factory=list)


class TeamEraRecordItem(BaseModel):
    label: str
    value: str
    detail: str | None = None


class TeamEraOverviewResult(BaseModel):
    persistent_team_code: str
    display_name: str
    first_season: str
    last_season: str
    season_count: int
    across_seasons: list[TeamEraRecordItem]
    team_records: list[TeamEraRecordItem]
    player_records_status: Literal["UNAVAILABLE"]
    player_records_note: str
    provenance: ResearchProvenance
    limitations: list[str] = Field(default_factory=list)


class TeamXIPlayer(BaseModel):
    player_id: str
    player_name: str
    position: str | None = None
    appearances: int
    starts: int
    minutes: int
    goals: int
    assists: int
    season_count: int


class TeamXISlot(BaseModel):
    slot_id: str
    line_index: int
    slot_index: int
    line_size: int
    x: float
    y: float
    role: Literal["GK", "DEF", "MID", "FWD"]
    player_id: str | None = None
    player_name: str | None = None
    position: str | None = None
    role_starts: int = 0
    appearances: int = 0


class TeamXIResult(BaseModel):
    persistent_team_code: str
    display_name: str
    season: str
    scope: Literal["season", "overall"]
    scope_label: str
    seasons_included: list[str]
    competition: str
    formation: str | None = None
    formation_uses: int
    formation_sample: int
    squad: list[TeamXIPlayer]
    xi: list[TeamXISlot]
    provenance: ResearchProvenance
    limitations: list[str]


class TeamRecordSequenceItem(BaseModel):
    result: Literal["W", "D", "L"]
    fixture_id: str
    season: str
    opponent: str
    venue: Literal["Home", "Away"]
    kickoff_time: str
    score: str


class TeamRecordRankEntry(BaseModel):
    rank: int
    label: str
    value: str
    relative: float


class TeamRecordItem(BaseModel):
    key: str
    label: str
    value: str
    detail: str | None = None
    fixture_id: str | None = None
    fixture_season: str | None = None
    percentage: float | None = None
    comparison_rank: int | None = None
    comparison_population: int | None = None
    top_percent: int | None = None
    comparison_basis: str | None = None
    ranking: list[TeamRecordRankEntry] = Field(default_factory=list)
    result_sequence: list[TeamRecordSequenceItem] = Field(default_factory=list)


class TeamPlayerLeaderboardRow(BaseModel):
    rank: int
    player_id: str
    player_name: str
    appearances: int
    goals: int
    assists: int
    goal_involvements: int


class TeamRecordCategory(BaseModel):
    key: Literal["results", "runs", "goals", "players", "matchday"]
    label: str
    status: Literal["AVAILABLE", "UNAVAILABLE"]
    items: list[TeamRecordItem] = Field(default_factory=list)
    leaderboard: list[TeamPlayerLeaderboardRow] = Field(default_factory=list)
    note: str | None = None


class TeamSeasonRecordsResult(BaseModel):
    persistent_team_code: str
    display_name: str
    season: str
    scope: Literal["season", "overall"]
    scope_label: str
    seasons_included: list[str]
    competition: str
    categories: list[TeamRecordCategory]
    provenance: ResearchProvenance
    limitations: list[str] = Field(default_factory=list)


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
        attendance=_normalise_int(home_optional.get("Attendance"))
        if home_optional.get("Attendance") is not None
        else _normalise_int(away_optional.get("Attendance")),
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
    if str(fixture.get("season")) not in set(player_match_stats.available_seasons()):
        return [], "UNAVAILABLE", (
            "The governed historical Player-Match source representation does "
            "not extend into this season."
        )
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


@app.get(
    "/api/v1/teams/{season}/{persistent_team_code}/overview",
    response_model=TeamOverviewResult,
)
def get_team_overview(season: str, persistent_team_code: str) -> TeamOverviewResult:
    try:
        table = query_api.league_table(season)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Team overview failed safely.") from exc

    requested_code = persistent_team_code.strip()
    row = next(
        (
            item
            for item in table["teams"]
            if str(item.get("persistent_team_code") or "").strip() == requested_code
        ),
        None,
    )
    if row is None:
        raise HTTPException(
            status_code=404,
            detail=f"Team {persistent_team_code} is unavailable in {season}.",
        )

    return TeamOverviewResult(
        persistent_team_code=requested_code,
        display_name=str(row["team"]),
        season=season,
        local_team_id=str(row["team_id"]),
        competition="Premier League",
        position=int(row["position"]),
        played=int(row["played"]),
        wins=int(row["wins"]),
        draws=int(row["draws"]),
        losses=int(row["losses"]),
        goals_for=int(row["goals_for"]),
        goals_against=int(row["goals_against"]),
        goal_difference=int(row["goal_difference"]),
        points=int(row["points"]),
        provenance=ResearchProvenance(
            source="query_api.league_table ? canonical fixtures + governed team identity",
            transformation_version=str(table.get("query_version", "unknown")),
        ),
        limitations=[
            "Season record reflects completed fixtures represented in the canonical fixture master.",
            "No historical information-availability as-of claim is made by this endpoint.",
        ],
    )




def _team_stats_split(
    label: str,
    rows: list[dict],
) -> TeamStatsSplit:
    if not rows:
        return TeamStatsSplit(
            label=label,
            matches=0,
        )

    points = 0
    goals_for = 0.0
    goals_against = 0.0
    scored_matches = 0

    for row in rows:
        gf = row.get("goals_for")
        ga = row.get("goals_against")

        if gf is None or ga is None:
            continue

        gf_value = float(gf)
        ga_value = float(ga)

        goals_for += gf_value
        goals_against += ga_value
        scored_matches += 1

        if gf_value > ga_value:
            points += 3
        elif gf_value == ga_value:
            points += 1

    matches = len(rows)

    return TeamStatsSplit(
        label=label,
        matches=matches,
        points_per_match=round(points / matches, 3),
        goals_for_per_match=(
            round(goals_for / scored_matches, 3)
            if scored_matches
            else None
        ),
        goals_against_per_match=(
            round(goals_against / scored_matches, 3)
            if scored_matches
            else None
        ),
    )


@app.get(
    "/api/v1/team-stats/{season}/{persistent_team_code}/overview",
    response_model=TeamStatsOverviewResult,
)
def get_team_stats_overview(
    season: str,
    persistent_team_code: str,
) -> TeamStatsOverviewResult:
    requested_code = persistent_team_code.strip()

    try:
        options = get_teams(season)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Team Stats context failed safely.",
        ) from exc

    selected = next(
        (
            option
            for option in options
            if option.persistent_team_code == requested_code
        ),
        None,
    )

    if selected is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Team {persistent_team_code} "
                f"is unavailable in {season}."
            ),
        )

    try:
        analysis = team_analysis_kernel.team_overview_analysis(
            season,
            requested_code,
        )

        if analysis is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Governed Team Stats are unavailable for "
                    f"{selected.display_name} in {season}."
                ),
            )

        stats = team_research_stats.team_season_stats(
            season,
            requested_code,
        )

        if stats.get("status") != "AVAILABLE":
            raise HTTPException(
                status_code=404,
                detail=(
                    "Governed Team Stats are unavailable for "
                    f"{selected.display_name} in {season}."
                ),
            )

        match_rows = list(
            team_research_stats.team_match_stats(
                season,
                requested_code,
            )
        )

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Team Stats Overview failed safely.",
        ) from exc

    metrics = [
        TeamStatsMetric(
            key=str(metric["key"]),
            label=str(metric["label"]),
            value=round(float(metric["value"]), 3),
            unit=str(metric["unit"]),
            rank=int(metric["rank"]),
            out_of=int(metric["out_of"]),
            percentile=float(metric["percentile"]),
            higher_is_better=bool(metric["higher_is_better"]),
        )
        for metric in analysis["metrics"]
        if metric.get("value") is not None
        and metric.get("rank") is not None
        and metric.get("percentile") is not None
    ]

    availability: list[TeamStatsAvailability] = []
    for metric in analysis["metrics"]:
        coverage = metric.get("coverage") or {}
        observed = int(coverage.get("observed_matches", 0))
        eligible = int(coverage.get("eligible_matches", stats.get("matches", 0)))
        value_available = metric.get("value") is not None
        status: Literal["AVAILABLE", "PARTIAL", "UNAVAILABLE", "REVIEW_REQUIRED"]
        if not value_available:
            status = "UNAVAILABLE"
        elif observed < eligible:
            status = "PARTIAL"
        else:
            status = "AVAILABLE"
        availability.append(
            TeamStatsAvailability(
                key=str(metric["key"]),
                label=str(metric["label"]),
                status=status,
                observed_matches=observed,
                eligible_matches=eligible,
                representation=str(metric["representation"]),
                note=(
                    None
                    if status == "AVAILABLE"
                    else (
                        "The governed representation is observed for only part of the eligible match population."
                        if status == "PARTIAL"
                        else "The required governed team-match representation is not available for this season."
                    )
                ),
            )
        )

    match_rows.sort(
        key=lambda row: (
            str(row.get("kickoff_time") or ""),
            str(row.get("fixture_id") or ""),
        )
    )

    trend: list[TeamStatsTrendPoint] = []

    for row in match_rows:
        gf = row.get("goals_for")
        ga = row.get("goals_against")
        points = 0

        if gf is not None and ga is not None:
            if float(gf) > float(ga):
                points = 3
            elif float(gf) == float(ga):
                points = 1

        trend.append(
            TeamStatsTrendPoint(
                fixture_id=str(row.get("fixture_id") or ""),
                kickoff_time=(
                    str(row.get("kickoff_time"))
                    if row.get("kickoff_time")
                    else None
                ),
                home=bool(row.get("home")),
                points=points,
                goals_for=(float(gf) if gf is not None else None),
                goals_against=(float(ga) if ga is not None else None),
                shots=(
                    float(row["Shots"])
                    if row.get("Shots") is not None
                    else None
                ),
                shots_on_target=(
                    float(row["Shots on target"])
                    if row.get("Shots on target") is not None
                    else None
                ),
                possession=(
                    float(row["Possession"])
                    if row.get("Possession") is not None
                    else None
                ),
            )
        )

    home_rows = [row for row in match_rows if row.get("home")]
    away_rows = [row for row in match_rows if not row.get("home")]

    xg = analysis.get("expected_goals") or {}
    expected_goals = xg.get("value")
    xg_overperformance = xg.get("xg_overperformance")
    availability.append(
        TeamStatsAvailability(
            key="expected_goals_per_match",
            label="Expected goals",
            status=(
                "AVAILABLE"
                if expected_goals is not None and xg.get("coverage_complete")
                else "PARTIAL"
                if expected_goals is not None
                else "UNAVAILABLE"
            ),
            observed_matches=int(xg.get("observed_matches", 0)),
            eligible_matches=int(xg.get("eligible_matches", stats.get("matches", 0))),
            representation=str(xg.get("representation") or "NO_GOVERNED_SEASON_ROUTE"),
            note=str(xg.get("note") or "") or None,
        )
    )

    limitations = [
        (
            "League ranks and percentiles are projections of the shared "
            "governed Team Stats season analysis result."
        ),
        (
            "Percentile is descriptive league context, not predictive "
            "evidence."
        ),
    ]

    if expected_goals is None:
        limitations.append(
            "Expected-goals evidence is omitted where no governed "
            "season representation is available."
        )
    elif not xg.get("coverage_complete"):
        limitations.append(
            "Expected-goals evidence is partial: "
            f"{xg.get('observed_matches', 0)} of "
            f"{xg.get('eligible_matches', 0)} team fixtures are observed. "
            "xG overperformance remains withheld until the season population "
            "is complete."
        )

    return TeamStatsOverviewResult(
        persistent_team_code=requested_code,
        display_name=selected.display_name,
        season=season,
        matches=int(stats.get("matches", 0)),
        metrics=metrics,
        pass_accuracy=(
            round(float(stats["pass_accuracy"]), 4)
            if stats.get("pass_accuracy") is not None
            else None
        ),
        clean_sheet_rate=(
            round(float(stats["clean_sheet_rate"]), 4)
            if stats.get("clean_sheet_rate") is not None
            else None
        ),
        failed_to_score_rate=(
            round(float(stats["failed_to_score_rate"]), 4)
            if stats.get("failed_to_score_rate") is not None
            else None
        ),
        expected_goals_per_match=(
            round(float(expected_goals), 3)
            if expected_goals is not None
            else None
        ),
        xg_overperformance=(
            round(float(xg_overperformance), 3)
            if xg_overperformance is not None
            else None
        ),
        splits=[
            _team_stats_split("Home", home_rows),
            _team_stats_split("Away", away_rows),
        ],
        trend=trend,
        availability=availability,
        provenance=ResearchProvenance(
            source=(
                "team_analysis_kernel + team_research_stats + governed "
                "expected-metric routing"
            ),
            transformation_version="team-stats-overview-kernel-v1",
        ),
        limitations=limitations,
    )



def _ordinal(value: int) -> str:
    mod100 = value % 100
    if 11 <= mod100 <= 13:
        return f"{value}th"
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(value % 10, "th")
    return f"{value}{suffix}"


def _longest_result_streak(matches: list[dict], allowed: set[str]) -> int:
    longest = 0
    current = 0

    for match in matches:
        if str(match.get("result")) in allowed:
            current += 1
            longest = max(longest, current)
        else:
            current = 0

    return longest


@app.get(
    "/api/v1/teams/{persistent_team_code}/era-overview",
    response_model=TeamEraOverviewResult,
)
def get_team_era_overview(persistent_team_code: str) -> TeamEraOverviewResult:
    requested_code = persistent_team_code.strip()

    try:
        available = get_team_seasons(requested_code)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Team FRL-era overview failed safely.",
        ) from exc

    if not available:
        raise HTTPException(
            status_code=404,
            detail=f"Team {persistent_team_code} is unavailable in the FRL dataset.",
        )

    season_records: list[dict] = []
    biggest_win: dict | None = None
    longest_win = {"value": 0, "season": None}
    longest_unbeaten = {"value": 0, "season": None}

    for option in available:
        table = query_api.league_table(option.season)
        row = next(
            (
                item
                for item in table["teams"]
                if str(item.get("persistent_team_code") or "").strip()
                == requested_code
            ),
            None,
        )
        if row is None:
            continue

        season_records.append(
            {
                "season": option.season,
                "position": int(row["position"]),
                "points": int(row["points"]),
                "wins": int(row["wins"]),
                "goals_for": int(row["goals_for"]),
                "goal_difference": int(row["goal_difference"]),
            }
        )

        fixtures = query_api.fixtures(
            season=option.season,
            team=option.display_name,
            limit=500,
        )["results"]

        for fixture in fixtures:
            if fixture.get("home_score") in (None, "") or fixture.get("away_score") in (None, ""):
                continue

            home_score = int(fixture["home_score"])
            away_score = int(fixture["away_score"])
            home_id = str(fixture["home_team_id"])
            away_id = str(fixture["away_team_id"])

            if str(option.local_team_id) == home_id:
                goals_for = home_score
                goals_against = away_score
                opponent = str(fixture["away_team_name"])
            elif str(option.local_team_id) == away_id:
                goals_for = away_score
                goals_against = home_score
                opponent = str(fixture["home_team_name"])
            else:
                continue

            margin = goals_for - goals_against
            if margin <= 0:
                continue

            candidate = {
                "margin": margin,
                "goals_for": goals_for,
                "goals_against": goals_against,
                "opponent": opponent,
                "season": option.season,
            }

            if biggest_win is None or (
                candidate["margin"],
                candidate["goals_for"],
            ) > (
                biggest_win["margin"],
                biggest_win["goals_for"],
            ):
                biggest_win = candidate

        form = query_api.team_form(
            season=option.season,
            team=option.display_name,
        )

        win_streak = _longest_result_streak(
            form["matches"],
            {"W"},
        )
        unbeaten_streak = _longest_result_streak(
            form["matches"],
            {"W", "D"},
        )

        if win_streak > longest_win["value"]:
            longest_win = {
                "value": win_streak,
                "season": option.season,
            }

        if unbeaten_streak > longest_unbeaten["value"]:
            longest_unbeaten = {
                "value": unbeaten_streak,
                "season": option.season,
            }

    if not season_records:
        raise HTTPException(
            status_code=404,
            detail="No verified FRL-era season records are available for this team.",
        )

    best_finish = min(
        season_records,
        key=lambda row: (row["position"], -row["points"]),
    )
    most_points = max(
        season_records,
        key=lambda row: (row["points"], row["goal_difference"]),
    )
    most_goals = max(
        season_records,
        key=lambda row: (row["goals_for"], row["points"]),
    )

    return TeamEraOverviewResult(
        persistent_team_code=requested_code,
        display_name=available[0].display_name,
        first_season=available[-1].season,
        last_season=available[0].season,
        season_count=len(season_records),
        across_seasons=[
            TeamEraRecordItem(
                label="Best league finish",
                value=_ordinal(best_finish["position"]),
                detail=best_finish["season"],
            ),
            TeamEraRecordItem(
                label="Most points",
                value=str(most_points["points"]),
                detail=most_points["season"],
            ),
            TeamEraRecordItem(
                label="Most league goals",
                value=str(most_goals["goals_for"]),
                detail=most_goals["season"],
            ),
        ],
        team_records=[
            TeamEraRecordItem(
                label="Biggest league win",
                value=(
                    f'{biggest_win["goals_for"]}?{biggest_win["goals_against"]}'
                    if biggest_win
                    else "Unavailable"
                ),
                detail=(
                    f'vs {biggest_win["opponent"]} ? {biggest_win["season"]}'
                    if biggest_win
                    else None
                ),
            ),
            TeamEraRecordItem(
                label="Longest winning run",
                value=f'{longest_win["value"]} matches',
                detail=str(longest_win["season"] or ""),
            ),
            TeamEraRecordItem(
                label="Longest unbeaten run",
                value=f'{longest_unbeaten["value"]} matches',
                detail=str(longest_unbeaten["season"] or ""),
            ),
        ],
        player_records_status="UNAVAILABLE",
        player_records_note=(
            "Team-scoped cross-season player career records are withheld until "
            "the governed player identity layer exposes that comparison safely."
        ),
        provenance=ResearchProvenance(
            source=(
                "query_api.league_table + query_api.fixtures + "
                "query_api.team_form + governed persistent team identity"
            ),
            transformation_version="team-era-overview-v1",
        ),
        limitations=[
            "FRL-era means the Premier League seasons currently represented in the governed FRL dataset, not club all-time history.",
            "Winning and unbeaten streak records are the best single-season league streaks in the represented FRL era.",
            "Player career records are intentionally not inferred from league-wide player leader queries.",
        ],
    )



def _record_date(value: object) -> str:
    if value in (None, ""):
        return "Date unavailable"
    return str(value).split("T", 1)[0]


def _best_streak(matches: list[dict], predicate) -> list[dict]:
    best: list[dict] = []
    current: list[dict] = []
    current_season: str | None = None

    for match in matches:
        match_season = str(match["season"])

        # Overall records must never bridge the summer between seasons.
        if current_season is not None and match_season != current_season:
            current = []

        current_season = match_season

        if predicate(match):
            current.append(match)

            if len(current) > len(best):
                best = list(current)
        else:
            current = []

    return best


def _fixture_record(
    key: str,
    label: str,
    match: dict | None,
    include_season: bool,
) -> TeamRecordItem:
    if match is None:
        return TeamRecordItem(
            key=key,
            label=label,
            value="Unavailable",
        )

    detail = (
        f'{match["venue"]} vs {match["opponent"]}'
        f' - {_record_date(match.get("kickoff_time"))}'
    )

    if include_season:
        detail += f' - {match["season"]}'

    return TeamRecordItem(
        key=key,
        label=label,
        value=f'{match["goals_for"]}-{match["goals_against"]}',
        detail=detail,
        fixture_id=str(match["fixture_id"]),
        fixture_season=str(match["season"]),
    )


def _streak_record(
    key: str,
    label: str,
    streak: list[dict],
    include_season: bool,
) -> TeamRecordItem:
    if not streak:
        return TeamRecordItem(
            key=key,
            label=label,
            value="0 matches",
        )

    start = _record_date(streak[0].get("kickoff_time"))
    end = _record_date(streak[-1].get("kickoff_time"))

    detail = start if start == end else f"{start} to {end}"

    if include_season:
        detail += f' - {streak[0]["season"]}'

    sequence: list[TeamRecordSequenceItem] = []

    for match in streak:
        # Tooltip score follows actual home-away scoreboard orientation.
        if match["venue"] == "Home":
            score = f'{match["goals_for"]}-{match["goals_against"]}'
        else:
            score = f'{match["goals_against"]}-{match["goals_for"]}'

        sequence.append(
            TeamRecordSequenceItem(
                result=match["result"],
                fixture_id=str(match["fixture_id"]),
                season=str(match["season"]),
                opponent=str(match["opponent"]),
                venue=match["venue"],
                kickoff_time=_record_date(match.get("kickoff_time")),
                score=score,
            )
        )

    return TeamRecordItem(
        key=key,
        label=label,
        value=f"{len(streak)} matches",
        detail=detail,
        result_sequence=sequence,
    )



def _goal_comparison_profiles(
    seasons: list[str],
) -> dict[str, dict]:
    profiles: dict[str, dict] = {}

    for comparison_season in seasons:
        options = get_teams(comparison_season)

        by_local_id = {
            str(option.local_team_id): option
            for option in options
            if option.persistent_team_code
        }

        payload = query_api.fixtures(
            season=comparison_season,
            team=None,
            limit=500,
        )

        for fixture in payload["results"]:
            if (
                fixture.get("home_score") in (None, "")
                or fixture.get("away_score") in (None, "")
            ):
                continue

            home_option = by_local_id.get(
                str(fixture["home_team_id"])
            )
            away_option = by_local_id.get(
                str(fixture["away_team_id"])
            )

            if home_option is None or away_option is None:
                continue

            home_score = int(fixture["home_score"])
            away_score = int(fixture["away_score"])

            for option, goals_for, goals_against in (
                (home_option, home_score, away_score),
                (away_option, away_score, home_score),
            ):
                code = str(option.persistent_team_code)

                profile = profiles.setdefault(
                    code,
                    {
                        "display_name": option.display_name,
                        "matches": 0,
                        "goals_for": 0,
                        "goals_against": 0,
                        "clean_sheets": 0,
                        "scored_2_plus": 0,
                        "scored_3_plus": 0,
                        "scored_4_plus": 0,
                        "conceded_2_plus": 0,
                    },
                )

                profile["display_name"] = option.display_name
                profile["matches"] += 1
                profile["goals_for"] += goals_for
                profile["goals_against"] += goals_against
                profile["clean_sheets"] += int(goals_against == 0)
                profile["scored_2_plus"] += int(goals_for >= 2)
                profile["scored_3_plus"] += int(goals_for >= 3)
                profile["scored_4_plus"] += int(goals_for >= 4)
                profile["conceded_2_plus"] += int(goals_against >= 2)

    return profiles


def _goal_comparison_value(
    profile: dict,
    metric: str,
) -> float:
    matches = int(profile["matches"])

    if matches <= 0:
        return 0.0

    if metric == "goals_for":
        return float(profile["goals_for"]) / matches

    if metric == "goals_against":
        return float(profile["goals_against"]) / matches

    return float(profile[metric]) / matches


def _apply_goal_comparisons(
    category: TeamRecordCategory,
    profiles: dict[str, dict],
    persistent_team_code: str,
) -> None:
    target = profiles.get(persistent_team_code)

    if target is None or int(target["matches"]) <= 0:
        return

    definitions = {
        "goals-scored": (
            "goals_for",
            True,
            "goals per match",
        ),
        "goals-conceded": (
            "goals_against",
            False,
            "goals conceded per match",
        ),
        "clean-sheets": (
            "clean_sheets",
            True,
            "clean-sheet rate",
        ),
        "scored-two-plus": (
            "scored_2_plus",
            True,
            "matches scoring 2+",
        ),
        "scored-three-plus": (
            "scored_3_plus",
            True,
            "matches scoring 3+",
        ),
        "scored-four-plus": (
            "scored_4_plus",
            True,
            "matches scoring 4+",
        ),
        "conceded-two-plus": (
            "conceded_2_plus",
            False,
            "matches conceding 2+",
        ),
    }

    eligible = {
        code: profile
        for code, profile in profiles.items()
        if int(profile["matches"]) > 0
    }

    population = len(eligible)

    for record in category.items:
        definition = definitions.get(record.key)

        if definition is None or population == 0:
            continue

        metric, higher_is_better, label = definition

        target_value = _goal_comparison_value(
            target,
            metric,
        )

        values = [
            _goal_comparison_value(profile, metric)
            for profile in eligible.values()
        ]

        if higher_is_better:
            better = sum(
                value > target_value + 1e-12
                for value in values
            )
        else:
            better = sum(
                value < target_value - 1e-12
                for value in values
            )

        rank = better + 1

        # "Top X%" is based on competitive rank:
        # 1st of 20 = Top 5%, 2nd = Top 10%, etc.
        top_percent = max(
            1,
            (rank * 100 + population - 1) // population,
        )

        if metric in {"goals_for", "goals_against"}:
            basis = f"{target_value:.2f} {label}"
        else:
            basis = f"{target_value * 100:.1f}% {label}"

        record.comparison_rank = rank
        record.comparison_population = population
        record.top_percent = top_percent
        record.comparison_basis = basis


_PLAYER_RECORD_COMPARISON_CACHE: dict[
    tuple[str, ...],
    tuple[dict, ...],
] = {}


def _competition_player_record_profiles(
    seasons: list[str],
) -> list[dict]:
    """Build league-wide player comparison profiles efficiently.

    Each season is handled with:
      1. one canonical fixture pass;
      2. one cached Player-Match row pass.

    This preserves the existing clean-sheet and personal scoring-streak
    definitions without resolving every fixture independently.
    """
    cache_key = tuple(seasons)

    cached = _PLAYER_RECORD_COMPARISON_CACHE.get(cache_key)

    if cached is not None:
        return [dict(player) for player in cached]

    players = [
        dict(player)
        for player in player_match_stats.competition_player_totals(
            seasons
        )
        if int(player.get("appearances", 0)) > 0
    ]

    players_by_id = {
        str(player["player_id"]): player
        for player in players
    }

    for player in players:
        player["clean_sheets"] = 0
        player["longest_scoring_streak"] = 0
        player["_scoring_appearances"] = []

    for selected_season in seasons:
        team_options = get_teams(selected_season)

        local_to_persistent = {
            str(option.local_team_id):
            str(option.persistent_team_code)
            for option in team_options
        }

        # This index is already cached inside player_match_stats.
        pair_index = (
            player_match_stats._player_match_pair_index(
                selected_season
            )
        )

        fixture_payload = query_api.fixtures(
            season=selected_season,
            limit=500,
        )

        # Resolve canonical fixtures to source matchIds ONCE.
        match_context: dict[str, dict] = {}

        for fixture in fixture_payload["results"]:
            if (
                fixture.get("home_score") in (None, "")
                or fixture.get("away_score") in (None, "")
            ):
                continue

            home_team = local_to_persistent.get(
                str(fixture.get("home_team_id", ""))
            )
            away_team = local_to_persistent.get(
                str(fixture.get("away_team_id", ""))
            )

            if not home_team or not away_team:
                continue

            source_matches = pair_index.get(
                (home_team, away_team),
                (),
            )

            # Fail closed on absent/ambiguous evidence.
            if len(source_matches) != 1:
                continue

            source_match_id = source_matches[0]

            match_context[source_match_id] = {
                "home_team": home_team,
                "away_team": away_team,
                "home_score": int(fixture["home_score"]),
                "away_score": int(fixture["away_score"]),
                "kickoff_time": str(
                    fixture.get("kickoff_time") or ""
                ),
            }

        seen_player_matches: set[
            tuple[str, str]
        ] = set()

        # One linear pass over the season's cached source rows.
        for row in player_match_stats._source_match_records(
            selected_season
        ):
            player_id = (
                player_match_stats.source_player_id(row)
            )

            if (
                not player_id
                or player_id not in players_by_id
            ):
                continue

            match_id = str(
                row.get("matchId", "")
            ).strip()

            context = match_context.get(match_id)

            if context is None:
                continue

            try:
                minutes = float(
                    row.get("minutesPlayed") or 0
                )
            except (TypeError, ValueError):
                minutes = 0.0

            if minutes <= 0:
                continue

            dedupe_key = (
                player_id,
                match_id,
            )

            if dedupe_key in seen_player_matches:
                continue

            seen_player_matches.add(dedupe_key)

            try:
                goals = int(
                    float(row.get("goals") or 0)
                )
            except (TypeError, ValueError):
                goals = 0

            player = players_by_id[player_id]

            player["_scoring_appearances"].append(
                {
                    "season": selected_season,
                    "kickoff_time": context[
                        "kickoff_time"
                    ],
                    "goals": goals,
                }
            )

            team_id = str(
                row.get("team_id", "")
            ).strip()

            if team_id == context["home_team"]:
                goals_against = context["away_score"]
            elif team_id == context["away_team"]:
                goals_against = context["home_score"]
            else:
                continue

            if minutes >= 60 and goals_against == 0:
                player["clean_sheets"] += 1

    # Personal scoring streak:
    # consecutive PLAYER appearances, with season boundaries resetting.
    for player in players:
        appearances = sorted(
            player["_scoring_appearances"],
            key=lambda item: (
                item["season"],
                item["kickoff_time"],
            ),
        )

        best = 0
        current = 0
        current_season = None

        for appearance in appearances:
            season = appearance["season"]

            if (
                current_season is not None
                and season != current_season
            ):
                current = 0

            current_season = season

            if appearance["goals"] > 0:
                current += 1
                best = max(best, current)
            else:
                current = 0

        player["longest_scoring_streak"] = best
        player.pop("_scoring_appearances", None)

    cached_result = tuple(
        dict(player)
        for player in players
    )

    _PLAYER_RECORD_COMPARISON_CACHE[
        cache_key
    ] = cached_result

    return [
        dict(player)
        for player in cached_result
    ]


def _team_player_records_category(
    seasons: list[str],
    persistent_team_code: str,
    scope: Literal["season", "overall"],
) -> TeamRecordCategory:
    try:
        players = list(
            player_match_stats.team_player_totals(
                seasons,
                persistent_team_code,
            )
        )
    except Exception:
        return TeamRecordCategory(
            key="players",
            label="Players",
            status="UNAVAILABLE",
            note=(
                "Player record evidence could not be resolved safely "
                "through the governed Player-Match source."
            ),
        )

    if not players:
        return TeamRecordCategory(
            key="players",
            label="Players",
            status="UNAVAILABLE",
            note="No governed player-match observations are available.",
        )

    players_by_id = {
        str(player["player_id"]): player
        for player in players
    }

    for player in players:
        player["clean_sheets"] = 0
        player["longest_scoring_streak"] = 0
        player["_scoring_appearances"] = []

    # ------------------------------------------------------------
    # Fixture-level enrichment:
    #   - clean-sheet appearances
    #   - chronological personal scoring appearances
    #
    # Player membership remains match-scoped, so transfers remain safe.
    # ------------------------------------------------------------

    seen_player_fixtures: set[tuple[str, str, str]] = set()

    for selected_season in seasons:
        option = next(
            (
                item
                for item in get_teams(selected_season)
                if str(item.persistent_team_code)
                == str(persistent_team_code)
            ),
            None,
        )

        if option is None:
            continue

        fixture_payload = query_api.fixtures(
            season=selected_season,
            team=option.display_name,
            limit=500,
        )

        for fixture in fixture_payload["results"]:
            if (
                fixture.get("home_score") in (None, "")
                or fixture.get("away_score") in (None, "")
            ):
                continue

            home_score = int(fixture["home_score"])
            away_score = int(fixture["away_score"])

            if str(fixture["home_team_id"]) == str(option.local_team_id):
                goals_against = away_score
            elif str(fixture["away_team_id"]) == str(option.local_team_id):
                goals_against = home_score
            else:
                continue

            try:
                source_rows = (
                    player_match_stats.fixture_player_match_rows(
                        fixture
                    )
                )
            except Exception:
                # Fail closed at the individual fixture rather than
                # inventing player evidence.
                continue

            for row in source_rows:
                if (
                    str(row.get("team_id", "")).strip()
                    != str(persistent_team_code)
                ):
                    continue

                player_id = player_match_stats.source_player_id(row)

                if not player_id or player_id not in players_by_id:
                    continue

                try:
                    minutes = float(
                        row.get("minutesPlayed") or 0
                    )
                except (TypeError, ValueError):
                    minutes = 0.0

                if minutes <= 0:
                    continue

                fixture_key = (
                    selected_season,
                    str(fixture["fixture_id"]),
                    player_id,
                )

                if fixture_key in seen_player_fixtures:
                    continue

                seen_player_fixtures.add(fixture_key)

                try:
                    goals = int(float(row.get("goals") or 0))
                except (TypeError, ValueError):
                    goals = 0

                player = players_by_id[player_id]

                player["_scoring_appearances"].append(
                    {
                        "season": selected_season,
                        "kickoff_time": str(
                            fixture.get("kickoff_time") or ""
                        ),
                        "goals": goals,
                    }
                )

                # Conservative, reproducible definition:
                # player completed at least 60 minutes in a fixture
                # where the team finished with zero goals conceded.
                if minutes >= 60 and goals_against == 0:
                    player["clean_sheets"] += 1

    # ------------------------------------------------------------
    # Longest personal scoring streak
    #
    # Consecutive PLAYER appearances, not consecutive team fixtures.
    # Missing a match therefore does not break the player's streak.
    # Overall mode does not stitch separate seasons together.
    # ------------------------------------------------------------

    for player in players:
        appearances = sorted(
            player["_scoring_appearances"],
            key=lambda item: (
                item["season"],
                item["kickoff_time"],
            ),
        )

        best = 0
        current = 0
        current_season: str | None = None

        for appearance in appearances:
            appearance_season = appearance["season"]

            if (
                current_season is not None
                and appearance_season != current_season
            ):
                current = 0

            current_season = appearance_season

            if appearance["goals"] > 0:
                current += 1
                best = max(best, current)
            else:
                current = 0

        player["longest_scoring_streak"] = best

    goal_involvement_leaders = sorted(
        players,
        key=lambda player: (
            -int(player.get("goal_involvements", 0)),
            -int(player.get("goals", 0)),
            -int(player.get("assists", 0)),
            -int(player.get("appearances", 0)),
            player["player_name"].casefold(),
        ),
    )

    leaderboard = [
        TeamPlayerLeaderboardRow(
            rank=index,
            player_id=str(player["player_id"]),
            player_name=player["player_name"],
            appearances=int(player["appearances"]),
            goals=int(player["goals"]),
            assists=int(player["assists"]),
            goal_involvements=int(
                player["goal_involvements"]
            ),
        )
        for index, player in enumerate(
            goal_involvement_leaders[:20],
            start=1,
        )
    ]

    definitions = [
        (
            "top-scorer",
            "Top scorer",
            "goals",
            "goals",
        ),
        (
            "most-assists",
            "Most assists",
            "assists",
            "assists",
        ),
        (
            "goal-involvements",
            "Most goal involvements",
            "goal_involvements",
            "goal involvements",
        ),
        (
            "most-clean-sheets",
            "Most clean sheets",
            "clean_sheets",
            "clean sheets",
        ),
        (
            "most-appearances",
            "Most appearances",
            "appearances",
            "appearances",
        ),
        (
            "longest-scoring-streak",
            "Longest scoring streak",
            "longest_scoring_streak",
            "appearances",
        ),
    ]

    def display_amount(
        metric: str,
        amount: int,
        unit: str,
    ) -> str:
        if metric == "longest_scoring_streak":
            return (
                f"{amount} consecutive "
                f"{'appearance' if amount == 1 else 'appearances'}"
            )

        return f"{amount} {unit}"

    competition_players = [
        player
        for player in player_match_stats.competition_player_totals(
            seasons
        )
        if int(player.get("appearances", 0)) > 0
    ]

    items: list[TeamRecordItem] = []

    for key, label, metric, unit in definitions:
        ranked = sorted(
            players,
            key=lambda player: (
                -int(player.get(metric, 0)),
                -int(player.get("minutes", 0)),
                -int(player.get("appearances", 0)),
                player["player_name"].casefold(),
            ),
        )

        leader = ranked[0]
        leader_amount = int(leader.get(metric, 0))

        ranking: list[TeamRecordRankEntry] = []

        for index, player in enumerate(ranked[:3], start=1):
            amount = int(player.get(metric, 0))

            relative = (
                round(
                    (amount / leader_amount) * 100,
                    1,
                )
                if leader_amount > 0
                else 0.0
            )

            ranking.append(
                TeamRecordRankEntry(
                    rank=index,
                    label=player["player_name"],
                    value=display_amount(
                        metric,
                        amount,
                        unit,
                    ),
                    relative=relative,
                )
            )

        achievement = display_amount(
            metric,
            leader_amount,
            unit,
        )

        if (
            scope == "overall"
            and metric != "longest_scoring_streak"
        ):
            seasons_played = leader["season_count"]

            detail = (
                f"{achievement} - "
                f"{seasons_played} represented "
                f"{'season' if seasons_played == 1 else 'seasons'}"
            )
        else:
            detail = achievement

        comparison_rank = None
        comparison_population = None
        top_percent = None
        comparison_basis = None

        if key == "top-scorer" and competition_players:
            scoring_total = int(leader.get("goals", 0))

            better = sum(
                int(player.get("goals", 0)) > scoring_total
                for player in competition_players
            )

            comparison_rank = better + 1
            comparison_population = len(
                competition_players
            )

            top_percent = max(
                1,
                (
                    comparison_rank * 100
                    + comparison_population
                    - 1
                )
                // comparison_population,
            )

            comparison_basis = (
                f"{scoring_total} goals - "
                f"#{comparison_rank} of "
                f"{comparison_population} "
                f"Premier League players"
            )

        items.append(
            TeamRecordItem(
                key=key,
                label=label,
                value=leader["player_name"],
                detail=detail,
                ranking=ranking,
                comparison_rank=comparison_rank,
                comparison_population=comparison_population,
                top_percent=top_percent,
                comparison_basis=comparison_basis,
            )
        )

    # PLAYER_ALL_SIX_COMPARISONS_START
    competition_players = (
        _competition_player_record_profiles(seasons)
    )

    metric_by_key = {
        "top-scorer": "goals",
        "most-assists": "assists",
        "goal-involvements": "goal_involvements",
        "most-clean-sheets": "clean_sheets",
        "most-appearances": "appearances",
        "longest-scoring-streak": "longest_scoring_streak",
    }

    basis_label = {
        "goals": "goalscorers",
        "assists": "players with an assist",
        "goal_involvements": "players with a goal involvement",
        "clean_sheets": "players with a qualifying clean sheet",
        "appearances": "players with an appearance",
        "longest_scoring_streak": "players with a scoring streak",
    }

    for item in items:
        metric = metric_by_key.get(item.key)

        if not metric:
            continue

        # Only compare against players who actually qualify
        # for this particular record category.
        qualified_players = [
            player
            for player in competition_players
            if int(player.get(metric, 0)) > 0
        ]

        if not qualified_players:
            continue

        amount = max(
            int(player.get(metric, 0))
            for player in players
        )

        rank = (
            sum(
                int(player.get(metric, 0)) > amount
                for player in qualified_players
            )
            + 1
        )

        population = len(qualified_players)

        item.comparison_rank = rank
        item.comparison_population = population
        item.top_percent = max(
            1,
            (rank * 100 + population - 1) // population,
        )

        item.comparison_basis = (
            f"#{rank} of {population} represented "
            f"Premier League {basis_label[metric]}"
        )
    # PLAYER_ALL_SIX_COMPARISONS_END

    return TeamRecordCategory(
        key="players",
        label="Players",
        status="AVAILABLE",
        items=items,
        leaderboard=leaderboard,
        note=(
            "Clean sheets require 60+ minutes in a team clean-sheet fixture. "
            "Scoring streaks use consecutive player appearances and do not "
            "bridge separate seasons."
        ),
    )


@app.get(
    "/api/v1/teams/{season}/{persistent_team_code}/records",
    response_model=TeamSeasonRecordsResult,
)
def get_team_season_records(
    season: str,
    persistent_team_code: str,
    scope: Literal["season", "overall"] = Query("season"),
) -> TeamSeasonRecordsResult:
    requested_code = persistent_team_code.strip()

    try:
        if scope == "overall":
            options = get_team_seasons(requested_code)
        else:
            selected = next(
                (
                    option
                    for option in get_teams(season)
                    if option.persistent_team_code == requested_code
                ),
                None,
            )
            options = [selected] if selected is not None else []

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Team record book failed safely.",
        ) from exc

    if not options:
        raise HTTPException(
            status_code=404,
            detail=f"Team {persistent_team_code} is unavailable.",
        )

    # Chronological season order is important for deterministic records.
    options = sorted(options, key=lambda option: option.season)

    seasons_included = [option.season for option in options]
    display_name = options[-1].display_name
    include_season = scope == "overall"

    scope_label = (
        season
        if scope == "season"
        else (
            f"{seasons_included[0]} to {seasons_included[-1]}"
            f" - {len(seasons_included)} seasons"
        )
    )

    matches: list[dict] = []

    for option in options:
        try:
            payload = query_api.fixtures(
                season=option.season,
                team=option.display_name,
                limit=500,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail="Team record fixture query failed safely.",
            ) from exc

        for fixture in payload["results"]:
            if (
                fixture.get("home_score") in (None, "")
                or fixture.get("away_score") in (None, "")
            ):
                continue

            home_score = int(fixture["home_score"])
            away_score = int(fixture["away_score"])

            if str(option.local_team_id) == str(fixture["home_team_id"]):
                goals_for = home_score
                goals_against = away_score
                opponent = str(fixture["away_team_name"])
                venue: Literal["Home", "Away"] = "Home"

            elif str(option.local_team_id) == str(fixture["away_team_id"]):
                goals_for = away_score
                goals_against = home_score
                opponent = str(fixture["home_team_name"])
                venue = "Away"

            else:
                continue

            if goals_for > goals_against:
                result: Literal["W", "D", "L"] = "W"
            elif goals_for == goals_against:
                result = "D"
            else:
                result = "L"

            matches.append(
                {
                    "season": option.season,
                    "fixture_id": str(fixture["fixture_id"]),
                    "kickoff_time": fixture.get("kickoff_time"),
                    "opponent": opponent,
                    "venue": venue,
                    "goals_for": goals_for,
                    "goals_against": goals_against,
                    "result": result,
                }
            )

    matches.sort(
        key=lambda match: (
            match["season"],
            str(match.get("kickoff_time") or ""),
            match["fixture_id"],
        )
    )

    if not matches:
        unavailable = [
            TeamRecordCategory(
                key="results",
                label="Results",
                status="UNAVAILABLE",
                note="No completed governed league fixtures are available.",
            ),
            TeamRecordCategory(
                key="runs",
                label="Runs & streaks",
                status="UNAVAILABLE",
                note="No completed governed league fixtures are available.",
            ),
            TeamRecordCategory(
                key="goals",
                label="Goals",
                status="UNAVAILABLE",
                note="No completed governed league fixtures are available.",
            ),
            TeamRecordCategory(
                key="players",
                label="Players",
                status="UNAVAILABLE",
                note="Team-scoped player records are not yet governed.",
            ),
            TeamRecordCategory(
                key="matchday",
                label="Matchday",
                status="UNAVAILABLE",
                note="Season-wide matchday comparison is not yet governed.",
            ),
        ]

        return TeamSeasonRecordsResult(
            persistent_team_code=requested_code,
            display_name=display_name,
            season=season,
            scope=scope,
            scope_label=scope_label,
            seasons_included=seasons_included,
            competition="Premier League",
            categories=unavailable,
            provenance=ResearchProvenance(
                source="query_api.fixtures + governed persistent team identity",
                transformation_version="team-records-v2",
            ),
        )

    wins = [match for match in matches if match["result"] == "W"]
    losses = [match for match in matches if match["result"] == "L"]

    biggest_win = max(
        wins,
        key=lambda match: (
            match["goals_for"] - match["goals_against"],
            match["goals_for"],
        ),
        default=None,
    )

    biggest_defeat = max(
        losses,
        key=lambda match: (
            match["goals_against"] - match["goals_for"],
            match["goals_against"],
        ),
        default=None,
    )

    biggest_home_win = max(
        (match for match in wins if match["venue"] == "Home"),
        key=lambda match: (
            match["goals_for"] - match["goals_against"],
            match["goals_for"],
        ),
        default=None,
    )

    biggest_away_win = max(
        (match for match in wins if match["venue"] == "Away"),
        key=lambda match: (
            match["goals_for"] - match["goals_against"],
            match["goals_for"],
        ),
        default=None,
    )

    highest_scoring = max(
        matches,
        key=lambda match: (
            match["goals_for"] + match["goals_against"],
            match["goals_for"],
        ),
    )

    longest_win = _best_streak(
        matches,
        lambda match: match["result"] == "W",
    )

    results_category = TeamRecordCategory(
        key="results",
        label="Results",
        status="AVAILABLE",
        items=[
            _fixture_record(
                "biggest-win",
                "Biggest win",
                biggest_win,
                include_season,
            ),
            _fixture_record(
                "biggest-defeat",
                "Biggest defeat",
                biggest_defeat,
                include_season,
            ),
            _fixture_record(
                "biggest-home-win",
                "Biggest home win",
                biggest_home_win,
                include_season,
            ),
            _fixture_record(
                "biggest-away-win",
                "Biggest away win",
                biggest_away_win,
                include_season,
            ),
            _fixture_record(
                "highest-scoring-match",
                "Highest-scoring match",
                highest_scoring,
                include_season,
            ),
            _streak_record(
                "winning-streak",
                "Longest winning streak",
                longest_win,
                include_season,
            ),
        ],
    )

    runs_category = TeamRecordCategory(
        key="runs",
        label="Runs & streaks",
        status="AVAILABLE",
        items=[
            _streak_record(
                "winning-streak",
                "Longest winning streak",
                longest_win,
                include_season,
            ),
            _streak_record(
                "unbeaten-streak",
                "Longest unbeaten streak",
                _best_streak(matches, lambda match: match["result"] != "L"),
                include_season,
            ),
            _streak_record(
                "losing-streak",
                "Longest losing streak",
                _best_streak(matches, lambda match: match["result"] == "L"),
                include_season,
            ),
            _streak_record(
                "winless-streak",
                "Longest winless streak",
                _best_streak(matches, lambda match: match["result"] != "W"),
                include_season,
            ),
            _streak_record(
                "scoring-streak",
                "Longest scoring streak",
                _best_streak(matches, lambda match: match["goals_for"] > 0),
                include_season,
            ),
            _streak_record(
                "goalless-streak",
                "Longest goalless streak",
                _best_streak(matches, lambda match: match["goals_for"] == 0),
                include_season,
            ),
            _streak_record(
                "clean-sheet-streak",
                "Longest clean-sheet streak",
                _best_streak(matches, lambda match: match["goals_against"] == 0),
                include_season,
            ),
            _streak_record(
                "conceding-streak",
                "Longest conceding streak",
                _best_streak(matches, lambda match: match["goals_against"] > 0),
                include_season,
            ),
        ],
    )

    total_matches = len(matches)
    goals_for = sum(match["goals_for"] for match in matches)
    goals_against = sum(match["goals_against"] for match in matches)

    clean_sheets = sum(
        match["goals_against"] == 0 for match in matches
    )
    scored_2_plus = sum(
        match["goals_for"] >= 2 for match in matches
    )
    scored_3_plus = sum(
        match["goals_for"] >= 3 for match in matches
    )
    scored_4_plus = sum(
        match["goals_for"] >= 4 for match in matches
    )
    conceded_2_plus = sum(
        match["goals_against"] >= 2 for match in matches
    )

    most_goals_match = max(
        matches,
        key=lambda match: (
            match["goals_for"],
            -match["goals_against"],
        ),
    )

    def percentage(count: int) -> float:
        return round((count / total_matches) * 100, 1)

    goals_category = TeamRecordCategory(
        key="goals",
        label="Goals",
        status="AVAILABLE",
        items=[
            TeamRecordItem(
                key="goals-scored",
                label="League goals scored",
                value=str(goals_for),
                detail=f"Across {total_matches} completed matches",
            ),
            TeamRecordItem(
                key="goals-conceded",
                label="League goals conceded",
                value=str(goals_against),
                detail=f"Across {total_matches} completed matches",
            ),
            TeamRecordItem(
                key="clean-sheets",
                label="Clean sheets",
                value=str(clean_sheets),
                detail=f"{clean_sheets} of {total_matches} matches",
                percentage=percentage(clean_sheets),
            ),
            TeamRecordItem(
                key="scored-two-plus",
                label="Matches scoring 2+",
                value=str(scored_2_plus),
                detail=f"{scored_2_plus} of {total_matches} matches",
                percentage=percentage(scored_2_plus),
            ),
            TeamRecordItem(
                key="scored-three-plus",
                label="Matches scoring 3+",
                value=str(scored_3_plus),
                detail=f"{scored_3_plus} of {total_matches} matches",
                percentage=percentage(scored_3_plus),
            ),
            TeamRecordItem(
                key="scored-four-plus",
                label="Matches scoring 4+",
                value=str(scored_4_plus),
                detail=f"{scored_4_plus} of {total_matches} matches",
                percentage=percentage(scored_4_plus),
            ),
            TeamRecordItem(
                key="conceded-two-plus",
                label="Matches conceding 2+",
                value=str(conceded_2_plus),
                detail=f"{conceded_2_plus} of {total_matches} matches",
                percentage=percentage(conceded_2_plus),
            ),
            _fixture_record(
                "most-goals-match",
                "Most goals scored in a match",
                most_goals_match,
                include_season,
            ),
        ],
    )

    comparison_seasons = (
        [season]
        if scope == "season"
        else sorted(query_api.list_seasons())
    )

    comparison_profiles = _goal_comparison_profiles(
        comparison_seasons
    )

    _apply_goal_comparisons(
        goals_category,
        comparison_profiles,
        requested_code,
    )

    return TeamSeasonRecordsResult(
        persistent_team_code=requested_code,
        display_name=display_name,
        season=season,
        scope=scope,
        scope_label=scope_label,
        seasons_included=seasons_included,
        competition="Premier League",
        categories=[
            results_category,
            runs_category,
            goals_category,
            _team_player_records_category(
                seasons_included,
                requested_code,
                scope,
            ),
            TeamRecordCategory(
                key="matchday",
                label="Matchday",
                status="UNAVAILABLE",
                note=(
                    "Attendance and event-level records remain withheld "
                    "until season-wide comparison is governed."
                ),
            ),
        ],
        provenance=ResearchProvenance(
            source=(
                "query_api.fixtures + governed persistent team identity + "
                "Player-Match club-scoped evidence"
            ),
            transformation_version="team-records-v3",
        ),
        limitations=[
            (
                "Individual season mode covers the selected Premier League season."
                if scope == "season"
                else
                "Overall mode covers all represented Premier League seasons for this persistent club in FRL."
            ),
            "Overall streaks never join separate seasons together.",
            "Tied records retain the first chronological occurrence.",
            "FRL overall records are dataset-era records, not club all-time records.",
        ],
    )


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
        provenance=ResearchProvenance(
            source="query_api.fixture_detail → query_lab.fixture_detail → canonical fixture + match statistics; player-match evidence via player_match_stats",
            transformation_version=str(detail.get("query_version", "unknown")),
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


# TEAM_XI_V1

_TEAM_XI_CACHE: dict[
    tuple[str, str, str],
    TeamXIResult,
] = {}


_TEAM_XI_SAMPLE_CACHE: dict[
    tuple[tuple[str, ...], str],
    list[dict],
] = {}


def _xi_formation_counts(
    formation: str | None,
) -> tuple[int, ...] | None:
    parts = str(formation or "").strip().split("-")

    if (
        not parts
        or any(not part.isdigit() for part in parts)
    ):
        return None

    counts = tuple(int(part) for part in parts)

    if (
        any(count <= 0 for count in counts)
        or sum(counts) != 10
    ):
        return None

    return counts


def _xi_coordinates(
    line_index: int,
    slot_index: int,
    line_size: int,
    outfield_lines: int,
) -> tuple[float, float]:
    if line_size == 1:
        x = 50.0
    else:
        span = min(
            64.0,
            24.0 * (line_size - 1),
        )

        x = (
            50.0
            + span / 2.0
            - span * slot_index / (line_size - 1)
        )

    y = (
        8.0
        if line_index == 0
        else 8.0
        + 83.0 * line_index / outfield_lines
    )

    return round(x, 2), round(y, 2)


def _xi_role(
    line_index: int,
    outfield_lines: int,
) -> Literal["GK", "DEF", "MID", "FWD"]:
    if line_index == 0:
        return "GK"

    if line_index == 1:
        return "DEF"

    if line_index == outfield_lines:
        return "FWD"

    return "MID"


def _xi_target_slots(
    formation: str,
) -> list[dict]:
    counts = _xi_formation_counts(formation)

    if counts is None:
        return []

    line_sizes = (1, *counts)
    slots: list[dict] = []

    for line_index, line_size in enumerate(line_sizes):
        for slot_index in range(line_size):
            x, y = _xi_coordinates(
                line_index,
                slot_index,
                line_size,
                len(counts),
            )

            slots.append(
                {
                    "slot_id": (
                        f"{line_index}-"
                        f"{slot_index}-"
                        f"{line_size}"
                    ),
                    "line_index": line_index,
                    "slot_index": slot_index,
                    "line_size": line_size,
                    "x": x,
                    "y": y,
                    "role": _xi_role(
                        line_index,
                        len(counts),
                    ),
                }
            )

    return slots


def _xi_seasons_for_team(
    persistent_team_code: str,
) -> list[str]:
    seasons: list[str] = []

    for candidate in query_api.list_seasons():
        if any(
            str(option.persistent_team_code)
            == str(persistent_team_code)
            for option in get_teams(candidate)
        ):
            seasons.append(candidate)

    return seasons


def _xi_fixture_samples(
    seasons: list[str],
    persistent_team_code: str,
) -> list[dict]:
    """Read formation XIs directly from preserved lineup evidence.

    The PulseLive source ID is bridged to the exact Player-Match
    player identity through the established pl_code relationship.
    """
    cache_key = (
        tuple(seasons),
        str(persistent_team_code),
    )

    cached = _TEAM_XI_SAMPLE_CACHE.get(cache_key)

    if cached is not None:
        return cached

    samples: list[dict] = []

    for selected_season in seasons:
        option = next(
            (
                option
                for option in get_teams(selected_season)
                if str(option.persistent_team_code)
                == str(persistent_team_code)
            ),
            None,
        )

        if option is None:
            continue

        player_bridge = (
            player_match_stats.pulselive_player_bridge_index(
                selected_season
            )
        )

        fixture_payload = query_api.fixtures(
            season=selected_season,
            team=option.display_name,
            limit=500,
        )

        for fixture in fixture_payload["results"]:
            if (
                str(fixture.get("home_team_id"))
                == str(option.local_team_id)
            ):
                side = "home"
            elif (
                str(fixture.get("away_team_id"))
                == str(option.local_team_id)
            ):
                side = "away"
            else:
                continue

            try:
                source_match = xi_resolve_source_match(
                    selected_season,
                    str(fixture["fixture_id"]),
                )

                snapshot, _ = xi_load_snapshot(
                    str(source_match["source_match_id"])
                )
            except Exception:
                continue

            if snapshot is None:
                continue

            lineup_data = xi_normalise_lineups(
                xi_resource_payload(
                    snapshot,
                    "lineups",
                )
            )

            formation_side = (
                lineup_data.get(
                    "formations",
                    {},
                ).get(side)
                or {}
            )

            if (
                formation_side.get("status")
                != "AVAILABLE"
            ):
                continue

            formation = str(
                formation_side.get("value") or ""
            ).strip()

            counts = _xi_formation_counts(
                formation
            )

            if counts is None:
                continue

            expected = (1, *counts)
            starting: list[dict] = []

            for row in lineup_data.get(
                "players",
                [],
            ):
                if row.get("side") != side:
                    continue

                order = row.get(
                    "source_formation_order"
                )

                if not isinstance(order, dict):
                    continue

                pulselive_id = str(
                    row.get("source_player_id")
                    or ""
                ).strip()

                bridge = player_bridge.get(
                    pulselive_id
                )

                if bridge is None:
                    continue

                try:
                    line_index = int(
                        order["line_index"]
                    )
                    slot_index = int(
                        order["slot_index"]
                    )
                    line_size = int(
                        order["line_size"]
                    )
                except (
                    KeyError,
                    TypeError,
                    ValueError,
                ):
                    continue

                if not (
                    0 <= line_index < len(expected)
                ):
                    continue

                if (
                    line_size != expected[line_index]
                    or not 0 <= slot_index < line_size
                ):
                    continue

                x, y = _xi_coordinates(
                    line_index,
                    slot_index,
                    line_size,
                    len(counts),
                )

                starting.append(
                    {
                        "player_id":
                            bridge["player_id"],
                        "player_name":
                            bridge["player_name"],
                        "position":
                            bridge.get("position"),
                        "line_index": line_index,
                        "slot_index": slot_index,
                        "line_size": line_size,
                        "x": x,
                        "y": y,
                        "role": _xi_role(
                            line_index,
                            len(counts),
                        ),
                    }
                )

            slot_keys = {
                (
                    row["line_index"],
                    row["slot_index"],
                    row["line_size"],
                )
                for row in starting
            }

            player_ids = {
                row["player_id"]
                for row in starting
            }

            if (
                len(starting) != 11
                or len(slot_keys) != 11
                or len(player_ids) != 11
            ):
                continue

            samples.append(
                {
                    "season": selected_season,
                    "fixture_id": str(
                        fixture["fixture_id"]
                    ),
                    "formation": formation,
                    "players": starting,
                }
            )

    _TEAM_XI_SAMPLE_CACHE[
        cache_key
    ] = samples

    return samples


def _xi_assign_season(
    formation: str,
    samples: list[dict],
    squad_by_id: dict[str, dict],
) -> list[TeamXISlot]:
    target = _xi_target_slots(formation)

    formation_samples = [
        sample
        for sample in samples
        if sample["formation"] == formation
    ]

    counts: dict[
        str,
        dict[str, int],
    ] = {}

    names: dict[str, str] = {}
    positions: dict[str, str | None] = {}

    for sample in formation_samples:
        for player in sample["players"]:
            slot_id = (
                f'{player["line_index"]}-'
                f'{player["slot_index"]}-'
                f'{player["line_size"]}'
            )

            counts.setdefault(
                slot_id,
                {},
            )[player["player_id"]] = (
                counts.setdefault(
                    slot_id,
                    {},
                ).get(
                    player["player_id"],
                    0,
                )
                + 1
            )

            names[player["player_id"]] = (
                player["player_name"]
            )

            positions[player["player_id"]] = (
                player.get("position")
            )

    used: set[str] = set()
    result: list[TeamXISlot] = []

    for slot in target:
        candidates = sorted(
            counts.get(
                slot["slot_id"],
                {},
            ).items(),
            key=lambda item: (
                -item[1],
                -int(
                    squad_by_id.get(
                        item[0],
                        {},
                    ).get(
                        "starts",
                        0,
                    )
                ),
                -int(
                    squad_by_id.get(
                        item[0],
                        {},
                    ).get(
                        "appearances",
                        0,
                    )
                ),
                names.get(
                    item[0],
                    item[0],
                ).casefold(),
            ),
        )

        chosen = next(
            (
                item
                for item in candidates
                if item[0] not in used
            ),
            None,
        )

        player_id = (
            chosen[0]
            if chosen
            else None
        )

        role_starts = (
            chosen[1]
            if chosen
            else 0
        )

        if player_id:
            used.add(player_id)

        squad_player = (
            squad_by_id.get(
                player_id or "",
                {},
            )
        )

        result.append(
            TeamXISlot(
                **slot,
                player_id=player_id,
                player_name=(
                    squad_player.get("player_name")
                    or names.get(
                        player_id or ""
                    )
                    if player_id
                    else None
                ),
                position=(
                    squad_player.get("position")
                    or positions.get(
                        player_id or ""
                    )
                    if player_id
                    else None
                ),
                role_starts=role_starts,
                appearances=int(
                    squad_player.get(
                        "appearances",
                        0,
                    )
                ),
            )
        )

    return result


def _xi_assign_overall(
    formation: str,
    samples: list[dict],
    squad_by_id: dict[str, dict],
) -> list[TeamXISlot]:
    """Era XI in the era's most-used exact formation.

    Only starts made in the modal formation contribute. This means
    every player competes for the exact source-backed tactical slot
    shown on the pitch rather than being translated between shapes.
    """
    target = _xi_target_slots(formation)

    formation_samples = [
        sample
        for sample in samples
        if sample["formation"] == formation
    ]

    counts: dict[
        str,
        dict[str, int],
    ] = {
        slot["slot_id"]: {}
        for slot in target
    }

    names: dict[str, str] = {}
    positions: dict[str, str | None] = {}

    for sample in formation_samples:
        for player in sample["players"]:
            slot_id = (
                f'{player["line_index"]}-'
                f'{player["slot_index"]}-'
                f'{player["line_size"]}'
            )

            if slot_id not in counts:
                continue

            player_id = player["player_id"]

            counts[slot_id][player_id] = (
                counts[slot_id].get(
                    player_id,
                    0,
                )
                + 1
            )

            names[player_id] = (
                player["player_name"]
            )

            positions[player_id] = (
                player.get("position")
            )

    # Resolve the clearest slots first so a genuinely versatile
    # player is not duplicated elsewhere in the XI.
    def confidence(
        slot: dict,
    ) -> tuple[int, int]:
        values = sorted(
            counts[
                slot["slot_id"]
            ].values(),
            reverse=True,
        )

        first = values[0] if values else 0
        second = values[1] if len(values) > 1 else 0

        return first, first - second

    assignment_order = sorted(
        target,
        key=lambda slot: (
            -confidence(slot)[0],
            -confidence(slot)[1],
            slot["line_index"],
            slot["slot_index"],
        ),
    )

    used: set[str] = set()
    assigned: dict[str, TeamXISlot] = {}

    for slot in assignment_order:
        candidates = sorted(
            counts[
                slot["slot_id"]
            ].items(),
            key=lambda item: (
                -item[1],
                -int(
                    squad_by_id.get(
                        item[0],
                        {},
                    ).get(
                        "appearances",
                        0,
                    )
                ),
                -int(
                    squad_by_id.get(
                        item[0],
                        {},
                    ).get(
                        "starts",
                        0,
                    )
                ),
                names.get(
                    item[0],
                    item[0],
                ).casefold(),
            ),
        )

        chosen = next(
            (
                candidate
                for candidate in candidates
                if candidate[0] not in used
            ),
            None,
        )

        if chosen is None:
            continue

        player_id, slot_starts = chosen
        used.add(player_id)

        squad_player = squad_by_id.get(
            player_id,
            {},
        )

        assigned[
            slot["slot_id"]
        ] = TeamXISlot(
            **slot,
            player_id=player_id,
            player_name=(
                squad_player.get("player_name")
                or names.get(player_id)
            ),
            position=(
                squad_player.get("position")
                or positions.get(player_id)
            ),
            role_starts=slot_starts,
            appearances=int(
                squad_player.get(
                    "appearances",
                    0,
                )
            ),
        )

    return [
        assigned.get(
            slot["slot_id"],
            TeamXISlot(**slot),
        )
        for slot in target
    ]


def _team_xi_result(
    season: str,
    persistent_team_code: str,
    scope: Literal["season", "overall"],
) -> TeamXIResult:
    cache_key = (
        season,
        str(persistent_team_code),
        scope,
    )

    if cache_key in _TEAM_XI_CACHE:
        return _TEAM_XI_CACHE[cache_key]

    selected_option = next(
        (
            option
            for option in get_teams(season)
            if str(option.persistent_team_code)
            == str(persistent_team_code)
        ),
        None,
    )

    if selected_option is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Team {persistent_team_code} "
                f"is not represented in {season}."
            ),
        )

    seasons = (
        [season]
        if scope == "season"
        else _xi_seasons_for_team(
            str(persistent_team_code)
        )
    )

    raw_squad = list(
        player_match_stats.team_player_totals(
            seasons,
            str(persistent_team_code),
        )
    )

    raw_squad.sort(
        key=lambda player: (
            -int(
                player.get(
                    "appearances",
                    0,
                )
            ),
            -int(
                player.get(
                    "starts",
                    0,
                )
            ),
            -int(
                player.get(
                    "minutes",
                    0,
                )
            ),
            player["player_name"].casefold(),
        )
    )

    squad = [
        TeamXIPlayer(
            player_id=str(
                player["player_id"]
            ),
            player_name=player[
                "player_name"
            ],
            position=player.get(
                "position"
            ),
            appearances=int(
                player.get(
                    "appearances",
                    0,
                )
            ),
            starts=int(
                player.get(
                    "starts",
                    0,
                )
            ),
            minutes=int(
                player.get(
                    "minutes",
                    0,
                )
            ),
            goals=int(
                player.get(
                    "goals",
                    0,
                )
            ),
            assists=int(
                player.get(
                    "assists",
                    0,
                )
            ),
            season_count=int(
                player.get(
                    "season_count",
                    1,
                )
            ),
        )
        for player in raw_squad
    ]

    squad_by_id = {
        player["player_id"]: player
        for player in raw_squad
    }

    samples = _xi_fixture_samples(
        seasons,
        str(persistent_team_code),
    )

    formation_counts: dict[
        str,
        int,
    ] = {}

    for sample in samples:
        formation_counts[
            sample["formation"]
        ] = (
            formation_counts.get(
                sample["formation"],
                0,
            )
            + 1
        )

    formation = (
        sorted(
            formation_counts.items(),
            key=lambda item: (
                -item[1],
                item[0],
            ),
        )[0][0]
        if formation_counts
        else None
    )

    formation_uses = (
        formation_counts.get(
            formation,
            0,
        )
        if formation
        else 0
    )

    if formation:
        xi = (
            _xi_assign_season(
                formation,
                samples,
                squad_by_id,
            )
            if scope == "season"
            else _xi_assign_overall(
                formation,
                samples,
                squad_by_id,
            )
        )
    else:
        xi = []

    scope_label = (
        season
        if scope == "season"
        else (
            f"{seasons[0]} to "
            f"{seasons[-1]} - "
            f"{len(seasons)} seasons"
            if seasons
            else "Overall"
        )
    )

    result = TeamXIResult(
        persistent_team_code=str(
            persistent_team_code
        ),
        display_name=(
            selected_option.display_name
        ),
        season=season,
        scope=scope,
        scope_label=scope_label,
        seasons_included=seasons,
        competition="Premier League",
        formation=formation,
        formation_uses=formation_uses,
        formation_sample=len(samples),
        squad=squad,
        xi=xi,
        provenance=ResearchProvenance(
            source=(
                "governed Player-Match participation + "
                "preserved PulseLive formation-line evidence"
            ),
            transformation_version="team-xi-v1",
        ),
        limitations=[
            (
                "Pitch positions use source formation-line "
                "ordering with deterministic presentation "
                "coordinates; they are not tracking coordinates."
            ),
            (
                "Fixtures without a complete governed "
                "formation XI are excluded from formation "
                "and role aggregation."
            ),
            (
                "Overall XI selects players by starts in "
                "goalkeeper, defensive, midfield and forward "
                "formation roles across represented FRL seasons."
            ),
        ],
    )

    _TEAM_XI_CACHE[
        cache_key
    ] = result

    return result


@app.get(
    "/api/v1/teams/{season}/{persistent_team_code}/xi",
    response_model=TeamXIResult,
)
def get_team_xi(
    season: str,
    persistent_team_code: str,
    scope: Literal["season", "overall"] = "season",
):
    return _team_xi_result(
        season,
        persistent_team_code,
        scope,
    )

