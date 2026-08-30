from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

import team_analysis_kernel


router = APIRouter()


class LeagueRankingEntry(BaseModel):
    persistent_team_code: str
    display_name: str
    local_team_id: str
    value: float | None = None
    rank: int | None = None
    out_of: int
    percentile: float | None = None
    coverage: dict[str, Any] = Field(default_factory=dict)


class LeagueRankingMetric(BaseModel):
    key: str
    label: str
    unit: str
    higher_is_better: bool
    representation: str
    ranking_policy: str
    percentile_policy: str
    entries: list[LeagueRankingEntry]


class TeamStatsLeagueRankingsResult(BaseModel):
    analysis_version: str
    season: str
    population_size: int
    ranking_policy: str
    percentile_policy: str
    metrics: list[LeagueRankingMetric]


def _ranking_order(entry: dict[str, Any]) -> tuple[bool, int, str]:
    rank = entry.get("rank")
    return (
        rank is None,
        int(rank) if rank is not None else 10_000,
        str(entry.get("display_name") or "").casefold(),
    )


def league_rankings_projection(season: str) -> TeamStatsLeagueRankingsResult:
    analysis = team_analysis_kernel.season_overview_analysis(season)
    metrics: list[LeagueRankingMetric] = []

    for key, metric in analysis["metrics"].items():
        definition = metric["definition"]
        entries = sorted(metric["entries"], key=_ranking_order)
        metrics.append(
            LeagueRankingMetric(
                key=key,
                label=str(definition["label"]),
                unit=str(definition["unit"]),
                higher_is_better=bool(definition["higher_is_better"]),
                representation=str(definition["representation"]),
                ranking_policy=str(metric["ranking_policy"]),
                percentile_policy=str(metric["percentile_policy"]),
                entries=[LeagueRankingEntry(**entry) for entry in entries],
            )
        )

    return TeamStatsLeagueRankingsResult(
        analysis_version=str(analysis["analysis_version"]),
        season=str(analysis["season"]),
        population_size=int(analysis["population_size"]),
        ranking_policy=str(analysis["ranking_policy"]),
        percentile_policy=str(analysis["percentile_policy"]),
        metrics=metrics,
    )


@router.get(
    "/api/v1/team-stats/{season}/rankings",
    response_model=TeamStatsLeagueRankingsResult,
)
def get_team_stats_league_rankings(season: str) -> TeamStatsLeagueRankingsResult:
    try:
        return league_rankings_projection(season)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=f"Unsupported season: {season}") from exc
