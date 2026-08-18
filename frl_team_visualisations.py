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


def _finish(chart, *, height: int = 300) -> alt.Chart:
    return (
        chart.properties(
            height=height,
            background=FRL_SURFACE,
            padding={"left": 4, "right": 12, "top": 8, "bottom": 4},
        )
        .configure_view(stroke=FRL_BORDER, strokeWidth=1)
        .configure_axis(
            labelColor=FRL_MUTED,
            domainColor=FRL_BORDER,
            tickColor=FRL_BORDER,
            gridColor=FRL_GRID,
            gridOpacity=0.55,
            labelFont="Arial",
            titleFont="Arial",
            labelFontSize=11,
        )
    )


def _profile_values(result: ResearchResult, metric: str) -> list[dict[str, Any]]:
    if metric not in {"form", "attack", "defence"}:
        raise ValueError("metric must be form, attack or defence")

    ordered = sorted(
        result.rows,
        key=lambda row: (_utc(row["kickoff_time"]), int(row["fixture_id"])),
    )
    total_points = 0
    total_gf = 0
    total_ga = 0
    values: list[dict[str, Any]] = []

    rolling_field = {
        "form": "rolling_ppg",
        "attack": "rolling_goals_for_per_match",
        "defence": "rolling_goals_against_per_match",
    }[metric]

    for index, row in enumerate(ordered, start=1):
        total_points += int(row.get("points", 0) or 0)
        total_gf += int(row.get("goals_for", 0) or 0)
        total_ga += int(row.get("goals_against", 0) or 0)
        cumulative = {
            "form": total_points / index,
            "attack": total_gf / index,
            "defence": total_ga / index,
        }[metric]
        rolling = row.get(rolling_field)
        values.append(
            {
                "kickoff_time": _utc(row["kickoff_time"]),
                "sequence": index,
                "fixture_id": row["fixture_id"],
                "opponent": row.get("opponent"),
                "result": row.get("result"),
                "value": rolling,
                "baseline": round(cumulative, 3),
                "label": {"form": "Rolling PPG", "attack": "Goals scored / match", "defence": "Goals conceded / match"}[metric],
            }
        )
    return values


def team_performance_trajectory(result: ResearchResult, metric: str = "form") -> alt.Chart:
    """Show a selected current-season trend against its cumulative baseline."""
    if result.query_type != "team_performance_profile":
        raise ValueError("team_performance_trajectory requires a team_performance_profile ResearchResult")

    required = {
        "kickoff_time",
        "fixture_id",
        "opponent",
        "result",
        "points",
        "rolling_ppg",
        "rolling_goals_for_per_match",
        "rolling_goals_against_per_match",
    }
    missing = required.difference(result.columns)
    if missing:
        raise ValueError(f"ResearchResult is missing visualisation fields: {sorted(missing)}")

    values = [row for row in _profile_values(result, metric) if row["value"] is not None]
    if not values:
        raise ValueError("ResearchResult contains no completed fixtures for visualisation")

    chart = alt.Chart(alt.Data(values=values)).encode(
        x=alt.X(
            "kickoff_time:T",
            title=None,
            axis=alt.Axis(format="%b", labelPadding=7, tickCount=8),
        ),
        y=alt.Y(
            "value:Q",
            title=None,
            scale=alt.Scale(zero=False, nice=True),
        ),
        tooltip=[
            alt.Tooltip("kickoff_time:T", title="Date", format="%d %b %Y"),
            alt.Tooltip("opponent:N", title="Opponent"),
            alt.Tooltip("result:N", title="Result"),
            alt.Tooltip("label:N", title="Trend"),
            alt.Tooltip("value:Q", title="Value", format=".2f"),
            alt.Tooltip("baseline:Q", title="Season baseline", format=".2f"),
            alt.Tooltip("sequence:Q", title="Match"),
        ],
    )

    baseline = chart.mark_line(color=FRL_MUTED, strokeWidth=1.25, strokeDash=[5, 5]).encode(
        y=alt.Y("baseline:Q")
    )
    rolling = chart.mark_area(color=FRL_ACCENT, opacity=0.07).encode(
        y=alt.Y("value:Q"),
        y2=alt.Y2("baseline:Q"),
    )
    line = chart.mark_line(color=FRL_ACCENT, strokeWidth=2.6, point=True)
    points = chart.mark_point(color=FRL_ACCENT, filled=True, size=44, stroke=FRL_SURFACE, strokeWidth=1.5)

    return _finish(alt.layer(rolling, baseline, line, points))


def _season_metric(row: dict[str, Any], metric: str) -> float | None:
    return {
        "ppg": row.get("points_per_match"),
        "attack": row.get("goals_for_per_match"),
        "defence": row.get("goals_against_per_match"),
    }[metric]


def team_season_trend(result: ResearchResult, metric: str = "ppg") -> alt.Chart:
    """Compare selected seasons as a clean historical performance arc."""
    if result.query_type != "team_season_comparison":
        raise ValueError("team_season_trend requires a team_season_comparison ResearchResult")
    if metric not in {"ppg", "attack", "defence"}:
        raise ValueError("metric must be ppg, attack or defence")

    labels = {
        "ppg": "Points per match",
        "attack": "Goals scored / match",
        "defence": "Goals conceded / match",
    }
    values = []
    for row in result.rows:
        value = _season_metric(row, metric)
        if value is not None:
            values.append(
                {
                    "season": row["season"],
                    "value": value,
                    "wins": row.get("wins", 0),
                    "draws": row.get("draws", 0),
                    "losses": row.get("losses", 0),
                    "played": row.get("played", 0),
                    "gf": row.get("goals_for_per_match"),
                    "ga": row.get("goals_against_per_match"),
                    "complete": "Complete" if row.get("complete") else "Incomplete",
                }
            )

    if not values:
        raise ValueError("ResearchResult contains no comparable season values")
    values.sort(key=lambda row: row["season"])
    mean_value = sum(row["value"] for row in values) / len(values)
    for row in values:
        row["delta"] = row["value"] - mean_value

    base = alt.Chart(alt.Data(values=values)).encode(
        x=alt.X("season:N", sort=None, title=None, axis=alt.Axis(labelAngle=0, labelPadding=8)),
        y=alt.Y("value:Q", title=None, scale=alt.Scale(zero=False, nice=True)),
        tooltip=[
            alt.Tooltip("season:N", title="Season"),
            alt.Tooltip("value:Q", title=labels[metric], format=".2f"),
            alt.Tooltip("delta:Q", title="Vs selected-period mean", format="+.2f"),
            alt.Tooltip("wins:Q", title="Wins"),
            alt.Tooltip("draws:Q", title="Draws"),
            alt.Tooltip("losses:Q", title="Losses"),
            alt.Tooltip("played:Q", title="Played"),
            alt.Tooltip("gf:Q", title="GF / match", format=".2f"),
            alt.Tooltip("ga:Q", title="GA / match", format=".2f"),
            alt.Tooltip("complete:N", title="Coverage"),
        ],
    )
    area = base.mark_area(color=FRL_ACCENT, opacity=0.06)
    line = base.mark_line(color=FRL_ACCENT, strokeWidth=2.6)
    points = base.mark_point(color=FRL_ACCENT, filled=True, size=62, stroke=FRL_SURFACE, strokeWidth=1.5)
    mean_rule = (
        alt.Chart(alt.Data(values=[{"mean": mean_value}]))
        .encode(y=alt.Y("mean:Q"))
        .mark_rule(color=FRL_MUTED, strokeDash=[5, 5], strokeWidth=1.1)
    )
    return _finish(alt.layer(area, mean_rule, line, points), height=280)


def team_season_ppg_comparison(result: ResearchResult) -> alt.Chart:
    """Compatibility wrapper for the historical PPG comparison surface."""
    return team_season_trend(result, metric="ppg")
