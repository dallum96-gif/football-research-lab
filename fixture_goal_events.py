"""Fixture goal-event retrieval from the established SofaScore source match ID.

This adapter deliberately sits outside the canonical fixture/query contracts.
The canonical fixture identity remains season + fixture_id; the existing
match-statistics layer supplies the SofaScore source_match_id used here.

Goal events are retrospective presentation evidence. They are not used by
predictive research features in this module.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any

import requests
import streamlit as st

BASE_URL = "https://api.sofascore.com/api/v1/event"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept": "application/json",
}


def _number(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


@lru_cache(maxsize=512)
def fixture_goal_events(source_match_id: str | int | None) -> dict[str, Any]:
    """Return normalised goal events for an external SofaScore event ID.

    Missing/invalid IDs, upstream failures and malformed payloads are exposed
    as UNAVAILABLE rather than crashing the fixture detail page.
    """
    if source_match_id in (None, ""):
        return {
            "status": "UNAVAILABLE",
            "source": "SofaScore /event/{eventId}/incidents",
            "source_match_id": None,
            "goals": [],
        }

    event_id = str(source_match_id).strip()
    if not event_id.isdigit():
        return {
            "status": "UNAVAILABLE",
            "source": "SofaScore /event/{eventId}/incidents",
            "source_match_id": event_id,
            "goals": [],
        }

    url = f"{BASE_URL}/{event_id}/incidents"

    try:
        response = requests.get(url, headers=HEADERS, timeout=8)
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError):
        return {
            "status": "UNAVAILABLE",
            "source": url,
            "source_match_id": event_id,
            "goals": [],
        }

    goals: list[dict[str, Any]] = []
    for incident in payload.get("incidents", []):
        if incident.get("incidentType") != "goal":
            continue

        player = incident.get("player") or {}
        goals.append(
            {
                "minute": _number(incident.get("time")),
                "added_time": _number(incident.get("addedTime")),
                "player": incident.get("playerName") or player.get("name"),
                "player_id": player.get("id"),
                "is_home": bool(incident.get("isHome")),
                "incident_class": incident.get("incidentClass") or "regular",
                "own_goal": incident.get("incidentClass") == "ownGoal",
            }
        )

    goals.sort(key=lambda item: ((item["minute"] is None), item["minute"] or 0, item["added_time"] or 0))

    return {
        "status": "AVAILABLE",
        "source": url,
        "source_match_id": event_id,
        "goals": goals,
    }


def _minute_label(goal: dict[str, Any]) -> str:
    minute = goal.get("minute")
    added = goal.get("added_time")
    if minute is None:
        return "–'"
    return f"{minute}+{added}'" if added else f"{minute}'"


def render_fixture_goal_timeline(goal_data: dict[str, Any], home: str, away: str) -> None:
    """Render a compact scorer timeline beneath the fixture scoreline."""
    if goal_data.get("status") != "AVAILABLE":
        return

    goals = goal_data.get("goals", [])

    st.markdown(
        "<div style='margin-top:.95rem;margin-bottom:.15rem;color:var(--frl-muted-soft);"
        "font-size:.56rem;font-weight:820;letter-spacing:.13em;text-transform:uppercase;"
        "text-align:center;'>Goal timeline</div>",
        unsafe_allow_html=True,
    )

    if not goals:
        st.markdown(
            "<div style='text-align:center;color:var(--frl-muted-soft);font-size:.66rem;"
            "padding:.25rem 0 .5rem;'>No goals</div>",
            unsafe_allow_html=True,
        )
        return

    rows: list[str] = []
    for goal in goals:
        player = goal.get("player") or "Unknown scorer"
        minute = _minute_label(goal)
        suffix = " · OG" if goal.get("own_goal") else ""
        label = f"{player}{suffix}"

        if goal.get("is_home"):
            rows.append(
                "<div style='display:grid;grid-template-columns:1fr 4.2rem 1fr;align-items:center;min-height:1.65rem;'>"
                f"<div style='text-align:right;color:var(--frl-text);font-size:.69rem;font-weight:740;padding-right:.55rem;'>{label}</div>"
                f"<div style='text-align:center;color:var(--frl-muted-soft);font-size:.59rem;font-weight:820;letter-spacing:.05em;'>{minute}</div>"
                "<div></div>"
                "</div>"
            )
        else:
            rows.append(
                "<div style='display:grid;grid-template-columns:1fr 4.2rem 1fr;align-items:center;min-height:1.65rem;'>"
                "<div></div>"
                f"<div style='text-align:center;color:var(--frl-muted-soft);font-size:.59rem;font-weight:820;letter-spacing:.05em;'>{minute}</div>"
                f"<div style='text-align:left;color:var(--frl-text);font-size:.69rem;font-weight:740;padding-left:.55rem;'>{label}</div>"
                "</div>"
            )

    st.markdown(
        "<div style='max-width:760px;margin:0 auto .45rem;'>"
        + "".join(rows)
        + "</div>",
        unsafe_allow_html=True,
    )
