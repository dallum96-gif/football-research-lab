"""Projection Lab workspace built around the existing Poisson model."""

import streamlit as st

import poisson_model


TEAM_ORDER = tuple(poisson_model.PREMIER_LEAGUE_2026_27)


def _pct(value):
    return f"{value * 100:.1f}%"


def _odds(value):
    return f"{value:.2f}" if value is not None else "—"


def _bar(label, value, tone):
    return (
        "<div style='margin:.65rem 0;'>"
        f"<div style='display:flex;justify-content:space-between;gap:.5rem;"
        f"font-size:.68rem;font-weight:760;color:var(--frl-text);'>"
        f"<span>{label}</span><span>{_pct(value)}</span></div>"
        "<div style='height:.42rem;margin-top:.28rem;border-radius:999px;"
        "background:var(--frl-surface-raised);overflow:hidden;'>"
        f"<div style='height:100%;width:{max(0,min(100,value*100)):.1f}%;"
        f"background:{tone};border-radius:999px;'></div></div></div>"
    )


def render_projection_lab():
    st.markdown(
        "<div class='frl-eyebrow'>Modelling</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='frl-entity-title'>Projection Lab</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='frl-context'>Model a prospective Premier League fixture from attacking and defensive strength.</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <style>
        .frl-proj-hero {
            margin-top:1rem;
            padding:1.15rem 1.15rem 1rem;
            border:1px solid var(--frl-border);
            border-radius:14px;
            background:var(--frl-surface);
        }
        .frl-proj-kicker {
            color:var(--frl-accent);
            font-size:.57rem;
            font-weight:820;
            letter-spacing:.14em;
            text-transform:uppercase;
        }
        .frl-proj-match {
            margin-top:.5rem;
            color:var(--frl-text);
            font-size:clamp(1.7rem,3vw,2.45rem);
            font-weight:820;
            letter-spacing:-.045em;
            line-height:1.02;
        }
        .frl-proj-meta {
            margin-top:.4rem;
            color:var(--frl-muted);
            font-size:.72rem;
        }
        .frl-proj-section {
            margin-top:1.25rem;
            color:var(--frl-accent);
            font-size:.60rem;
            font-weight:820;
            letter-spacing:.14em;
            text-transform:uppercase;
        }
        .frl-proj-card {
            padding:.95rem 1rem;
            border:1px solid var(--frl-border);
            border-radius:12px;
            background:var(--frl-surface);
        }
        .frl-proj-card-title {
            color:var(--frl-text);
            font-size:.88rem;
            font-weight:800;
        }
        .frl-proj-card-note {
            margin-top:.18rem;
            color:var(--frl-muted-soft);
            font-size:.64rem;
            line-height:1.35;
        }
        .frl-proj-score {
            margin-top:.45rem;
            color:var(--frl-text);
            font-size:2.05rem;
            font-weight:860;
            letter-spacing:-.04em;
        }
        .frl-proj-muted {
            color:var(--frl-muted);
            font-size:.72rem;
        }
        .frl-proj-small {
            color:var(--frl-muted-soft);
            font-size:.62rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if len(TEAM_ORDER) < 2:
        st.error("The projection team universe is not configured.")
        return

    current_default = "2025-26"
    source_season = poisson_model.SOURCE_SEASON
    target_season = poisson_model.TARGET_SEASON

    controls = st.columns([1, 1, 1.15], gap="medium")

    with controls[0]:
        st.markdown(
            "<div style='color:var(--frl-muted-soft);font-size:.56rem;font-weight:820;"
            "letter-spacing:.12em;text-transform:uppercase;margin-bottom:.24rem;'>"
            "Target season</div>",
            unsafe_allow_html=True,
        )
        st.selectbox(
            "Target season",
            [target_season],
            index=0,
            key="projection_target_season",
            label_visibility="collapsed",
        )

    with controls[1]:
        st.markdown(
            "<div style='color:var(--frl-muted-soft);font-size:.56rem;font-weight:820;"
            "letter-spacing:.12em;text-transform:uppercase;margin-bottom:.24rem;'>"
            "Home team</div>",
            unsafe_allow_html=True,
        )
        home_team = st.selectbox(
            "Home team",
            TEAM_ORDER,
            index=TEAM_ORDER.index("Arsenal") if "Arsenal" in TEAM_ORDER else 0,
            key="projection_home_team",
            label_visibility="collapsed",
        )

    with controls[2]:
        st.markdown(
            "<div style='color:var(--frl-muted-soft);font-size:.56rem;font-weight:820;"
            "letter-spacing:.12em;text-transform:uppercase;margin-bottom:.24rem;'>"
            "Away team</div>",
            unsafe_allow_html=True,
        )
        away_options = [team for team in TEAM_ORDER if team != home_team]
        away_team = st.selectbox(
            "Away team",
            away_options,
            index=away_options.index("Manchester United") if "Manchester United" in away_options else 0,
            key="projection_away_team",
            label_visibility="collapsed",
        )

    prediction = poisson_model.poisson_prediction(
        home_team=home_team,
        away_team=away_team,
    )

    probs = prediction["probabilities"]
    expected = prediction["expected_goals"]
    likely = prediction["most_likely_score"]
    fair = prediction["fair_odds"]

    st.markdown(
        "<div class='frl-proj-hero'>"
        "<div class='frl-proj-kicker'>Projection</div>"
        f"<div class='frl-proj-match'>{home_team} <span style='color:var(--frl-muted-soft);font-weight:650;'>vs</span> {away_team}</div>"
        f"<div class='frl-proj-meta'>Poisson {prediction['model'].replace('Poisson ', '')} · Premier League {target_season} · built from {source_season} evidence</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='frl-proj-section'>Expected goals</div>",
        unsafe_allow_html=True,
    )

    xcols = st.columns(2, gap="medium")
    with xcols[0]:
        st.markdown(
            f"<div class='frl-proj-card'><div class='frl-proj-card-title'>{home_team}</div>"
            f"<div class='frl-proj-score'>{expected['home']:.2f}</div>"
            "<div class='frl-proj-muted'>expected goals</div></div>",
            unsafe_allow_html=True,
        )
    with xcols[1]:
        st.markdown(
            f"<div class='frl-proj-card'><div class='frl-proj-card-title'>{away_team}</div>"
            f"<div class='frl-proj-score'>{expected['away']:.2f}</div>"
            "<div class='frl-proj-muted'>expected goals</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        "<div class='frl-proj-section'>Outcome probabilities</div>",
        unsafe_allow_html=True,
    )

    outcome_cols = st.columns(2, gap="medium")
    with outcome_cols[0]:
        st.markdown(
            "<div class='frl-proj-card'>"
            "<div class='frl-proj-card-title'>1X2</div>"
            + _bar(home_team, probs["home_win"], "var(--frl-secondary)")
            + _bar("Draw", probs["draw"], "var(--frl-warning)")
            + _bar(away_team, probs["away_win"], "var(--frl-accent)")
            + "</div>",
            unsafe_allow_html=True,
        )

    with outcome_cols[1]:
        st.markdown(
            "<div class='frl-proj-card'>"
            "<div class='frl-proj-card-title'>Match conditions</div>"
            + _bar("Over 2.5 goals", probs["over_2_5"], "var(--frl-accent)")
            + _bar("Both teams to score", probs["btts"], "var(--frl-secondary)")
            + "</div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        "<div class='frl-proj-section'>Most likely score</div>",
        unsafe_allow_html=True,
    )

    score_cols = st.columns(2, gap="medium")
    with score_cols[0]:
        st.markdown(
            f"<div class='frl-proj-card'><div class='frl-proj-card-title'>Model favourite</div>"
            f"<div class='frl-proj-score'>{likely['home']}–{likely['away']}</div>"
            f"<div class='frl-proj-muted'>{_pct(likely['probability'])} probability</div></div>",
            unsafe_allow_html=True,
        )
    with score_cols[1]:
        st.markdown(
            "<div class='frl-proj-card'><div class='frl-proj-card-title'>Fair odds</div>"
            f"<div style='margin-top:.7rem;display:grid;grid-template-columns:repeat(3,1fr);gap:.65rem;'>"
            f"<div><div class='frl-proj-small'>{home_team}</div><div class='frl-proj-score' style='font-size:1.45rem;'>{_odds(fair['home_win'])}</div></div>"
            f"<div><div class='frl-proj-small'>Draw</div><div class='frl-proj-score' style='font-size:1.45rem;'>{_odds(fair['draw'])}</div></div>"
            f"<div><div class='frl-proj-small'>{away_team}</div><div class='frl-proj-score' style='font-size:1.45rem;'>{_odds(fair['away_win'])}</div></div>"
            "</div></div>",
            unsafe_allow_html=True,
        )

    with st.expander("Model notes", expanded=False):
        st.markdown(
            f"**Model:** {prediction['model']}  \n"
            f"**Source season:** {prediction['source_season']}  \n"
            f"**Target season:** {prediction['target_season']}  \n"
            f"**Promotion prior:** {prediction['promotion_method']}"
        )
        league = prediction["league_environment"]
        st.caption(
            f"Source scoring environment: {league['home_goals']:.2f} home goals and "
            f"{league['away_goals']:.2f} away goals per match across {league['matches']} completed fixtures."
        )

        odds_col = st.columns(3, gap="small")
        with odds_col[0]:
            home_odds = st.number_input("Home odds", min_value=1.01, value=2.50, step=0.01, key="projection_home_odds")
        with odds_col[1]:
            draw_odds = st.number_input("Draw odds", min_value=1.01, value=3.40, step=0.01, key="projection_draw_odds")
        with odds_col[2]:
            away_odds = st.number_input("Away odds", min_value=1.01, value=2.80, step=0.01, key="projection_away_odds")

        market = poisson_model.compare_bookmaker_odds(
            prediction,
            home_odds,
            draw_odds,
            away_odds,
        )

        st.markdown(
            f"Overround: **{market['overround']*100-100:.1f}%**"
        )

        edge_cols = st.columns(3, gap="small")
        labels = [(home_team, "home_win"), ("Draw", "draw"), (away_team, "away_win")]
        for col, (label, key) in zip(edge_cols, labels):
            edge = market["probability_edge"][key]
            ev = market["expected_value"][key]
            col.metric(
                label,
                _pct(market["market_probability"][key]),
                f"{edge*100:+.1f} pp · EV {ev:+.3f}",
            )
