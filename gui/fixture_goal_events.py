"""Compact goal-timeline presentation for fixture detail pages."""

from __future__ import annotations

from html import escape
from typing import Iterable

import streamlit as st


def _first(row: dict, keys: Iterable[str]):
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return value
    return None


def _minute(row: dict):
    raw = _first(row, ("minute", "eventMinute", "goalMinute", "time", "incidentTime"))
    if raw in (None, ""):
        return None
    text = str(raw).strip()
    for suffix in ("+0", "'"):
        if text.endswith(suffix):
            text = text[: -len(suffix)]
    return text


def _player(row: dict):
    return _first(row, ("playerName", "player_name", "player", "name", "scorer"))


def _team(row: dict):
    return _first(row, ("teamName", "team_name", "team"))


def _event_type(row: dict):
    raw = _first(row, ("eventType", "event_type", "type", "incidentType", "incident_type"))
    return str(raw).strip().casefold() if raw is not None else ""


def extract_goals(rows: Iterable[dict] | None, home: str, away: str):
    goals = []
    for row in rows or ():
        event_type = _event_type(row)
        player = _player(row)
        if not player:
            continue

        goal_like = (
            "goal" in event_type
            or str(row.get("isGoal", "")).casefold() == "true"
            or str(row.get("incidentClass", "")).casefold() == "goal"
        )
        if not goal_like:
            continue

        team = _team(row)
        goals.append(
            {
                "player": str(player),
                "team": str(team) if team not in (None, "") else None,
                "minute": _minute(row),
                "own_goal": "own" in event_type or str(row.get("ownGoal", "")).casefold() == "true",
            }
        )

    def sort_key(item):
        minute = item["minute"]
        try:
            return (0, float(str(minute).split("+")[0]))
        except (TypeError, ValueError):
            return (1, 9999)

    return sorted(goals, key=sort_key)


def render_goal_timeline(rows: Iterable[dict] | None, home: str, away: str) -> None:
    goals = extract_goals(rows, home, away)
    if not goals:
        return

    st.markdown(
        "<div style='margin-top:.85rem;color:var(--frl-muted-soft);font-size:.56rem;"
        "font-weight:820;letter-spacing:.12em;text-transform:uppercase;'>Goal timeline</div>",
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        for index, goal in enumerate(goals):
            team = goal["team"]
            side = "home" if team == home else "away" if team == away else None
            justify = "flex-start" if side == "home" else "flex-end" if side == "away" else "center"
            colour = "var(--frl-secondary)" if side == "home" else "var(--frl-accent)" if side == "away" else "var(--frl-text)"
            minute = f"{escape(str(goal['minute']))}'" if goal["minute"] not in (None, "") else ""
            marker = " · OG" if goal["own_goal"] else ""

            st.markdown(
                f"<div style='display:flex;align-items:center;gap:.55rem;justify-content:{justify};padding:.28rem 0;'>"
                f"<span style='min-width:2.2rem;color:var(--frl-muted-soft);font-size:.68rem;font-weight:820;'>{minute}</span>"
                f"<span style='color:var(--frl-text);font-size:.73rem;font-weight:760;'>{escape(goal['player'])}</span>"
                f"<span style='color:{colour};font-size:.58rem;font-weight:820;letter-spacing:.08em;text-transform:uppercase;'>{escape(team or '')}{escape(marker)}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
            if index < len(goals) - 1:
                st.markdown("<div style='height:1px;background:var(--frl-border);'></div>", unsafe_allow_html=True)
