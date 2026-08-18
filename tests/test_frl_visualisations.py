from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import altair as alt

from frl_analytical import ResearchResult
from frl_team_visualisations import team_performance_trajectory, team_season_ppg_comparison, team_season_trend
from frl_visualisations import team_goals_trend


def _result() -> ResearchResult:
    columns = [
        "kickoff_time",
        "fixture_id",
        "opponent",
        "goals_for",
        "goals_against",
        "result",
    ]
    return ResearchResult(
        query_type="team_fixtures",
        parameters={"season": "2025-26", "team": "Arsenal", "limit": 10},
        columns=columns,
        rows=[
            {"kickoff_time": datetime(2025, 8, 17, tzinfo=timezone.utc), "fixture_id": 1, "opponent": "Manchester United", "goals_for": 1, "goals_against": 0, "result": "win"},
            {"kickoff_time": datetime(2025, 8, 23, tzinfo=timezone.utc), "fixture_id": 2, "opponent": "Leeds United", "goals_for": 2, "goals_against": 1, "result": "win"},
        ],
        population={"season": "2025-26", "rows_returned": 2},
        provenance={"fixture_source": "fixture-test"},
        temporal_context={"season": "2025-26"},
    )


def _team_season_result() -> ResearchResult:
    columns = [
        "season",
        "points_per_match",
        "played",
        "complete",
        "wins",
        "draws",
        "losses",
        "goals_for_per_match",
        "goals_against_per_match",
    ]
    return ResearchResult(
        query_type="team_season_comparison",
        parameters={"team": "Arsenal", "seasons": ["2023-24", "2024-25", "2025-26"]},
        columns=columns,
        rows=[
            {"season": "2023-24", "points_per_match": 2.26, "played": 38, "complete": True, "wins": 28, "draws": 5, "losses": 5, "goals_for_per_match": 2.37, "goals_against_per_match": 0.84},
            {"season": "2024-25", "points_per_match": 1.97, "played": 38, "complete": True, "wins": 20, "draws": 15, "losses": 3, "goals_for_per_match": 1.84, "goals_against_per_match": 0.84},
            {"season": "2025-26", "points_per_match": 2.08, "played": 38, "complete": True, "wins": 24, "draws": 7, "losses": 7, "goals_for_per_match": 1.95, "goals_against_per_match": 0.76},
        ],
        population={"requested_seasons": ["2023-24", "2024-25", "2025-26"]},
        provenance={"fixture_source": "fixture-test"},
        temporal_context={"seasons": ["2023-24", "2024-25", "2025-26"]},
    )


def test_team_goals_trend_returns_altair_chart() -> None:
    chart = team_goals_trend(_result())
    assert isinstance(chart, alt.Chart)
    mark = chart.to_dict()["mark"]
    assert mark["type"] == "line"
    assert mark["point"] == {"filled": True, "size": 44, "strokeWidth": 1.2}


def test_team_goals_trend_normalises_dst_timezone_for_altair() -> None:
    result = _result()
    rows = [dict(row) for row in result.rows]
    rows[0]["kickoff_time"] = datetime(2025, 8, 17, 16, 30, tzinfo=ZoneInfo("Europe/London"))
    result = ResearchResult(
        query_type=result.query_type,
        parameters=result.parameters,
        columns=result.columns,
        rows=rows,
        population=result.population,
        provenance=result.provenance,
        temporal_context=result.temporal_context,
    )
    chart = team_goals_trend(result)
    value = chart.to_dict()["data"]["values"][0]["kickoff_time"]
    assert value["year"] == 2025
    assert value["month"] == 8
    assert value["date"] == 17
    assert value["hours"] == 15
    assert value["minutes"] == 30


def test_team_goals_trend_does_not_accept_wrong_result_type() -> None:
    result = _result()
    wrong = ResearchResult(
        query_type="league_table",
        parameters=result.parameters,
        columns=result.columns,
        rows=result.rows,
        population=result.population,
        provenance=result.provenance,
        temporal_context=result.temporal_context,
    )
    try:
        team_goals_trend(wrong)
    except ValueError as exc:
        assert "team_fixtures" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_team_performance_trajectory_supports_three_metrics() -> None:
    columns = [
        "kickoff_time",
        "fixture_id",
        "opponent",
        "result",
        "points",
        "goals_for",
        "goals_against",
        "rolling_ppg",
        "rolling_goals_for_per_match",
        "rolling_goals_against_per_match",
    ]
    result = ResearchResult(
        query_type="team_performance_profile",
        parameters={"season": "2025-26", "team": "Arsenal", "rolling_window": 5},
        columns=columns,
        rows=[
            {"kickoff_time": datetime(2025, 8, 17, tzinfo=timezone.utc), "fixture_id": 1, "opponent": "Manchester United", "result": "W", "points": 3, "goals_for": 1, "goals_against": 0, "rolling_ppg": 3.0, "rolling_goals_for_per_match": 1.0, "rolling_goals_against_per_match": 0.0},
            {"kickoff_time": datetime(2025, 8, 23, tzinfo=timezone.utc), "fixture_id": 2, "opponent": "Leeds United", "result": "W", "points": 3, "goals_for": 2, "goals_against": 1, "rolling_ppg": 3.0, "rolling_goals_for_per_match": 1.5, "rolling_goals_against_per_match": 0.5},
        ],
        population={},
        provenance={},
        temporal_context={},
    )
    for metric in ("form", "attack", "defence"):
        chart = team_performance_trajectory(result, metric=metric)
        assert isinstance(chart, alt.LayerChart)


def test_team_season_trend_returns_clean_layered_chart() -> None:
    chart = team_season_trend(_team_season_result(), metric="ppg")
    assert isinstance(chart, alt.LayerChart)
    spec = chart.to_dict()
    assert len(spec["layer"]) == 4
    assert spec["layer"][0]["mark"]["type"] == "area"
    assert spec["layer"][1]["mark"]["type"] == "rule"
    assert spec["layer"][2]["mark"]["type"] == "line"
    assert spec["layer"][3]["mark"]["type"] == "point"
    assert "background" in spec
    assert "background" not in spec["layer"][0]


def test_team_season_ppg_comparison_remains_compatible() -> None:
    chart = team_season_ppg_comparison(_team_season_result())
    assert isinstance(chart, alt.LayerChart)
