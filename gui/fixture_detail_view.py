"""Fixture landing-page presentation.

Uses the existing query_api.fixture_detail contract. This module owns
presentation only; it does not create a new fixture-data retrieval path.
"""

from datetime import datetime

import pandas as pd
import streamlit as st


CORE_GROUPS = [
    (
        "Attacking",
        [
            "Shots",
            "Shots on target",
            "Shots off target",
            "Blocked shots",
            "Corners",
        ],
    ),
    (
        "Possession & passing",
        [
            "Possession",
            "Passes",
            "Accurate passes",
            "Crosses",
        ],
    ),
    (
        "Defending",
        [
            "Tackles",
            "Tackles won",
            "Interceptions",
            "Interceptions won",
            "Clearances",
            "Effective clearances",
            "Offsides",
        ],
    ),
    (
        "Discipline",
        [
            "Fouls won",
            "Fouls conceded",
            "Yellow cards",
            "Red cards",
        ],
    ),
]


def _date_label(value):
    try:
        return datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        ).strftime("%d %b %Y")
    except (TypeError, ValueError):
        return str(value)[:10]


def _value(values, label):
    value = values.get(label)
    return "—" if value is None else value


def render_fixture_detail_view(detail, on_back=None):
    """Render a polished fixture landing page from an existing detail payload."""
    fixture = detail["fixture"]
    stats = detail["stats"]

    home = fixture["home_team_name"]
    away = fixture["away_team_name"]
    home_score = fixture["home_score"] or "—"
    away_score = fixture["away_score"] or "—"

    st.markdown(
        """
        <style>
        .frl-match-kicker { color:var(--frl-accent); font-size:.62rem; font-weight:800; letter-spacing:.16em; text-transform:uppercase; text-align:center; }
        .frl-match-meta { color:var(--frl-muted-soft); font-size:.68rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; text-align:center; margin-top:.35rem; }
        .frl-match-card { margin:1rem auto 1.4rem; padding:1.35rem 1.2rem 1.15rem; max-width:900px; border:1px solid var(--frl-border); border-radius:16px; background:var(--frl-surface); }
        .frl-match-teams { display:grid; grid-template-columns:1fr auto 1fr; gap:1.1rem; align-items:center; }
        .frl-match-team { color:var(--frl-text); font-size:clamp(1.2rem,2vw,1.8rem); font-weight:820; line-height:1; text-align:center; letter-spacing:-.035em; }
        .frl-match-score { color:var(--frl-text); font-size:clamp(2.4rem,5vw,4rem); font-weight:900; line-height:1; text-align:center; letter-spacing:-.06em; }
        .frl-match-dash { color:var(--frl-accent); }
        .frl-match-note { margin-top:.8rem; color:var(--frl-muted); font-size:.72rem; text-align:center; }
        .frl-correction { margin:.9rem 0; padding:.7rem .85rem; border-left:3px solid var(--frl-accent); background:var(--frl-surface-raised); border-radius:0 10px 10px 0; color:var(--frl-muted); font-size:.72rem; }
        .frl-stat-heading { margin-top:1.35rem; margin-bottom:.45rem; color:var(--frl-negative); font-size:.62rem; font-weight:820; letter-spacing:.14em; text-transform:uppercase; }
        .frl-stat-card { overflow:hidden; border:1px solid var(--frl-border); border-radius:13px; background:var(--frl-surface); }
        .frl-stat-card table { width:100%; border-collapse:collapse; }
        .frl-stat-card th { padding:.5rem .65rem; color:var(--frl-muted-soft); font-size:.58rem; font-weight:780; letter-spacing:.09em; text-transform:uppercase; text-align:right; }
        .frl-stat-card th:first-child, .frl-stat-card td:first-child { text-align:left; }
        .frl-stat-card td { padding:.56rem .65rem; border-top:1px solid var(--frl-border); color:var(--frl-text); font-size:.7rem; font-weight:680; text-align:right; }
        .frl-stat-card td:first-child { color:var(--frl-muted); font-weight:700; }
        .frl-provenance { color:var(--frl-muted); font-size:.7rem; line-height:1.5; }
        @media (max-width:700px) { .frl-match-teams { grid-template-columns:1fr; gap:.55rem; } .frl-match-score { order:-1; } }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if on_back is not None and st.button("← Back to Fixtures", key="fixture_detail_back", type="tertiary"):
        on_back()
        st.rerun()

    st.markdown("<div class='frl-match-kicker'>Fixture landing page</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='frl-match-meta'>{fixture['season']} · GW {fixture['gameweek']} · {_date_label(fixture['kickoff_time'])}</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='frl-match-card'><div class='frl-match-teams'>"
        f"<div class='frl-match-team'>{home}</div>"
        f"<div class='frl-match-score'>{home_score}<span class='frl-match-dash'>–</span>{away_score}</div>"
        f"<div class='frl-match-team'>{away}</div>"
        "</div></div>",
        unsafe_allow_html=True,
    )

    if fixture.get("data_corrected") == "true":
        st.markdown(
            "<div class='frl-correction'><strong>Verified historical correction.</strong> "
            "The analytical view uses the corrected kickoff and result while preserving the original scheduled record.</div>",
            unsafe_allow_html=True,
        )

    if stats.get("status") != "AVAILABLE":
        st.warning("Historical match statistics are not available for this fixture.")
        return

    home_core = stats["home"]["core"]
    away_core = stats["away"]["core"]

    for title, labels in CORE_GROUPS:
        rows = []
        for label in labels:
            if label in home_core or label in away_core:
                rows.append(
                    {
                        "Statistic": label,
                        home: _value(home_core, label),
                        away: _value(away_core, label),
                    }
                )

        if not rows:
            continue

        st.markdown(f"<div class='frl-stat-heading'>{title}</div>", unsafe_allow_html=True)
        st.markdown("<div class='frl-stat-card'>", unsafe_allow_html=True)
        st.dataframe(
            pd.DataFrame(rows),
            width="stretch",
            hide_index=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    optional_rows = []
    home_optional = stats.get("home", {}).get("optional", {})
    away_optional = stats.get("away", {}).get("optional", {})

    for label in home_optional:
        optional_rows.append(
            {
                "Statistic": label,
                home: _value(home_optional, label),
                away: _value(away_optional, label),
            }
        )

    if optional_rows:
        with st.expander("Additional statistics", expanded=False):
            st.dataframe(
                pd.DataFrame(optional_rows),
                width="stretch",
                hide_index=True,
            )

    with st.expander("Data provenance", expanded=False):
        provenance = detail.get("provenance", {})
        st.markdown(
            "<div class='frl-provenance'>"
            f"<strong>Canonical fixture ID:</strong> {fixture['fixture_id']}<br>"
            f"<strong>PL source match ID:</strong> {stats.get('source_match_id', '—')}<br>"
            f"<strong>Canonical fixture source:</strong> {provenance.get('canonical_source', '—')}<br>"
            f"<strong>Identity source:</strong> {provenance.get('identity_source', '—')}<br>"
            f"<strong>Correction source:</strong> {provenance.get('correction_source', '—')}"
            "</div>",
            unsafe_allow_html=True,
        )
