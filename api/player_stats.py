from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

import player_analysis_kernel
import player_research


router = APIRouter()


class PlayerOption(BaseModel):
    player_code: str
    player_name: str
    position: str
    clubs: list[str]
    minutes: int
    appearances: int


class PlayerProfileMetric(BaseModel):
    key: str
    label: str
    value: float | None = None
    unit: str


class PlayerProfileResult(BaseModel):
    season: str
    player_code: str
    player_name: str
    position: str
    clubs: list[str]
    competition: str
    appearances: int
    starts: int
    minutes: int
    metrics: list[PlayerProfileMetric]
    evidence: dict[str, Any] = Field(default_factory=dict)
    limitations: list[str] = Field(default_factory=list)


class PlayerStatsCohort(BaseModel):
    competition: str
    season: str
    position: str
    minimum_minutes: int
    description: str


class PlayerStatsMetric(BaseModel):
    key: str
    label: str
    unit: str
    family: str
    higher_is_better: bool
    representation: str
    value: float | None = None
    rank: int | None = None
    out_of: int
    percentile: float | None = None
    availability: Literal["AVAILABLE", "PARTIAL", "UNAVAILABLE"]
    observed_players: int
    eligible_players: int
    ranking_policy: str
    percentile_policy: str


class PlayerStatsResult(BaseModel):
    analysis_version: str
    season: str
    player: PlayerOption
    cohort: PlayerStatsCohort
    overview_keys: list[str]
    metrics: list[PlayerStatsMetric]
    limitations: list[str] = Field(default_factory=list)


class PlayerRankingEntry(BaseModel):
    player_code: str
    player_name: str
    position: str
    clubs: list[str]
    minutes: int
    starts: int
    appearances: int
    value: float | None = None
    rank: int | None = None
    out_of: int
    percentile: float | None = None


class PlayerRankingMetric(BaseModel):
    key: str
    label: str
    unit: str
    family: str
    higher_is_better: bool
    representation: str
    availability: Literal["AVAILABLE", "PARTIAL", "UNAVAILABLE"]
    observed_players: int
    eligible_players: int
    ranking_policy: str
    percentile_policy: str
    entries: list[PlayerRankingEntry]


class PlayerRankingsResult(BaseModel):
    analysis_version: str
    season: str
    position: str
    population_size: int
    cohort: PlayerStatsCohort
    ranking_policy: str
    percentile_policy: str
    metrics: list[PlayerRankingMetric]


def _integer(value: object) -> int:
    try:
        return int(float(value or 0))
    except (TypeError, ValueError):
        return 0


def _option(player: dict) -> PlayerOption:
    return PlayerOption(
        player_code=str(player.get("player_code") or ""),
        player_name=str(player.get("player_name") or ""),
        position=str(player.get("position") or ""),
        clubs=list(player.get("clubs") or ()),
        minutes=_integer(player.get("minutes")),
        appearances=_integer(player.get("appearances")),
    )


def _profile_metrics(player: dict) -> list[PlayerProfileMetric]:
    definitions = (
        ("goals", "Goals", "goals"),
        ("assists", "Assists", "assists"),
        ("xg", "xG", "xG"),
        ("xa", "xA", "xA"),
        ("xgi", "xGI", "xGI"),
        ("clean_sheets", "Clean sheets", "clean sheets"),
        ("saves", "Saves", "saves"),
        ("tackles", "Tackles", "tackles"),
        ("recoveries", "Recoveries", "recoveries"),
        ("defensive_contribution", "Defensive contribution", "actions"),
        ("yellow_cards", "Yellow cards", "cards"),
        ("red_cards", "Red cards", "cards"),
        ("points", "FPL points", "points"),
    )

    metrics = []
    for key, label, unit in definitions:
        value = player.get(key)
        if value is None:
            continue
        metrics.append(
            PlayerProfileMetric(
                key=key,
                label=label,
                value=float(value),
                unit=unit,
            )
        )
    return metrics


@router.get("/api/v1/players/{season}", response_model=list[PlayerOption])
def get_players(season: str) -> list[PlayerOption]:
    try:
        players = player_research.season_players(season)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Player directory failed safely.") from exc

    return sorted(
        (_option(player) for player in players),
        key=lambda player: (player.player_name.casefold(), player.player_code),
    )


@router.get(
    "/api/v1/players/{season}/{player_code}",
    response_model=PlayerProfileResult,
)
def get_player_profile(season: str, player_code: str) -> PlayerProfileResult:
    try:
        player = player_research.player_detail(season, player_code)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Player profile failed safely.") from exc

    if player is None:
        raise HTTPException(status_code=404, detail="Player is unavailable for this season.")

    return PlayerProfileResult(
        season=season,
        player_code=str(player.get("player_code") or ""),
        player_name=str(player.get("player_name") or ""),
        position=str(player.get("position") or ""),
        clubs=list(player.get("clubs") or ()),
        competition="Premier League",
        appearances=_integer(player.get("appearances")),
        starts=_integer(player.get("starts")),
        minutes=_integer(player.get("minutes")),
        metrics=_profile_metrics(player),
        evidence=dict(player.get("_evidence") or {}),
        limitations=[
            "Profile totals use the governed season player-fixture aggregate available for the selected season.",
            "A profile can include a registered zero-minute player; analytical rankings require at least one recorded minute.",
            "FPL-native measures remain labelled as FPL measures and are not asserted as historically equivalent to richer Opta player-match fields.",
        ],
    )


@router.get(
    "/api/v1/player-stats/{season}/{player_code}",
    response_model=PlayerStatsResult,
)
def get_player_stats(season: str, player_code: str) -> PlayerStatsResult:
    try:
        result = player_analysis_kernel.player_analysis(season, player_code)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Player Stats analysis failed safely.") from exc

    if result is None:
        raise HTTPException(status_code=404, detail="Player Stats are unavailable for this player and season.")

    return PlayerStatsResult(
        analysis_version=str(result["analysis_version"]),
        season=str(result["season"]),
        player=PlayerOption(**result["player"]),
        cohort=PlayerStatsCohort(**result["cohort"]),
        overview_keys=list(result["overview_keys"]),
        metrics=[PlayerStatsMetric(**metric) for metric in result["metrics"]],
        limitations=[
            "Ranks and percentiles compare only players with the same listed position and at least one recorded minute in the selected season.",
            "The comparison cohort is intentionally permissive in V1 so early current-season data remains usable; a user-controlled minimum-minutes threshold can be added without changing metric definitions.",
            "Metrics with no governed representation in a season remain unavailable rather than being inferred from adjacent measures.",
        ],
    )


@router.get(
    "/api/v1/player-stats/{season}/rankings/{position}",
    response_model=PlayerRankingsResult,
)
def get_player_rankings(
    season: str,
    position: str,
    family: str | None = Query(None),
) -> PlayerRankingsResult:
    position = position.upper()
    if family and family not in set(player_analysis_kernel.FAMILIES):
        raise HTTPException(status_code=400, detail=f"Unsupported player metric family: {family}")

    try:
        analysis = player_analysis_kernel.season_position_analysis(season, position)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Player rankings failed safely.") from exc

    metrics = []
    for metric in analysis["metrics"].values():
        definition = metric["definition"]
        if family and family != "overview" and definition["family"] != family:
            continue
        if family == "overview" and definition["key"] not in set(
            player_analysis_kernel.OVERVIEW_KEYS_BY_POSITION[position]
        ):
            continue
        if metric["availability"] == "UNAVAILABLE":
            continue

        entries = sorted(
            metric["entries"],
            key=lambda entry: (
                entry.get("rank") is None,
                int(entry.get("rank") or 10_000),
                str(entry.get("player_name") or "").casefold(),
            ),
        )
        metrics.append(
            PlayerRankingMetric(
                key=str(definition["key"]),
                label=str(definition["label"]),
                unit=str(definition["unit"]),
                family=str(definition["family"]),
                higher_is_better=bool(definition["higher_is_better"]),
                representation=str(definition["representation"]),
                availability=metric["availability"],
                observed_players=int(metric["observed_players"]),
                eligible_players=int(metric["eligible_players"]),
                ranking_policy=str(metric["ranking_policy"]),
                percentile_policy=str(metric["percentile_policy"]),
                entries=[PlayerRankingEntry(**entry) for entry in entries],
            )
        )

    return PlayerRankingsResult(
        analysis_version=str(analysis["analysis_version"]),
        season=str(analysis["season"]),
        position=str(analysis["position"]),
        population_size=int(analysis["population_size"]),
        cohort=PlayerStatsCohort(**analysis["cohort"]),
        ranking_policy=str(analysis["ranking_policy"]),
        percentile_policy=str(analysis["percentile_policy"]),
        metrics=metrics,
    )
