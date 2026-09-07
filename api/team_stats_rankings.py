from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

import query_api
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
    if season not in set(query_api.list_seasons()):
        raise ValueError(f"Unsupported season: {season}")

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

    # Expected goals deliberately remains outside the generic
    # team_analysis_kernel.RANKING_METRICS registry because expected metrics
    # have their own governed representation-routing contract.  Project that
    # already-governed surface into the rankings API here.
    xg_observations = list(
        (analysis.get("expected_goals") or {}).values()
    )

    if any(
        observation.get("value") is not None
        for observation in xg_observations
    ):
        xg_entries = [
            {
                "persistent_team_code": str(
                    observation["persistent_team_code"]
                ),
                "display_name": str(observation["display_name"]),
                "local_team_id": str(observation["local_team_id"]),
                "value": (
                    float(observation["value"])
                    if observation.get("value") is not None
                    else None
                ),
                "coverage": {
                    "eligible_matches": int(
                        observation.get("eligible_matches", 0)
                    ),
                    "observed_matches": int(
                        observation.get("observed_matches", 0)
                    ),
                    "missing_matches": int(
                        observation.get("missing_matches", 0)
                    ),
                    "coverage_status": str(
                        observation.get(
                            "coverage_status",
                            "UNAVAILABLE",
                        )
                    ),
                    "coverage_complete": bool(
                        observation.get("coverage_complete", False)
                    ),
                },
            }
            for observation in xg_observations
        ]

        team_analysis_kernel.rank_metric_entries(
            xg_entries,
            higher_is_better=True,
        )

        representations = {
            str(observation.get("representation") or "").strip()
            for observation in xg_observations
            if str(observation.get("representation") or "").strip()
        }

        if len(representations) != 1:
            raise ValueError(
                "Expected one governed expected-goals representation "
                f"for season {season}; found {sorted(representations)}"
            )

        metrics.append(
            LeagueRankingMetric(
                key="expected_goals_per_match",
                label="Expected goals",
                unit="xG / match",
                higher_is_better=True,
                representation=next(iter(representations)),
                ranking_policy=str(analysis["ranking_policy"]),
                percentile_policy=str(analysis["percentile_policy"]),
                entries=[
                    LeagueRankingEntry(**entry)
                    for entry in sorted(
                        xg_entries,
                        key=_ranking_order,
                    )
                ],
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
