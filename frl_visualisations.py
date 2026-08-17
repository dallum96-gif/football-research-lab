from __future__ import annotations

from typing import Any

import altair as alt

from frl_analytical import ResearchResult


def team_goals_trend(result: ResearchResult) -> alt.Chart:
    """Build a team goals-for/goals-against trend from a validated result."""
    if result.query_type != "team_fixtures":
        raise ValueError("team_goals_trend requires a team_fixtures ResearchResult")

    required = {"kickoff_time", "fixture_id", "opponent", "goals_for", "goals_against", "result"}
    missing = required.difference(result.columns)
    if missing:
        raise ValueError(f"ResearchResult is missing visualisation fields: {sorted(missing)}")

    rows: list[dict[str, Any]] = []
    for row in result.rows:
        if row.get("goals_for") is None or row.get("goals_against") is None:
            continue
        rows.append(
            {
                "kickoff_time": row["kickoff_time"],
                "fixture_id": row["fixture_id"],
                "opponent": row["opponent"],
                "goals_for": row["goals_for"],
                "goals_against": row["goals_against"],
                "result": row["result"],
            }
        )

    if not rows:
        raise ValueError("ResearchResult contains no completed fixtures for visualisation")

    values: list[dict[str, Any]] = []
    for row in rows:
        values.extend(
            [
                {
                    "kickoff_time": row["kickoff_time"],
                    "fixture_id": row["fixture_id"],
                    "opponent": row["opponent"],
                    "result": row["result"],
                    "metric": "Goals for",
                    "value": row["goals_for"],
                },
                {
                    "kickoff_time": row["kickoff_time"],
                    "fixture_id": row["fixture_id"],
                    "opponent": row["opponent"],
                    "result": row["result"],
                    "metric": "Goals against",
                    "value": row["goals_against"],
                },
            ]
        )

    chart = (
        alt.Chart(alt.Data(values=values))
        .mark_line(point=True, strokeWidth=2.5)
        .encode(
            x=alt.X("kickoff_time:T", title="Kick-off"),
            y=alt.Y("value:Q", title="Goals"),
            detail="metric:N",
            color=alt.Color("metric:N", title=None),
            shape=alt.Shape(
                "result:N",
                title="Result",
                scale=alt.Scale(domain=["win", "draw", "loss", "unplayed"]),
            ),
            tooltip=[
                alt.Tooltip("kickoff_time:T", title="Kick-off"),
                alt.Tooltip("opponent:N", title="Opponent"),
                alt.Tooltip("result:N", title="Result"),
                alt.Tooltip("metric:N", title="Metric"),
                alt.Tooltip("value:Q", title="Goals"),
                alt.Tooltip("fixture_id:Q", title="Fixture"),
            ],
        )
        .properties(
            title=f"{result.parameters.get('team', 'Team')} — goals trend",
        )
    )
    return chart
