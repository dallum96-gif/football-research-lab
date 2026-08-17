from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import altair as alt

from frl_analytical import ResearchResult


FRL_BG = "#f5f1e8"
FRL_SURFACE = "#fffdf8"
FRL_BORDER = "#d9d4c8"
FRL_GRID = "#dfdbd1"
FRL_TEXT = "#171714"
FRL_MUTED = "#68645c"
FRL_ACCENT = "#e85d3f"
FRL_SECONDARY = "#9aaa42"


def _canonical_chart_datetime(value: Any) -> Any:
    """Convert timezone-aware datetimes to UTC for Altair compatibility."""
    if isinstance(value, datetime) and value.tzinfo is not None:
        return value.astimezone(timezone.utc)
    return value


def _normalise_result(value: Any) -> str:
    if value is None:
        return "Unplayed"
    mapping = {"W": "Win", "D": "Draw", "L": "Loss", "UNPLAYED": "Unplayed"}
    return mapping.get(str(value).upper(), str(value).title())


def team_goals_trend(result: ResearchResult) -> alt.Chart:
    """Build an FRL-styled team goals-for/goals-against trend."""
    if result.query_type != "team_fixtures":
        raise ValueError("team_goals_trend requires a team_fixtures ResearchResult")

    required = {"kickoff_time", "fixture_id", "opponent", "goals_for", "goals_against", "result"}
    missing = required.difference(result.columns)
    if missing:
        raise ValueError(f"ResearchResult is missing visualisation fields: {sorted(missing)}")

    values: list[dict[str, Any]] = []
    for row in result.rows:
        if row.get("goals_for") is None or row.get("goals_against") is None:
            continue
        kickoff = _canonical_chart_datetime(row["kickoff_time"])
        outcome = _normalise_result(row.get("result"))
        common = {
            "kickoff_time": kickoff,
            "fixture_id": row["fixture_id"],
            "opponent": row["opponent"],
            "result": outcome,
        }
        values.append({**common, "metric": "Goals for", "value": int(row["goals_for"])})
        values.append({**common, "metric": "Goals against", "value": int(row["goals_against"])})

    if not values:
        raise ValueError("ResearchResult contains no completed fixtures for visualisation")

    base = alt.Chart(alt.Data(values=values)).encode(
        x=alt.X(
            "kickoff_time:T",
            title=None,
            axis=alt.Axis(
                format="%d %b",
                labelColor=FRL_MUTED,
                titleColor=FRL_MUTED,
                domainColor=FRL_BORDER,
                tickColor=FRL_BORDER,
                labelFontSize=11,
                titleFontSize=11,
                labelPadding=7,
            ),
        ),
        y=alt.Y(
            "value:Q",
            title=None,
            scale=alt.Scale(nice=True, zero=True),
            axis=alt.Axis(
                labelColor=FRL_MUTED,
                titleColor=FRL_MUTED,
                domainColor=FRL_BORDER,
                tickColor=FRL_BORDER,
                gridColor=FRL_GRID,
                gridOpacity=0.7,
                labelFontSize=11,
                labelPadding=7,
            ),
        ),
        color=alt.Color(
            "metric:N",
            title=None,
            scale=alt.Scale(
                domain=["Goals for", "Goals against"],
                range=[FRL_ACCENT, FRL_SECONDARY],
            ),
            legend=alt.Legend(
                orient="top-left",
                labelColor=FRL_MUTED,
                labelFontSize=11,
                symbolSize=70,
                padding=0,
                offset=0,
            ),
        ),
        tooltip=[
            alt.Tooltip("kickoff_time:T", title="Date", format="%d %b %Y"),
            alt.Tooltip("opponent:N", title="Opponent"),
            alt.Tooltip("result:N", title="Result"),
            alt.Tooltip("metric:N", title="Metric"),
            alt.Tooltip("value:Q", title="Goals"),
            alt.Tooltip("fixture_id:Q", title="Fixture"),
        ],
    )

    line = base.mark_line(strokeWidth=2.3)
    points = base.mark_point(filled=True, size=44, strokeWidth=1.2)

    return (
        (line + points)
        .properties(
            height=285,
            background=FRL_SURFACE,
            padding={"left": 4, "right": 8, "top": 8, "bottom": 4},
        )
        .configure_view(stroke=FRL_BORDER, strokeWidth=1)
        .configure_axis(labelFont="Arial", titleFont="Arial")
        .configure_legend(labelFont="Arial", titleFont="Arial")
    )
