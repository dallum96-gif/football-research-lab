from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache

import query_api
import team_research_stats
from expected_metric_artifact import team_expected_metric_observation
from expected_metric_routing import (
    DIRECT_TEAM_MATCH,
    EXPECTED_GOALS,
    NO_GOVERNED_SEASON_ROUTE,
    PLAYER_MATCH_DERIVED_TEAM_MATCH,
    single_season_route,
)


CANONICAL_FIXTURE_RESULT = "CANONICAL_FIXTURE_RESULT"
COMPETITION_RANK = "COMPETITION_RANK"
RANK_POSITION_PERCENTILE = "RANK_POSITION_PERCENTILE"
ANALYSIS_VERSION = "team-analysis-kernel-v1"


@dataclass(frozen=True)
class MetricDefinition:
    key: str
    label: str
    unit: str
    higher_is_better: bool
    coverage_key: str
    representation: str


OVERVIEW_METRICS = (
    MetricDefinition(
        key="points_per_match",
        label="Points per match",
        unit="PPG",
        higher_is_better=True,
        coverage_key="result_coverage",
        representation=CANONICAL_FIXTURE_RESULT,
    ),
    MetricDefinition(
        key="goals_for_per_match",
        label="Goals per match",
        unit="goals",
        higher_is_better=True,
        coverage_key="goals_for",
        representation=CANONICAL_FIXTURE_RESULT,
    ),
    MetricDefinition(
        key="goals_against_per_match",
        label="Goals against",
        unit="goals",
        higher_is_better=False,
        coverage_key="goals_against",
        representation=CANONICAL_FIXTURE_RESULT,
    ),
    MetricDefinition(
        key="Shots_per_match",
        label="Shots per match",
        unit="shots",
        higher_is_better=True,
        coverage_key="Shots",
        representation=DIRECT_TEAM_MATCH,
    ),
    MetricDefinition(
        key="Shots on target_per_match",
        label="Shots on target",
        unit="shots",
        higher_is_better=True,
        coverage_key="Shots on target",
        representation=DIRECT_TEAM_MATCH,
    ),
    MetricDefinition(
        key="Possession_per_match",
        label="Possession",
        unit="%",
        higher_is_better=True,
        coverage_key="Possession",
        representation=DIRECT_TEAM_MATCH,
    ),
)

METRIC_DEFINITIONS = {metric.key: metric for metric in OVERVIEW_METRICS}


def _coverage(stats: dict, definition: MetricDefinition) -> dict:
    if definition.coverage_key == "result_coverage":
        source = stats.get("result_coverage", {})
        return {
            "eligible_matches": int(source.get("eligible_matches", stats.get("matches", 0))),
            "observed_matches": int(source.get("observed_matches", 0)),
            "missing_matches": int(source.get("missing_matches", 0)),
            "coverage_status": source.get("coverage_status", "UNAVAILABLE"),
        }

    source = stats.get("metric_coverage", {}).get(definition.coverage_key, {})
    return {
        "eligible_matches": int(source.get("eligible_matches", stats.get("matches", 0))),
        "observed_matches": int(source.get("observed_matches", 0)),
        "missing_matches": int(source.get("missing_matches", 0)),
        "coverage_status": source.get("coverage_status", "UNAVAILABLE"),
    }


def rank_metric_entries(entries: list[dict], higher_is_better: bool) -> list[dict]:
    """Apply the existing Team Stats competition-rank/percentile behaviour centrally."""
    available = [entry for entry in entries if entry.get("value") is not None]
    out_of = len(available)

    for entry in entries:
        value = entry.get("value")
        if value is None:
            entry["rank"] = None
            entry["out_of"] = out_of
            entry["percentile"] = None
            continue

        value = float(value)
        better = sum(
            1
            for candidate in available
            if (
                float(candidate["value"]) > value
                if higher_is_better
                else float(candidate["value"]) < value
            )
        )
        rank = better + 1
        percentile = (
            100.0
            if out_of == 1
            else round(100.0 * (out_of - rank) / (out_of - 1), 1)
        )
        entry["rank"] = rank
        entry["out_of"] = out_of
        entry["percentile"] = percentile

    return entries


def _team_population(season: str) -> list[dict]:
    table = query_api.league_table(season)
    population = []
    for row in table.get("teams", []):
        code = str(row.get("persistent_team_code") or "").strip()
        if not code:
            continue
        population.append(
            {
                "persistent_team_code": code,
                "display_name": str(row.get("team") or "").strip(),
                "local_team_id": str(row.get("team_id") or "").strip(),
            }
        )
    return population


def _player_derived_xg(season: str, team_code: str, stats: dict) -> dict:
    rows = team_research_stats.team_match_stats(season, team_code)
    values: list[float] = []
    missing_fixture_ids: list[str] = []

    for row in rows:
        fixture_id = str(row.get("fixture_id") or "")
        side = "home" if row.get("home") else "away"
        observation = team_expected_metric_observation(
            season,
            fixture_id,
            side,
            EXPECTED_GOALS,
        )
        if observation.get("status") == "AVAILABLE" and observation.get("value") is not None:
            values.append(float(observation["value"]))
        else:
            missing_fixture_ids.append(fixture_id)

    eligible = len(rows)
    observed = len(values)
    total = sum(values) if values else None
    per_observed_match = total / observed if total is not None and observed else None
    coverage_status = (
        "COMPLETE"
        if observed == eligible and eligible
        else "PARTIAL"
        if observed
        else "UNAVAILABLE"
    )

    goals_for = stats.get("goals_for")
    xg_overperformance = (
        float(goals_for) - float(total)
        if total is not None
        and goals_for is not None
        and observed == eligible
        else None
    )

    return {
        "value": per_observed_match,
        "observed_total": total,
        "eligible_matches": eligible,
        "observed_matches": observed,
        "missing_matches": eligible - observed,
        "missing_fixture_ids": missing_fixture_ids,
        "coverage_status": coverage_status,
        "coverage_complete": observed == eligible and bool(eligible),
        "representation": PLAYER_MATCH_DERIVED_TEAM_MATCH,
        "construction_version": "FRL_PLAYER_DERIVED_EXPECTED_METRICS_V1",
        "xg_overperformance": xg_overperformance,
    }


def _direct_xg(season: str, stats: dict) -> dict:
    coverage = stats.get("metric_coverage", {}).get("Expected goals", {})
    eligible = int(coverage.get("eligible_matches", stats.get("matches", 0)))
    observed = int(coverage.get("observed_matches", 0))
    value = stats.get("Expected goals_per_match")
    total = stats.get("Expected goals")

    return {
        "value": float(value) if value is not None else None,
        "observed_total": float(total) if total is not None else None,
        "eligible_matches": eligible,
        "observed_matches": observed,
        "missing_matches": int(coverage.get("missing_matches", eligible - observed)),
        "missing_fixture_ids": [],
        "coverage_status": coverage.get("coverage_status", "UNAVAILABLE"),
        "coverage_complete": bool(coverage.get("coverage_complete", False)),
        "representation": DIRECT_TEAM_MATCH,
        "construction_version": "fixture-match-stats-v1",
        "xg_overperformance": (
            float(stats["xg_overperformance"])
            if stats.get("xg_overperformance") is not None
            else None
        ),
    }


def expected_goals_observation(season: str, team_code: str, stats: dict | None = None) -> dict:
    stats = stats or team_research_stats.team_season_stats(season, team_code)
    route = single_season_route(EXPECTED_GOALS, season)

    base = {
        "route_purpose": route.purpose,
        "route_coverage_status": route.coverage_status,
        "representation_mixing_allowed": route.representation_mixing_allowed,
    }

    if route.representation == PLAYER_MATCH_DERIVED_TEAM_MATCH:
        return {**_player_derived_xg(season, team_code, stats), **base}
    if route.representation == DIRECT_TEAM_MATCH:
        return {**_direct_xg(season, stats), **base}
    if route.representation == NO_GOVERNED_SEASON_ROUTE:
        return {
            **base,
            "value": None,
            "observed_total": None,
            "eligible_matches": int(stats.get("matches", 0)),
            "observed_matches": 0,
            "missing_matches": int(stats.get("matches", 0)),
            "missing_fixture_ids": [],
            "coverage_status": "UNAVAILABLE",
            "coverage_complete": False,
            "representation": NO_GOVERNED_SEASON_ROUTE,
            "construction_version": None,
            "xg_overperformance": None,
        }
    raise ValueError(f"Unsupported governed xG representation: {route.representation}")


@lru_cache(maxsize=16)
def season_overview_analysis(season: str) -> dict:
    """Build the one governed season result consumed by Team View and Rankings."""
    population = _team_population(season)
    team_stats: dict[str, dict] = {}

    for team in population:
        code = team["persistent_team_code"]
        stats = team_research_stats.team_season_stats(season, code)
        if stats.get("status") == "AVAILABLE":
            team_stats[code] = stats

    metrics: dict[str, dict] = {}
    for definition in OVERVIEW_METRICS:
        entries: list[dict] = []
        for team in population:
            code = team["persistent_team_code"]
            stats = team_stats.get(code)
            if stats is None:
                continue
            raw_value = stats.get(definition.key)
            entries.append(
                {
                    **team,
                    "value": float(raw_value) if raw_value is not None else None,
                    "coverage": _coverage(stats, definition),
                    "representation": definition.representation,
                }
            )

        rank_metric_entries(entries, definition.higher_is_better)
        metrics[definition.key] = {
            "definition": asdict(definition),
            "ranking_policy": COMPETITION_RANK,
            "percentile_policy": RANK_POSITION_PERCENTILE,
            "entries": entries,
        }

    xg = {
        team["persistent_team_code"]: {
            **team,
            **expected_goals_observation(
                season,
                team["persistent_team_code"],
                team_stats.get(team["persistent_team_code"]),
            ),
        }
        for team in population
        if team["persistent_team_code"] in team_stats
    }

    return {
        "analysis_version": ANALYSIS_VERSION,
        "season": season,
        "population_size": len(population),
        "ranking_policy": COMPETITION_RANK,
        "percentile_policy": RANK_POSITION_PERCENTILE,
        "metrics": metrics,
        "expected_goals": xg,
    }


def team_overview_analysis(season: str, team_code: str) -> dict | None:
    analysis = season_overview_analysis(season)
    selected_metrics = []

    for definition in OVERVIEW_METRICS:
        metric = analysis["metrics"][definition.key]
        entry = next(
            (
                item
                for item in metric["entries"]
                if item["persistent_team_code"] == str(team_code)
            ),
            None,
        )
        if entry is not None:
            selected_metrics.append(
                {
                    **metric["definition"],
                    **entry,
                    "ranking_policy": metric["ranking_policy"],
                    "percentile_policy": metric["percentile_policy"],
                }
            )

    xg = analysis["expected_goals"].get(str(team_code))
    if not selected_metrics and xg is None:
        return None

    identity = (
        selected_metrics[0]
        if selected_metrics
        else xg
    )
    return {
        "analysis_version": analysis["analysis_version"],
        "season": season,
        "persistent_team_code": str(team_code),
        "display_name": identity["display_name"],
        "local_team_id": identity["local_team_id"],
        "metrics": selected_metrics,
        "expected_goals": xg,
    }


__all__ = [
    "ANALYSIS_VERSION",
    "CANONICAL_FIXTURE_RESULT",
    "COMPETITION_RANK",
    "METRIC_DEFINITIONS",
    "OVERVIEW_METRICS",
    "RANK_POSITION_PERCENTILE",
    "MetricDefinition",
    "expected_goals_observation",
    "rank_metric_entries",
    "season_overview_analysis",
    "team_overview_analysis",
]
