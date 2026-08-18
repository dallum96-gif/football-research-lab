from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import Any


EVENT_FILE = Path(__file__).resolve().parent / "data" / "fixture_goal_events.csv"


@lru_cache(maxsize=1)
def _rows() -> tuple[dict[str, str], ...]:
    if not EVENT_FILE.is_file():
        return tuple()
    with EVENT_FILE.open("r", encoding="utf-8-sig", newline="") as handle:
        return tuple(csv.DictReader(handle))


def _minute_label(seconds: str | int | None, native_label: str | None) -> str:
    label = (native_label or "").strip()
    if label:
        label = label.replace("'00", "'").replace(" ", "")
        return label if label.endswith("'") else f"{label}'"

    try:
        value = int(float(str(seconds)))
    except (TypeError, ValueError):
        return "–"
    return f"{value // 60 + 1}'"


@lru_cache(maxsize=128)
def fixture_goal_events(season: str, fixture_id: str | int) -> tuple[dict[str, Any], ...]:
    key = (str(season), str(fixture_id))
    output: list[dict[str, Any]] = []

    for row in _rows():
        if (row.get("season"), str(row.get("fixture_id"))) != key:
            continue
        if row.get("identity_status") != "VERIFIED":
            continue
        output.append(
            {
                "minute": _minute_label(
                    row.get("source_event_seconds"),
                    row.get("source_event_time_label"),
                ),
                "seconds": int(float(row["source_event_seconds"])) if row.get("source_event_seconds") else None,
                "player_name": row.get("player_name", "").strip(),
                "side": row.get("side", "").strip(),
                "own_goal": row.get("own_goal", "").casefold() == "true",
                "source_event_id": row.get("source_event_id", "").strip(),
            }
        )

    output.sort(key=lambda row: (row["seconds"] is None, row["seconds"] or 0, row["source_event_id"]))
    return tuple(output)


def render_fixture_goal_timeline(
    goal_rows: tuple[dict[str, Any], ...],
    home: str,
    away: str,
) -> None:
    """Render the compact scorer timeline beneath the fixture scoreline."""
    import streamlit as st

    if not goal_rows:
        return

    st.markdown(
        "<div style='margin-top:.72rem;color:var(--frl-muted-soft);"
        "font-size:.56rem;font-weight:820;letter-spacing:.13em;"
        "text-transform:uppercase;text-align:center;'>Goals</div>",
        unsafe_allow_html=True,
    )

    rows: list[str] = []
    for goal in goal_rows:
        name = goal["player_name"]
        if not name:
            continue
        if goal["own_goal"]:
            name = f"{name} · OG"

        home_name = name if goal["side"] == "home" else ""
        away_name = name if goal["side"] == "away" else ""

        rows.append(
            "<div style='display:grid;grid-template-columns:minmax(0,1fr) 3.2rem minmax(0,1fr);"
            "align-items:center;min-height:1.78rem;'>"
            f"<div style='text-align:right;padding:.12rem .7rem;color:var(--frl-text);font-size:.72rem;font-weight:760;'>{home_name}</div>"
            f"<div style='text-align:center;color:var(--frl-muted);font-size:.66rem;font-weight:820;'>{goal['minute']}</div>"
            f"<div style='text-align:left;padding:.12rem .7rem;color:var(--frl-text);font-size:.72rem;font-weight:760;'>{away_name}</div>"
            "</div>"
        )

    if rows:
        st.markdown(
            "<div style='margin:0 auto .18rem;max-width:720px;'>" + "".join(rows) + "</div>",
            unsafe_allow_html=True,
        )
