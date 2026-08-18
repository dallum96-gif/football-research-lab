"""Polished Projection Lab UI built around the existing Poisson model."""

import math

import streamlit as st

import poisson_model


TEAM_ORDER = tuple(poisson_model.PREMIER_LEAGUE_2026_27)


def _pct(value):
    return f"{value * 100:.1f}%"


def _odds(value):
    return f"{value:.2f}" if value is not None else "—"


def _scoreline_likelihoods(home_xg, away_xg, max_goals=8):
    rows = []
    for home_goals in range(max_goals + 1):
        home_prob = poisson_model.poisson_probability(home_goals, home_xg)
        for away_goals in range(max_goals + 1):
            away_prob = poisson_model.poisson_probability(away_goals, away_xg)
            rows.append(
                {
                    "scoreline": f"{home_goals}–{away_goals}",
                    "home_goals": home_goals,
                    "away_goals": away_goals,
                    "probability": home_prob * away_prob,
                }
            )
    return sorted(rows, key=lambda row: row["probability"], reverse=True)


def _bar(label, value, tone):
    return (
        "<div style='margin:.65rem 0;'>"
        f"<div style='display:flex;justify-content:space-between;gap:.5rem;font-size:.68rem;font-weight:760;color:var(--frl-text);'>"
        f"<span>{label}</span><span>{_pct(value)}</span></div>"
        "<div style='height:.42rem;margin-top:.28rem;border-radius:999px;background:var(--frl-surface-raised);overflow:hidden;'>"
        f"<div style='height:100%;width:{max(0,min(100,value*100)):.1f}%;background:{tone};border-radius:999px;'></div></div></div>"
    )


def render_projection_lab():
    st.markdown("<div class='frl-eyebrow'>Analysis</div>", unsafe_allow_html=True)
    st.markdown("<div class='frl-entity-title'>Projection Lab</div>", unsafe_allow_html=True)
    st.markdown("<div class='frl-context'>Poisson projection workspace</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <style>
        .frl-proj-hero { margin-top:1rem; padding:1.15rem 1.15rem 1rem; border:1px solid var(--frl-border); border-radius:14px; background:var(--frl-surface); }
        .frl-proj-kicker { color:var(--frl-accent); font-size:.57rem; font-weight:820; letter-spacing:.14em; text-transform:uppercase; }
        .frl-proj-match { margin-top:.5rem; color:var(--frl-text); font-size:clamp(1.7rem,3vw,2.45rem); font-weight:820; letter-spacing:-.045em; line-height:1.02; }
        .frl-proj-meta { margin-top:.4rem; color:var(--frl-muted); font-size:.72rem; }
        .frl-proj-section { margin-top:1.25rem; color:var(--frl-accent); font-size:.60rem; font-weight:820; letter-spacing:.14em; text-transform:uppercase; }
        .frl-proj-card { padding:.95rem 1rem; border:1px solid var(--frl-border); border-radius:12px; background:var(--frl-surface); }
        .frl-proj-card-title { color:var(--frl-text); font-size:.88rem; font-weight:800; }
        .frl-proj-score { margin-top:.45rem; color:var(--frl-text); font-size:2.05rem; font-weight:860; letter-spacing:-.04em; }
        .frl-proj-muted { color:var(--frl-muted); font-size:.72rem; }
        .frl-proj-small { color:var(--frl-muted-soft); font-size:.62rem; }
        div[data-testid='stExpander'] { border:1px solid var(--frl-border) !important; border-radius:10px !important; background:var(--frl-surface) !important; }
        div[data-testid='stExpander'] summary { color:var(--frl-text) !important; font-weight:780 !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if len(TEAM_ORDER) < 2:
        st.error("The projection team universe is not configured.")
        return

    source_season = poisson_model.SOURCE_SEASON
    target_season = poisson_model.TARGET_SEASON

    controls = st.columns([1, 1, 1.15], gap="medium")

    with controls[0]:
        st.markdown("<div style='color:var(--frl-muted-soft);font-size:.56rem;font-weight:820;letter-spacing:.12em;text-transform:uppercase;margin-bottom:.24rem;'>Target season</div>", unsafe_allow_html=True)
        st.selectbox("Target season", [target_season], key="projection_target_season_v2", label_visibility="collapsed")

    with controls[1]:
        st.markdown("<div style='color:var(--frl-muted-soft);font-size:.56rem;font-weight:820;letter-spacing:.12em;text-transform:uppercase;margin-bottom:.24rem;'>Home team</div>", unsafe_allow_html=True)
        home_team = st.selectbox("Home team", TEAM_ORDER, index=TEAM_ORDER.index("Arsenal") if "Arsenal" in TEAM_ORDER else 0, key="projection_home_team_v2", label_visibility="collapsed")

    with controls[2]:
        st.markdown("<div style='color:var(--frl-muted-soft);font-size:.56rem;font-weight:820;letter-spacing:.12em;text-transform:uppercase;margin-bottom:.24rem;'>Away team</div>", unsafe_allow_html=True)
        away_options = [team for team in TEAM_ORDER if team != home_team]
        away_team = st.selectbox("Away team", away_options, index=away_options.index("Manchester United") if "Manchester United" in away_options else 0, key="projection_away_team_v2", label_visibility="collapsed")

    try:
        prediction = poisson_model.poisson_prediction(home_team=home_team, away_team=away_team)
    except Exception as exc:
        st.error("Projection could not be generated from the current model/data.")
        st.code(f"{type(exc).__name__}: {exc}")
        return

    probs = prediction["probabilities"]
    expected = prediction["expected_goals"]
    likely = prediction["most_likely_score"]
    fair = prediction["fair_odds"]

    st.markdown(
        "<div class='frl-proj-hero'>"
        "<div class='frl-proj-kicker'>Projection</div>"
        f"<div class='frl-proj-match'>{home_team} <span style='color:var(--frl-muted-soft);font-weight:650;'>vs</span> {away_team}</div>"
        f"<div class='frl-proj-meta'>{prediction['model']} · Premier League {target_season} · built from {source_season} evidence</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='frl-proj-section'>Expected goals</div>", unsafe_allow_html=True)
    xcols = st.columns(2, gap="medium")
    for col, team, value in zip(xcols, [home_team, away_team], [expected["home"], expected["away"]]):
        with col:
            st.markdown(
                f"<div class='frl-proj-card'><div class='frl-proj-card-title'>{team}</div><div class='frl-proj-score'>{value:.2f}</div><div class='frl-proj-muted'>expected goals</div></div>",
                unsafe_allow_html=True,
            )

    st.markdown("<div class='frl-proj-section'>Outcome probabilities</div>", unsafe_allow_html=True)
    outcome_cols = st.columns(2, gap="medium")
    with outcome_cols[0]:
        st.markdown(
            "<div class='frl-proj-card'><div class='frl-proj-card-title'>1X2</div>"
            + _bar(home_team, probs["home_win"], "var(--frl-secondary)")
            + _bar("Draw", probs["draw"], "var(--frl-warning)")
            + _bar(away_team, probs["away_win"], "var(--frl-accent)")
            + "</div>",
            unsafe_allow_html=True,
        )
    with outcome_cols[1]:
        st.markdown(
            "<div class='frl-proj-card'><div class='frl-proj-card-title'>Match conditions</div>"
            + _bar("Over 2.5 goals", probs["over_2_5"], "var(--frl-accent)")
            + _bar("Both teams to score", probs["btts"], "var(--frl-secondary)")
            + "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div class='frl-proj-section'>Model favourite</div>", unsafe_allow_html=True)
    score_cols = st.columns(2, gap="medium")
    with score_cols[0]:
        st.markdown(
            f"<div class='frl-proj-card'><div class='frl-proj-card-title'>Most likely score</div><div class='frl-proj-score'>{likely['home']}–{likely['away']}</div><div class='frl-proj-muted'>{_pct(likely['probability'])} probability</div></div>",
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

    likelihoods = _scoreline_likelihoods(expected["home"], expected["away"])
    top_scorelines = likelihoods[:12]

    with st.expander("Scoreline likelihoods", expanded=False):
        st.markdown(
            "<div class='frl-proj-muted'>Exact-score probabilities from the same Poisson distribution. Ranked from most to least likely.</div>",
            unsafe_allow_html=True,
        )
        for index, row in enumerate(top_scorelines, start=1):
            cols = st.columns([.55, 2.2, 1], gap="small")
            cols[0].markdown(f"<div style='color:var(--frl-muted-soft);font-size:.64rem;padding:.30rem 0;'>{index:02d}</div>", unsafe_allow_html=True)
            cols[1].markdown(f"<div style='color:var(--frl-text);font-size:.73rem;font-weight:760;padding:.30rem 0;'>{home_team} {row['scoreline']} {away_team}</div>", unsafe_allow_html=True)
            cols[2].markdown(f"<div style='color:var(--frl-accent);font-size:.73rem;font-weight:820;text-align:right;padding:.30rem 0;'>{_pct(row['probability'])}</div>", unsafe_allow_html=True)

    with st.expander("Model notes", expanded=False):
        st.markdown(
            f"**Model:** {prediction['model']}  \n"
            f"**Source season:** {prediction['source_season']}  \n"
            f"**Target season:** {prediction['target_season']}  \n"
            f"**Promotion prior:** {prediction['promotion_method']}"
        )
        league = prediction["league_environment"]
        st.caption(
            f"Source scoring environment: {league['home_goals']:.2f} home goals and {league['away_goals']:.2f} away goals per match across {league['matches']} completed fixtures."
        )

        odds_col = st.columns(3, gap="small")
        with odds_col[0]:
            home_odds = st.number_input("Home odds", min_value=1.01, value=2.50, step=0.01, key="projection_home_odds_v2")
        with odds_col[1]:
            draw_odds = st.number_input("Draw odds", min_value=1.01, value=3.40, step=0.01, key="projection_draw_odds_v2")
        with odds_col[2]:
            away_odds = st.number_input("Away odds", min_value=1.01, value=2.80, step=0.01, key="projection_away_odds_v2")

        market = poisson_model.compare_bookmaker_odds(prediction, home_odds, draw_odds, away_odds)
        st.markdown(f"Overround: **{market['overround']*100-100:.1f}%**")

        edge_cols = st.columns(3, gap="small")
        labels = [(home_team, "home_win"), ("Draw", "draw"), (away_team, "away_win")]
        for col, (label, key) in zip(edge_cols, labels):
            edge = market["probability_edge"][key]
            ev = market["expected_value"][key]
            col.metric(label, _pct(market["market_probability"][key]), f"{edge*100:+.1f} pp · EV {ev:+.3f}")
