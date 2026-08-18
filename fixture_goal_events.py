"""Historical goal-event adapter for the FRL fixture landing page.

Source: Premier League / PulseLive fixture data, matching the source family
used by the upstream historical archive. Presentation/research evidence only.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any
import re

import requests
import streamlit as st

BASE_URL = "https://footballapi.pulselive.com/football"
HEADERS = {
    "Origin": "https://www.premierleague.com",
    "Referer": "https://www.premierleague.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept": "application/json",
}


def _minute(raw_time: Any, raw_seconds: Any) -> tuple[int | None, int | None]:
    if raw_seconds not in (None, ""):
        try:
            seconds = int(float(raw_seconds))
            return seconds // 60, seconds % 60
        except (TypeError, ValueError):
            pass

    if raw_time in (None, ""):
        return None, None

    text = str(raw_time).strip()
    match = re.search(r"(\d+)\s*'", text)
    if match:
        return int(match.group(1)), None

    match = re.match(r"^(\d+)(?::(\d+))?$", text)
    if match:
        return int(match.group(1)), int(match.group(2) or 0)

    return None, None


def _name(player: Any) -> str | None:
    if isinstance(player, str):
        return player.strip() or None
    if not isinstance(player, dict):
        return None
    name = player.get("name")
    if isinstance(name, dict):
        return name.get("display") or name.get("full") or name.get("first")
    return name or player.get("displayName") or player.get("fullName")


def _iter_events(payload: Any):
    if isinstance(payload, dict):
        for key in ("events", "goals", "fixtureEvents", "fixture_events"):
            value = payload.get(key)
            if isinstance(value, list):
                yield from value
        for value in payload.values():
            if isinstance(value, (dict, list)):
                yield from _iter_events(value)
    elif isinstance(payload, list):
        for value in payload:
            yield from _iter_events(value)


def _is_goal(event: dict[str, Any]) -> bool:
    kind = str(
        event.get("type")
        or event.get("eventType")
        or event.get("event_type")
        or event.get("incidentType")
        or event.get("description")
        or ""
    ).lower()
    return "goal" in kind or "penalty goal" in kind or event.get("isGoal") is True


def _is_own_goal(event: dict[str, Any]) -> bool:
    if event.get("ownGoal") is True or event.get("isOwnGoal") is True:
        return True
    kind = str(
        event.get("type")
        or event.get("eventType")
        or event.get("event_type")
        or event.get("incidentClass")
        or ""
    ).lower()
    return "own" in kind and "goal" in kind


def _event_name(event: dict[str, Any]) -> str | None:
    for key in ("scorer", "player", "playerName", "scorerName"):
        value = event.get(key)
        name = _name(value)
        if name:
            return name
    return None


def _event_side(event: dict[str, Any], home_team_id: str | None, away_team_id: str | None) -> str | None:
    if isinstance(event.get("isHome"), bool):
        return "home" if event["isHome"] else "away"

    for key in ("homeAway", "side", "teamSide"):
        value = str(event.get(key) or "").lower()
        if value in {"home", "h"}:
            return "home"
        if value in {"away", "a"}:
            return "away"

    team = event.get("team")
    team_id = event.get("teamId")
    if isinstance(team, dict):
        team_id = team.get("id") or team.get("teamId")

    if team_id is not None:
        if home_team_id is not None and str(team_id) == str(home_team_id):
            return "home"
        if away_team_id is not None and str(team_id) == str(away_team_id):
            return "away"

    return None


def _normalise_event(event: dict[str, Any], home_team_id: str | None, away_team_id: str | None) -> dict[str, Any] | None:
    if not _is_goal(event):
        return None

    minute, seconds_remainder = _minute(
        event.get("time") or event.get("clock") or event.get("minute"),
        event.get("seconds"),
    )
    name = _event_name(event)
    if minute is None or not name:
        return None

    return {
        "minute": minute,
        "seconds_remainder": seconds_remainder,
        "player": name,
        "side": _event_side(event, home_team_id, away_team_id),
        "own_goal": _is_own_goal(event),
        "goal_type": event.get("type") or event.get("eventType") or event.get("incidentType"),
    }


@lru_cache(maxsize=512)
def fixture_goal_events(
    source_match_id: str | int | None,
    home_team_id: str | int | None = None,
    away_team_id: str | int | None = None,
) -> dict[str, Any]:
    """Fetch and normalise goal events for a PulseLive fixture ID."""
    if source_match_id in (None, ""):
        return {"status": "UNAVAILABLE", "goals": [], "source": None}

    match_id = str(source_match_id).strip()
    if not match_id.isdigit():
        return {"status": "UNAVAILABLE", "goals": [], "source": None}

    url = f"{BASE_URL}/fixtures/{match_id}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError):
        return {"status": "UNAVAILABLE", "goals": [], "source": url}

    goals: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()
    for raw in _iter_events(payload):
        if not isinstance(raw, dict):
            continue
        event = _normalise_event(
            raw,
            str(home_team_id) if home_team_id is not None else None,
            str(away_team_id) if away_team_id is not None else None,
        )
        if event is None:
            continue
        key = (event["minute"], event["player"], event["side"], event["own_goal"])
        if key in seen:
            continue
        seen.add(key)
        goals.append(event)

    goals.sort(key=lambda item: (item["minute"], item.get("seconds_remainder") or 0))
    return {"status": "AVAILABLE", "goals": goals, "source": url}


def render_fixture_goal_timeline(goal_data: dict[str, Any], home: str, away: str) -> None:
    """Render a compact scorer strip beneath the fixture scoreline."""
    if goal_data.get("status") != "AVAILABLE" or not goal_data.get("goals"):
        return

    st.markdown(
        "<div style='margin-top:.75rem;color:var(--frl-muted-soft);font-size:.56rem;"
        "font-weight:820;letter-spacing:.13em;text-transform:uppercase;text-align:center;'>Goals</div>",
        unsafe_allow_html=True,
    )

    rows = []
    for goal in goal_data["goals"]:
        minute = f"{goal['minute']}'"
        name = goal["player"] + (" · OG" if goal.get("own_goal") else "")
        side = goal.get("side")
        home_name = name if side == "home" else ""
        away_name = name if side == "away" else ""

        rows.append(
            "<div style='display:grid;grid-template-columns:minmax(0,1fr) 3.2rem minmax(0,1fr);"
            "align-items:center;min-height:1.75rem;border-bottom:1px solid var(--frl-border);'>"
            f"<div style='text-align:right;padding:.12rem .7rem;color:var(--frl-text);font-size:.72rem;font-weight:760;'>{home_name}</div>"
            f"<div style='text-align:center;color:var(--frl-muted);font-size:.66rem;font-weight:820;'>{minute}</div>"
            f"<div style='text-align:left;padding:.12rem .7rem;color:var(--frl-text);font-size:.72rem;font-weight:760;'>{away_name}</div>"
            "</div>"
        )

    st.markdown(
        "<div style='margin:0 auto .15rem;max-width:720px;'>" + "".join(rows) + "</div>",
        unsafe_allow_html=True,
    )
