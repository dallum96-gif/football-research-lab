from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import altair as alt

from frl_analytical import ResearchResult


FRL_SURFACE = "#fffdf8"
FRL_BORDER = "#d9d4c8"
FRL_GRID = "#dfdbd1"
FRL_TEXT = "#171714"
FRL_MUTED = "#68645c"
FRL_ACCENT = "#e85d3f"
FRL_SECONDARY = "#9aaa42"


def _utc(value: Any) -> Any:
    if isinstance(value, datetime) and value.tzinfo is not None:
        return value.astimezone(timezone.utc)
    return value


def _base_chart(data: list[dict[str, Any]]) -> alt.Chart:
    return alt.Chart(alt.Data(values=data))


def _style_chart(chart: alt.Chart, height: int = 285) -> alt.Chart:
    return (
        chart
        .configure_view(stroke=FRL_BORDER, strokeWidth=1)
        .configure_axis(
            labelColor=FRL_MUTED,
            domainColor=FRL_BORDER,
            tickColor=FRL_BORDER,
            gridColor=FRL_GRID,
            gridOpacity=0.7,
            labelFont="Arial",
            titleFont="Arial",
            labelFontSize=11,
        )
        .configure_legend(labelFont="Arial", titleFont="Arial", labelColor=FRL_MUTED)
        .properties(
            height=height,
            background=FRL_SURFACE,
            padding={"left": 4, "right": 8, "top": 8, "bottom": 4},
        )
    )


def team_performance_trajectory(result: ResearchResult) -> alt.Chart:
    """Show cumulative and rolling PPG from the same team-performance research result."""
    if result.query_type != "team_performance_profile":
        raise ValueError("team_performance_trajectory requires a team_performance_profile ResearchResult")

    required = {"kickoff_time", "fixture_id", "opponent", "result", "cumulative_ppg", "rolling_ppg"}
    missing = required.difference(result.columns)
    if missing:
        raise ValueError(f"ResearchResult is missing visualisation fields: {sorted(missing)}")

    values: list[dict[str, Any]] = []
    for row in result.rows:
        values.append(
            {
                "kickoff_time": _utc(row["kickoff_time"]),
                "fixture_id": row["fixture_id"],
                "opponent": row["opponent"],
                "result": row["result"],
                "metric": "Cumulative PPG",
                "value": row["cumulative_ppg"],
            }
        )
        if row.get("rolling_ppg") is not None:
            values.append(
                {
                    "kickoff_time": _utc(row["kickoff_time"]),
                    "fixture_id": row["fixture_id"],
                    "opponent": row["opponent"],
                    "result": row["result"],
                    "metric": "Rolling PPG",
                    "value": row["rolling_ppg"],
                }
            )

    chart = _base_chart(values).encode(
        x=alt.X(
            "kickoff_time:T",
            title=None,
            axis=alt.Axis(format="%d %b", labelPadding=7),
        ),
        y=alt.Y(
            "value:Q",
            title=None,
            scale=alt.Scale(zero=False, nice=True),
        ),
        color=alt.Color(
            "metric:N",
            title=None,
            scale=alt.Scale(
                domain=["Cumulative PPG", "Rolling PPG"],
                range=[FRL_MUTED, FRL_ACCENT],
            ),
            legend=alt.Legend(orient="top-left", symbolSize=60, padding=0),
        ),
        tooltip=[
            alt.Tooltip("kickoff_time:T", title="Date", format="%d %b %Y"),
            alt.Tooltip("opponent:N", title="Opponent"),
            alt.Tooltip("result:N", title="Result"),
            alt.Tooltip("metric:N", title="Measure"),
            alt.Tooltip("value:Q", title="PPG", format=".2f"),
            alt.Tooltip("fixture_id:Q", title="Fixture"),
        ],
    )
    return _style_chart(
        chart.mark_line(
            point=alt.OverlayMarkDef(filled=True, size=38, strokeWidth=1.0),
            strokeWidth=2.1,
        )
    )


def team_season_performance_map(result: ResearchResult) -> alt.LayerChart:
    """Map each season by attacking output and defensive concession rate.

    The chronological path shows how the team's performance profile moved between
    seasons; point size and colour encode points per match so the map separates
    *how* a team performed from the resulting league points.
    """
    if result.query_type != "team_season_comparison":
        raise ValueError("team_season_performance_map requires a team_season_comparison ResearchResult")

    required = {
        "season",
        "points_per_match",
        "played",
        "complete",
        "wins",
        "draws",
        "losses",
        "goals_for_per_match",
        "goals_against_per_match",
    }
    missing = required.difference(result.columns)
    if missing:
        raise ValueError(f"ResearchResult is missing visualisation fields: {sorted(missing)}")

    values = [
        {
            "season": row["season"],
            "ppg": row["points_per_match"],
            "played": row["played"],
            "complete": "Complete" if row.get("complete") else "Incomplete",
            "wins": row.get("wins", 0),
            "draws": row.get("draws", 0),
            "losses": row.get("losses", 0),
            "goals_for_per_match": row.get("goals_for_per_match"),
            "goals_against_per_match": row.get("goals_against_per_match"),
        }
        for row in result.rows
        if row.get("points_per_match") is not None
        and row.get("goals_for_per_match") is not None
        and row.get("goals_against_per_match") is not None
    ]
    if not values:
        raise ValueError("ResearchResult contains no comparable season performance values")

    values.sort(key=lambda row: row["season"])
    base = _base_chart(values)
    encoding = dict(
        x=alt.X(
            "goals_for_per_match:Q",
            title="Goals scored / match",
            scale=alt.Scale(zero=True, nice=True),
        ),
        y=alt.Y(
            "goals_against_per_match:Q",
            title="Goals conceded / match",
            scale=alt.Scale(zero=True, nice=True),
        ),
        tooltip=[
            alt.Tooltip("season:N", title="Season"),
            alt.Tooltip("ppg:Q", title="Points per match", format=".2f"),
            alt.Tooltip("wins:Q", title="Wins"),
            alt.Tooltip("draws:Q", title="Draws"),
            alt.Tooltip("losses:Q", title="Losses"),
            alt.Tooltip("played:Q", title="Played"),
            alt.Tooltip("goals_for_per_match:Q", title="GF / match", format=".2f"),
            alt.Tooltip("goals_against_per_match:Q", title="GA / match", format=".2f"),
            alt.Tooltip("complete:N", title="Coverage"),
        ],
    )

    line = base.encode(
        **encoding,
        order=alt.Order("season:N", sort="ascending"),
    ).mark_line(
        color=FRL_BORDER,
        strokeWidth=1.6,
    )

    points = base.encode(
        **encoding,
        size=alt.Size(
            "ppg:Q",
            title="PPG",
            scale=alt.Scale(range=[80, 520]),
            legend=None,
        ),
        color=alt.Color(
            "ppg:Q",
            title="Points / match",
            scale=alt.Scale(range=[FRL_SECONDARY, FRL_ACCENT]),
            legend=alt.Legend(format=".1f", orient="top-right", titlePadding=4),
        ),
    ).mark_point(
        filled=True,
        opacity=0.95,
        stroke=FRL_SURFACE,
        strokeWidth=2,
    )

    return _style_chart(alt.layer(line, points), height=320)


# Backwards-compatible name for callers that used the earlier PPG-specific visual.
team_season_ppg_comparison = team_season_performance_map
