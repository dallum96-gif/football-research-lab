import pytest
from fastapi import HTTPException

import team_analysis_kernel
from api.team_stats_rankings import get_team_stats_league_rankings
from expected_metric_routing import DIRECT_TEAM_MATCH


def _metric_map(response):
    return {metric.key: metric for metric in response.metrics}


def test_rankings_api_projects_the_shared_season_kernel_without_recalculation():
    season = "2024-25"
    kernel = team_analysis_kernel.season_overview_analysis(season)
    response = get_team_stats_league_rankings(season)

    assert response.analysis_version == kernel["analysis_version"]
    assert response.population_size == kernel["population_size"] == 20
    assert response.ranking_policy == kernel["ranking_policy"]
    assert response.percentile_policy == kernel["percentile_policy"]
    assert len(response.metrics) == len(kernel["metrics"]) == 7
    assert "Corners_per_match" in _metric_map(response)

    for key, api_metric in _metric_map(response).items():
        kernel_metric = kernel["metrics"][key]
        kernel_rows = {
            row["persistent_team_code"]: row
            for row in kernel_metric["entries"]
        }
        assert len(api_metric.entries) == len(kernel_rows) == 20

        for row in api_metric.entries:
            expected = kernel_rows[row.persistent_team_code]
            assert row.value == expected["value"]
            assert row.rank == expected["rank"]
            assert row.out_of == expected["out_of"]
            assert row.percentile == expected["percentile"]
            assert row.coverage == expected["coverage"]


def test_rankings_and_team_view_are_the_same_analysis_result_for_same_metric():
    season = "2024-25"
    rankings = get_team_stats_league_rankings(season)
    metric = _metric_map(rankings)["points_per_match"]
    sample = metric.entries[4]
    team = team_analysis_kernel.team_overview_analysis(
        season,
        sample.persistent_team_code,
    )

    assert team is not None
    team_metric = next(
        row for row in team["metrics"] if row["key"] == "points_per_match"
    )
    assert sample.value == team_metric["value"]
    assert sample.rank == team_metric["rank"]
    assert sample.out_of == team_metric["out_of"]
    assert sample.percentile == team_metric["percentile"]


def test_corners_are_rankings_only_and_preserve_kernel_coverage():
    season = "2025-26"
    rankings = get_team_stats_league_rankings(season)
    corners = _metric_map(rankings)["Corners_per_match"]

    assert corners.label == "Corners per match"
    assert corners.unit == "corners"
    assert corners.representation == DIRECT_TEAM_MATCH
    assert any(row.coverage["missing_matches"] > 0 for row in corners.entries)

    sample = next(row for row in corners.entries if row.value is not None)
    team = team_analysis_kernel.team_overview_analysis(
        season,
        sample.persistent_team_code,
    )
    assert team is not None
    assert "Corners_per_match" not in {row["key"] for row in team["metrics"]}


def test_rankings_keep_competition_ties_and_are_ordered_by_kernel_rank():
    response = get_team_stats_league_rankings("2024-25")

    for metric in response.metrics:
        ranks = [row.rank for row in metric.entries if row.rank is not None]
        assert ranks == sorted(ranks)

        by_value: dict[float, list[int]] = {}
        for row in metric.entries:
            if row.value is not None and row.rank is not None:
                by_value.setdefault(row.value, []).append(row.rank)

        for tied_ranks in by_value.values():
            assert len(set(tied_ranks)) == 1


def test_rankings_fail_closed_for_unsupported_season():
    with pytest.raises(HTTPException) as exc_info:
        get_team_stats_league_rankings("2099-00")

    assert exc_info.value.status_code == 400
