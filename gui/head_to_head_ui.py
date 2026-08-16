"""Head-to-Head research workspace."""

import streamlit as st

import query_api


def _season_key(season):
    return int(season.split("-")[0])


def _teams_for_season(season):
    payload = query_api.league_table(season=season)
    return sorted(
        [row["team"] for row in payload.get("teams", [])],
        key=str.casefold,
    )


def render_head_to_head():
    seasons = sorted(
        query_api.list_seasons(),
        key=_season_key,
        reverse=True,
    )

    st.markdown(
        "<div class='frl-eyebrow'>Explore</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='frl-entity-title'>Head-to-Head</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='frl-context'>Compare two clubs across Premier League history</div>",
        unsafe_allow_html=True,
    )

    if not seasons:
        st.info("No seasons are available.")
        return

    current_season = (
        "2025-26"
        if "2025-26" in seasons
        else seasons[0]
    )

    control_cols = st.columns([1, 1, 1.2], gap="medium")

    with control_cols[0]:
        st.markdown(
            "<div style='color:var(--frl-muted-soft);font-size:.56rem;"
            "font-weight:820;letter-spacing:.12em;text-transform:uppercase;"
            "margin-bottom:.25rem;'>Club</div>",
            unsafe_allow_html=True,
        )
        anchor_season = st.selectbox(
            "Anchor season",
            seasons,
            index=seasons.index(current_season),
            key="h2h_anchor_season",
            label_visibility="collapsed",
        )

    teams = _teams_for_season(anchor_season)

    if len(teams) < 2:
        st.info("Not enough teams are available for a comparison.")
        return

    with control_cols[1]:
        st.markdown(
            "<div style='color:var(--frl-muted-soft);font-size:.56rem;"
            "font-weight:820;letter-spacing:.12em;text-transform:uppercase;"
            "margin-bottom:.25rem;'>Team</div>",
            unsafe_allow_html=True,
        )
        team = st.selectbox(
            "Team",
            teams,
            key="h2h_team",
            label_visibility="collapsed",
        )

    opponents = [name for name in teams if name != team]

    with control_cols[2]:
        st.markdown(
            "<div style='color:var(--frl-muted-soft);font-size:.56rem;"
            "font-weight:820;letter-spacing:.12em;text-transform:uppercase;"
            "margin-bottom:.25rem;'>Opponent</div>",
            unsafe_allow_html=True,
        )
        opponent = st.selectbox(
            "Opponent",
            opponents,
            key="h2h_opponent",
            label_visibility="collapsed",
        )

    st.markdown(
        "<div style='margin-top:.85rem;color:var(--frl-muted-soft);"
        "font-size:.56rem;font-weight:820;letter-spacing:.12em;"
        "text-transform:uppercase;'>Scope</div>",
        unsafe_allow_html=True,
    )

    scope_cols = st.columns(3, gap="small")
    scope = st.session_state.get(
        "h2h_scope",
        "All seasons",
    )

    for col, option in zip(
        scope_cols,
        ["All seasons", "Recent 5", "Custom range"],
    ):
        with col:
            if st.button(
                option,
                key=f"h2h_scope_{option}",
                type="primary" if scope == option else "secondary",
                width="stretch",
            ):
                st.session_state["h2h_scope"] = option
                st.rerun()

    if scope == "All seasons":
        selected_seasons = seasons
        scope_note = f"{seasons[-1]} → {seasons[0]}"
    elif scope == "Recent 5":
        selected_seasons = seasons[:5]
        scope_note = f"{selected_seasons[-1]} → {selected_seasons[0]}"
    else:
        range_cols = st.columns(2, gap="small")
        with range_cols[0]:
            start = st.selectbox(
                "From",
                seasons,
                key="h2h_range_start",
            )
        with range_cols[1]:
            valid_end = [
                value for value in seasons
                if _season_key(value) >= _season_key(start)
            ]
            end = st.selectbox(
                "To",
                valid_end,
                key="h2h_range_end",
            )
        selected_seasons = [
            value for value in seasons
            if _season_key(start) <= _season_key(value) <= _season_key(end)
        ]
        scope_note = f"{start} → {end}"

    h2h = query_api.head_to_head(
        team=team,
        opponent=opponent,
        seasons=selected_seasons,
    )

    summary = h2h.get("summary", {})
    matches = h2h.get("matches", [])

    st.markdown(
        f"<div style='margin-top:.9rem;color:var(--frl-muted-soft);"
        f"font-size:.63rem;'>{team} vs {opponent} · {scope_note}</div>",
        unsafe_allow_html=True,
    )

    metrics = st.columns(4, gap="small")
    metrics[0].metric(f"{team} wins", summary.get("wins", 0))
    metrics[1].metric("Draws", summary.get("draws", 0))
    metrics[2].metric(f"{opponent} wins", summary.get("losses", 0))
    metrics[3].metric("Matches", summary.get("matches", 0))

    st.markdown(
        f"<div style='margin-top:.8rem;color:var(--frl-muted);font-size:.73rem;'>"
        f"Goals: {summary.get('goals_for', 0)}–{summary.get('goals_against', 0)}"
        f" · GD {summary.get('goal_difference', 0):+d}</div>",
        unsafe_allow_html=True,
    )

    skipped = h2h.get("skipped_seasons", [])
    if skipped:
        skipped_text = ", ".join(row["season"] for row in skipped)
        st.caption(f"No Premier League meeting in: {skipped_text}")

    st.markdown(
        "<div style='margin-top:1.2rem;color:var(--frl-accent);"
        "font-size:.60rem;font-weight:820;letter-spacing:.14em;"
        "text-transform:uppercase;'>Meetings</div>",
        unsafe_allow_html=True,
    )

    if not matches:
        st.markdown(
            "<div class='frl-empty-state'>No meetings found for this selection.</div>",
            unsafe_allow_html=True,
        )
        return

    with st.container(border=True):
        header = st.columns([.8, .9, 2.7, .75], gap="small")
        headings = ["Season", "GW", "Fixture", "Result"]

        for col, heading in zip(header, headings):
            col.markdown(
                f"<div style='color:var(--frl-muted-soft);font-size:.56rem;"
                f"font-weight:820;letter-spacing:.08em;text-transform:uppercase;"
                f"padding:.2rem 0;'>{heading}</div>",
                unsafe_allow_html=True,
            )

        st.divider()

        for row in matches:
            result = row.get("team_result", "-")
            result_class = (
                "var(--frl-secondary)" if result == "W"
                else "var(--frl-negative)" if result == "L"
                else "var(--frl-muted)"
            )

            cols = st.columns([.8, .9, 2.7, .75], gap="small")

            cols[0].markdown(
                f"<div style='color:var(--frl-muted);font-size:.70rem;"
                f"padding:.26rem 0;'>{row.get('season', '-')}</div>",
                unsafe_allow_html=True,
            )
            cols[1].markdown(
                f"<div style='color:var(--frl-muted-soft);font-size:.70rem;"
                f"padding:.26rem 0;'>GW {row.get('gameweek', '-')}</div>",
                unsafe_allow_html=True,
            )
            cols[2].markdown(
                f"<div style='color:var(--frl-text);font-size:.72rem;"
                f"font-weight:720;padding:.26rem 0;'>"
                f"{row.get('home_team_name', '')} "
                f"<span style='font-weight:850;'>"
                f"{row.get('home_score', '-')}–{row.get('away_score', '-')}"
                f"</span> {row.get('away_team_name', '')}</div>",
                unsafe_allow_html=True,
            )
            cols[3].markdown(
                f"<div style='text-align:right;color:{result_class};"
                f"font-size:.72rem;font-weight:850;padding:.26rem 0;'>"
                f"{result}</div>",
                unsafe_allow_html=True,
            )
