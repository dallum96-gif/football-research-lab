from __future__ import annotations

import csv
from functools import lru_cache
import re
from pathlib import Path
from typing import Any

import requests


EVENT_FILE = Path(__file__).resolve().parent / "data" / "fixture_goal_events.csv"
PULSE_BASE = "https://footballapi.pulselive.com/football"
PULSE_HEADERS = {
    "Origin": "https://www.premierleague.com",
    "Referer": "https://www.premierleague.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/142 Safari/537.36",
    "Accept": "application/json",
}


@lru_cache(maxsize=1)
def _rows() -> tuple[dict[str, str], ...]:
    if not EVENT_FILE.is_file():
        return tuple()
    with EVENT_FILE.open("r", encoding="utf-8-sig", newline="") as handle:
        return tuple(csv.DictReader(handle))


def _minute_label(seconds: str | int | None, native_label: str | None) -> str:
    label = (native_label or "").strip().replace("'00", "'").replace(" ", "")
    if label:
        return label if label.endswith("'") else f"{label}'"
    try:
        value = int(float(str(seconds)))
    except (TypeError, ValueError):
        return "–"
    return f"{value // 60 + 1}'"


def _parse_scorer_text(text: str) -> tuple[str | None, str | None]:
    match = re.search(r"\.\s+(.+?)\s+\(([^)]+)\)", text or "")
    if not match:
        return None, None
    return match.group(1).strip(), match.group(2).strip()


def _is_goal_event(event: dict[str, Any]) -> bool:
    return str(event.get("type") or "").strip().casefold() in {"goal", "penalty goal"}


def _own_goal(text: str, event: dict[str, Any]) -> bool:
    return bool(
        event.get("ownGoal") is True
        or event.get("isOwnGoal") is True
        or "own goal" in text.casefold()
    )


@lru_cache(maxsize=32)
def _competition_season_id(season: str) -> str | None:
    try:
        response = requests.get(
            f"{PULSE_BASE}/competitions/1/compseasons",
            params={"page": 0, "pageSize": 100},
            headers=PULSE_HEADERS,
            timeout=20,
        )
        response.raise_for_status()
        rows = response.json().get("content", [])
    except (requests.RequestException, ValueError):
        return None
    target = season.replace("-", "/")
    for row in rows:
        if str(row.get("label") or "").strip() == target:
            value = row.get("id")
            return str(int(float(value))) if value not in (None, "") else None
    return None


@lru_cache(maxsize=64)
def _pulse_fixture(season: str, source_match_id: str | int) -> dict[str, Any] | None:
    source = str(source_match_id).strip()
    if not source.isdigit():
        return None
    comp_season = _competition_season_id(season)
    if comp_season is None:
        return None
    try:
        response = requests.get(
            f"{PULSE_BASE}/fixtures",
            params={
                "comps": 1,
                "compSeasons": comp_season,
                "page": 0,
                "pageSize": 1000,
                "sort": "asc",
                "altIds": "true",
            },
            headers=PULSE_HEADERS,
            timeout=20,
        )
        response.raise_for_status()
        rows = response.json().get("content", [])
    except (requests.RequestException, ValueError):
        return None

    target = f"g{source}"
    matches = []
    for fixture in rows:
        alt_ids = fixture.get("altIds") or {}
        if str(alt_ids.get("opta") or "").strip() == target:
            matches.append(fixture)
    return matches[0] if len(matches) == 1 else None


@lru_cache(maxsize=64)
def _verified_player_index(season: str) -> dict[str, tuple[str, str]]:
    try:
        import player_identity_crosswalk
        import player_research
        report = player_identity_crosswalk.summarize()
    except Exception:
        return {}

    if report.get("review_rows"):
        return {}

    names: dict[str, str] = {}
    try:
        for row in player_research._load_season_rows(season):
            element = str(row.get("element") or "").strip()
            if element:
                names[element] = player_research.display_player_name(row)
    except Exception:
        pass

    index: dict[str, tuple[str, str]] = {}
    for row in report.get("confirmed", []):
        if row.get("season") != season:
            continue
        source_player_id = str(row.get("source_player_id") or "").strip()
        element = str(row.get("element") or "").strip()
        team_code = str(row.get("team_code") or "").split(";")[0].strip()
        if source_player_id and element and source_player_id not in index:
            index[source_player_id] = (names.get(element, row.get("name_norm", "")), team_code)
    return index


def _team_names(pulse_fixture: dict[str, Any]) -> tuple[str, str]:
    teams = pulse_fixture.get("teams") or []
    if len(teams) < 2:
        return "", ""
    home = teams[0].get("team", {}) if isinstance(teams[0], dict) else {}
    away = teams[1].get("team", {}) if isinstance(teams[1], dict) else {}
    return str(home.get("name") or home.get("shortName") or "").strip(), str(away.get("name") or away.get("shortName") or "").strip()


@lru_cache(maxsize=64)
def _live_goal_events(season: str, source_match_id: str | int) -> tuple[dict[str, Any], ...]:
    pulse_fixture = _pulse_fixture(season, source_match_id)
    if pulse_fixture is None:
        return tuple()
    pulse_id = pulse_fixture.get("id")
    if pulse_id in (None, ""):
        return tuple()

    try:
        response = requests.get(
            f"{PULSE_BASE}/fixtures/{int(float(pulse_id))}/textstream/EN",
            params={"pageSize": 1000, "sort": "desc"},
            headers=PULSE_HEADERS,
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError):
        return tuple()

    home_name, away_name = _team_names(pulse_fixture)
    events = ((payload.get("events") or {}).get("content") or [])
    player_index = _verified_player_index(season)
    goals: list[dict[str, Any]] = []

    for event in events:
        if not isinstance(event, dict) or not _is_goal_event(event):
            continue

        text = str(event.get("text") or "").strip()
        scorer_name, scorer_team = _parse_scorer_text(text)
        player_ids = event.get("playerIds") or []
        scorer_id = str(player_ids[0]).strip() if player_ids else ""
        candidate = player_index.get(scorer_id)
        if candidate is None:
            continue

        canonical_name, _team_code = candidate
        if not canonical_name:
            continue

        scoring_side = ""
        if scorer_team:
            if scorer_team.casefold() == home_name.casefold():
                scoring_side = "home"
            elif scorer_team.casefold() == away_name.casefold():
                scoring_side = "away"

        own_goal = _own_goal(text, event)
        if own_goal and scoring_side:
            scoring_side = "away" if scoring_side == "home" else "home"

        time_block = event.get("time") or {}
        seconds_raw = time_block.get("secs")
        seconds = int(float(seconds_raw)) if seconds_raw not in (None, "") else None

        goals.append(
            {
                "minute": _minute_label(seconds, str(time_block.get("label") or "")),
                "seconds": seconds,
                "player_name": canonical_name,
                "side": scoring_side,
                "own_goal": own_goal,
                "source_event_id": str(event.get("id") or ""),
                "source_scorer_id": scorer_id,
            }
        )

    goals.sort(key=lambda row: (row["seconds"] is None, row["seconds"] or 0, row["source_event_id"]))
    return tuple(goals)


@lru_cache(maxsize=128)
def fixture_goal_events(
    season: str,
    fixture_id: str | int,
    source_match_id: str | int | None = None,
) -> tuple[dict[str, Any], ...]:
    key = (str(season), str(fixture_id))
    output: list[dict[str, Any]] = []

    for row in _rows():
        if (row.get("season"), str(row.get("fixture_id"))) != key:
            continue
        if row.get("identity_status") != "VERIFIED":
            continue
        output.append(
            {
                "minute": _minute_label(row.get("source_event_seconds"), row.get("source_event_time_label")),
                "seconds": int(float(row["source_event_seconds"])) if row.get("source_event_seconds") else None,
                "player_name": row.get("player_name", "").strip(),
                "side": row.get("side", "").strip(),
                "own_goal": row.get("own_goal", "").casefold() == "true",
                "source_event_id": row.get("source_event_id", "").strip(),
            }
        )

    if output:
        output.sort(key=lambda row: (row["seconds"] is None, row["seconds"] or 0, row["source_event_id"]))
        return tuple(output)

    if source_match_id not in (None, ""):
        return _live_goal_events(str(season), str(source_match_id))
    return tuple()


def render_fixture_goal_timeline(goal_rows: tuple[dict[str, Any], ...], home: str, away: str) -> None:
    import html
    import streamlit as st

    if not goal_rows:
        return

    st.markdown(
        "<div style='margin-top:.72rem;color:var(--frl-muted-soft);font-size:.56rem;"
        "font-weight:820;letter-spacing:.13em;text-transform:uppercase;text-align:center;'>Goals</div>",
        unsafe_allow_html=True,
    )

    rows: list[str] = []
    for goal in goal_rows:
        name = html.escape(goal["player_name"])
        if goal["own_goal"]:
            name = f"{name} · OG"
        minute = html.escape(goal["minute"])
        home_name = name if goal["side"] == "home" else ""
        away_name = name if goal["side"] == "away" else ""
        rows.append(
            "<div style='display:grid;grid-template-columns:minmax(0,1fr) 3.2rem minmax(0,1fr);"
            "align-items:center;min-height:1.78rem;'>"
            f"<div style='text-align:right;padding:.12rem .7rem;color:var(--frl-text);font-size:.72rem;font-weight:760;'>{home_name}</div>"
            f"<div style='text-align:center;color:var(--frl-muted);font-size:.66rem;font-weight:820;'>{minute}</div>"
            f"<div style='text-align:left;padding:.12rem .7rem;color:var(--frl-text);font-size:.72rem;font-weight:760;'>{away_name}</div>"
            "</div>"
        )

    st.markdown(
        "<div style='margin:0 auto .18rem;max-width:720px;'>" + "".join(rows) + "</div>",
        unsafe_allow_html=True,
    )
