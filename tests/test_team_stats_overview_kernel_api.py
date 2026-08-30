import query_api
import team_analysis_kernel
from api.frl_api import get_team_stats_overview


def _sample_team_code(season: str) -> str:
    for row in query_api.league_table(season)["teams"]:
        code = str(row.get("persistent_team_code") or "").strip()
        if code:
            return code
    raise AssertionError(f"No persistent team code found for {season}")


def test_overview_api_metrics_project_the_shared_kernel_result():
    season = "2024-25"
    code = _sample_team_code(season)
    kernel = team_analysis_kernel.team_overview_analysis(season, code)
    response = get_team_stats_overview(season, code)

    assert kernel is not None
    assert response.provenance.transformation_version == "team-stats-overview-kernel-v1"

    kernel_metrics = {metric["key"]: metric for metric in kernel["metrics"]}
    assert len(response.metrics) == len(kernel_metrics) == 6

    for metric in response.metrics:
        expected = kernel_metrics[metric.key]
        assert metric.value == round(float(expected["value"]), 3)
        assert metric.rank == expected["rank"]
        assert metric.out_of == expected["out_of"]
        assert metric.percentile == expected["percentile"]
        assert metric.higher_is_better == expected["higher_is_better"]

    xg = kernel["expected_goals"]
    assert response.expected_goals_per_match == round(float(xg["value"]), 3)
    assert response.xg_overperformance == round(float(xg["xg_overperformance"]), 3)


def test_partial_2023_24_player_xg_is_exposed_without_fake_overperformance():
    season = "2023-24"
    season_analysis = team_analysis_kernel.season_overview_analysis(season)
    partial = next(
        row
        for row in season_analysis["expected_goals"].values()
        if not row["coverage_complete"]
    )

    response = get_team_stats_overview(season, partial["persistent_team_code"])

    assert response.expected_goals_per_match is not None
    assert response.xg_overperformance is None
    assert any("Expected-goals evidence is partial" in item for item in response.limitations)


def test_pre_2022_overview_withholds_expected_goals_without_governed_route():
    season = "2021-22"
    code = _sample_team_code(season)
    response = get_team_stats_overview(season, code)

    assert response.expected_goals_per_match is None
    assert response.xg_overperformance is None
    assert any(
        "no governed season representation" in item.casefold()
        for item in response.limitations
    )
