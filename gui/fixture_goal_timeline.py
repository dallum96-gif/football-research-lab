from __future__ import annotations

import streamlit as st


def render_fixture_goal_timeline(goal_events: dict | None) -> None:
    if not isinstance(goal_events, dict) or not goal_events.get("available"):
        return

    home = list(goal_events.get("home", []))
    away = list(goal_events.get("away", []))
    events = [(event, "home") for event in home] + [(event, "away") for event in away]

    if not events:
        return

    events.sort(key=lambda item: (str(item[0].get("minute", "")), str(item[0].get("source_event_id", ""))))

    st.markdown(
        "<div style='margin-top:1.15rem;color:var(--frl-accent);font-size:.60rem;"
        "font-weight:820;letter-spacing:.14em;text-transform:uppercase;'>Match timeline</div>",
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        for index, (event, side) in enumerate(events):
            minute = str(event.get("minute", "")).strip()
            player = str(event.get("player", "")).strip()
            team = str(event.get("team", "")).strip()
            align = "flex-end" if side == "home" else "flex-start"
            text_align = "right" if side == "home" else "left"

            st.markdown(
                f"<div style='display:flex;justify-content:center;align-items:center;gap:.65rem;"
                f"padding:.34rem 0;'>"
                f"<div style='width:18%;text-align:right;color:var(--frl-muted-soft);"
                f"font-size:.66rem;font-weight:800;'>{minute}'</div>"
                f"<div style='width:12px;height:12px;border-radius:50%;"
                f"background:var(--frl-accent);flex:0 0 auto;'></div>"
                f"<div style='width:18%;text-align:left;color:var(--frl-text);font-size:.78rem;"
                f"font-weight:820;'>{player}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

            if index < len(events) - 1:
                st.markdown(
                    "<div style='width:1px;height:10px;background:var(--frl-border);"
                    "margin:0 auto;'></div>",
                    unsafe_allow_html=True,
                )
