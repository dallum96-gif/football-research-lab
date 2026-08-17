from datetime import datetime, timezone

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
    assert chart.to_dict()["mark"] == {"point": True, "type": "line"}


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
