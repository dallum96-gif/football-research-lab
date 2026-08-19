from __future__ import annotations

import csv
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
GOALS = ROOT / "data" / "fixture_goal_events.csv"


def load_fixture_goals(season: str, fixture_id: str):
    if not GOALS.is_file():
        return []

    with GOALS.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    events = [
        row for row in rows
        if row.get("season") == str(season)
        and str(row.get("fixture_id", "")) == str(fixture_id)
        and row.get("identity_status") == "VERIFIED"
    ]
    events.sort(
        key=lambda row: (
            float(row.get("source_event_seconds") or 0),
            str(row.get("source_event_id") or ""),
        )
    )
    return events


def render_fixture_goal_block(season: str, fixture_id: str, home_team: str, away_team: str):
    events = load_fixture_goals(season, fixture_id)
    if not events:
        return

    home_events = [
        row for row in events
        if str(row.get("source_scorer_team") or "").replace("_", " ").strip()
        == str(row.get("source_fixture_home") or "").replace("_", " ").strip()
    ]
    away_events = [
        row for row in events
        if str(row.get("source_scorer_team") or "").replace("_", " ").strip()
        == str(row.get("source_fixture_away") or "").replace("_", " ").strip()
    ]

    home_by_id = {str(row.get("source_event_id")): row for row in home_events}
    away_by_id = {str(row.get("source_event_id")): row for row in away_events}

    st.markdown(
        "<div style='margin-top:.72rem;color:var(--frl-muted-soft);"
        "font-size:.56rem;font-weight:820;letter-spacing:.14em;"
        "text-transform:uppercase;text-align:center;'>Goals</div>",
        unsafe_allow_html=True,
    )

    rows_html = []
    for row in events:
        event_id = str(row.get("source_event_id") or "")
        scorer_team = str(row.get("source_scorer_team") or "").replace("_", " ").strip()
        player = str(row.get("source_scorer_name") or "").strip()
        minute = str(row.get("source_event_time_label") or "").strip()
        is_home = scorer_team == str(row.get("source_fixture_home") or "").replace("_", " ").strip()
        is_away = scorer_team == str(row.get("source_fixture_away") or "").replace("_", " ").strip()

        left = player if is_home else ""
        right = player if is_away else ""

        rows_html.append(
            "<div style='display:grid;grid-template-columns:minmax(0,1fr) 62px "
            "minmax(0,1fr);align-items:center;min-height:28px;'>"
            f"<div style='text-align:right;padding-right:.8rem;color:var(--frl-text);"
            f"font-size:.72rem;font-weight:760;line-height:1.15;'>{left}</div>"
            f"<div style='position:relative;text-align:center;color:var(--frl-muted-soft);"
            f"font-size:.64rem;font-weight:820;line-height:1.15;'>{minute}'"
            "<span style='position:absolute;left:50%;top:19px;bottom:-14px;"
            "width:1px;background:var(--frl-border);transform:translateX(-50%);'></span>"
            "</div>"
            f"<div style='text-align:left;padding-left:.8rem;color:var(--frl-text);"
            f"font-size:.72rem;font-weight:760;line-height:1.15;'>{right}</div>"
            "</div>"
        )

    if rows_html:
        rows_html[-1] = rows_html[-1].replace(
            "<span style='position:absolute;left:50%;top:19px;bottom:-14px;"
            "width:1px;background:var(--frl-border);transform:translateX(-50%);'></span>",
            "<span style='position:absolute;left:50%;top:19px;bottom:-4px;"
            "width:1px;background:transparent;transform:translateX(-50%);'></span>",
        )

    st.markdown("".join(rows_html), unsafe_allow_html=True)
