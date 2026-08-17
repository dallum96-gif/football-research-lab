from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import altair as alt

from frl_analytical import ResearchResult
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
            {
                "kickoff_time": datetime(2025, 8, 17, tzinfo=timezone.utc),
                "fixture_id": 1,
                "opponent": "Manchester United",
                "goals_for": 1,
                "goals_against": 0,
                "result": "win",
            },
            {
                "kickoff_time": datetime(2025, 8, 23, tzinfo=timezone.utc),
                "fixture_id": 2,
                "opponent": "Leeds United",
                "goals_for": 2,
                "goals_against": 1,
                "result": "win",
            },
        ],
        population={"season": "2025-26", "rows_returned": 2},
        provenance={"fixture_source": "fixture-test"},
        temporal_context={"season": "2025-26"},
    )


def test_team_goals_trend_returns_altair_chart() -> None:
    chart = team_goals_trend(_result())
    assert isinstance(chart, alt.Chart)
    mark = chart.to_dict()["mark"]
    assert mark["type"] == "line"
    assert mark["point"] is True


def test_team_goals_trend_normalises_dst_timezone_for_altair() -> None:
    result = _result()
    rows = [dict(row) for row in result.rows]
    rows[0]["kickoff_time"] = datetime(
        2025, 8, 17, 16, 30,
        tzinfo=ZoneInfo("Europe/London"),
    )
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
