from __future__ import annotations

import pandas as pd
import streamlit as st

from fixture_evidence import fixture_evidence, player_display_rows


CORE_TEAM_FIELDS = [
    "possessionPercentage",
    "totalScoringAtt",
    "ontargetScoringAtt",
    "cornerTaken",
    "totalPass",
    "accuratePass",
    "totalTackle",
    "interception",
    "totalClearance",
    "totalYelCard",
    "totalRedCard",
]

CORE_PLAYER_COLUMNS = [
    "Player",
    "Team",
    "Role",
    "Minutes",
    "Goals",
    "Assists",
    "Rating",
]



def _value(row: dict, field: str) -> str:
    value = row.get(f"source_{field}")
    if value in (None, ""):
        return "—"
    try:
        number = float(value)
        return str(int(number)) if number.is_integer() else f"{number:.1f}"
    except (TypeError, ValueError):
        return str(value)


def _team_summary(rows: list[dict[str, str]]) -> pd.DataFrame:
    records = []
    for row in rows:
        record = {"Statistic": field for field in CORE_TEAM_FIELDS}
        record["Team"] = row.get("source_team", "")
        for field in CORE_TEAM_FIELDS:
            record[field] = _value(row, field)
        records.append(record)
    return pd.DataFrame(records)


def _team_comparison(rows: list[dict[str, str]]) -> pd.DataFrame:
    if len(rows) != 2:
        return pd.DataFrame()
    home = rows[0]
    away = rows[1]
    records = []
    for field in CORE_TEAM_FIELDS:
        records.append(
            {
                "Statistic": field,
                home.get("source_team", "Home"): _value(home, field),
                away.get("source_team", "Away"): _value(away, field),
            }
        )
    return pd.DataFrame(records)


def _render_player_group(rows: list[dict[str, str]], role: str) -> None:
    filtered = [row for row in rows if row.get("frl_participation_status") == role]
    if not filtered:
        st.caption("No source records in this category.")
        return
    table = pd.DataFrame(player_display_rows(filtered))
    st.dataframe(table[CORE_PLAYER_COLUMNS], width="stretch", hide_index=True)


def render_fixture_landing(detail: dict) -> None:
    fixture = detail["fixture"]
    stats = detail["stats"]
    season = str(fixture["season"])
    fixture_id = str(fixture["fixture_id"])
    evidence = fixture_evidence(season, fixture_id)

    home = fixture["home_team_name"]
    away = fixture["away_team_name"]
    home_score = fixture["home_score"] if fixture["home_score"] not in (None, "") else "—"
    away_score = fixture["away_score"] if fixture["away_score"] not in (None, "") else "—"

    st.markdown(
        f"<div style='text-align:center;color:var(--frl-muted-soft);font-size:.62rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;'>{season} · GW {fixture['gameweek']}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='text-align:center;color:var(--frl-muted);font-size:.72rem;margin-top:.18rem;'>{fixture['kickoff_time'][:10]}</div>",
        unsafe_allow_html=True,
    )

    score = st.columns([1.2, .8, 1.2], gap="small", vertical_alignment="center")
    with score[0]:
        st.markdown(f"<div style='text-align:right;color:var(--frl-text);font-size:1.42rem;font-weight:820;'>{home}</div>", unsafe_allow_html=True)
    with score[1]:
        st.markdown(f"<div style='text-align:center;color:var(--frl-text);font-size:3rem;font-weight:850;line-height:1;'>{home_score}&ndash;{away_score}</div>", unsafe_allow_html=True)
    with score[2]:
        st.markdown(f"<div style='text-align:left;color:var(--frl-text);font-size:1.42rem;font-weight:820;'>{away}</div>", unsafe_allow_html=True)

    if fixture.get("data_corrected") == "true":
        st.info("This fixture contains a verified historical data correction. The analytical view uses the corrected kickoff and result.")

    if stats.get("status") != "AVAILABLE":
        st.warning("Historical match statistics are not available for this fixture.")

    if evidence["team"]["status"] == "AVAILABLE":
        st.markdown("<div style='margin-top:1.2rem;color:var(--frl-accent);font-size:.60rem;font-weight:820;letter-spacing:.14em;text-transform:uppercase;'>Team evidence</div>", unsafe_allow_html=True)
        st.caption("Complete source-native team evidence is attached to both sides of the canonical fixture. The first view shows the most useful matchday variables.")
        st.dataframe(_team_comparison(evidence["team"]["rows"]), width="stretch", hide_index=True)
        with st.expander(f"All team evidence · {len(evidence['team']['source_fields'])} source fields"):
            raw = []
            for row in evidence["team"]["rows"]:
                for field in evidence["team"]["source_fields"]:
                    raw.append({
                        "Team": row.get("source_team", ""),
                        "Field": field,
                        "Value": _value(row, field),
                    })
            st.dataframe(pd.DataFrame(raw), width="stretch", hide_index=True)
    else:
        st.info("Complete team evidence is not available in the local evidence materialisation for this fixture.")

    if evidence["players"]["status"] == "AVAILABLE":
        player_rows = evidence["players"]["rows"]
        st.markdown("<div style='margin-top:1.4rem;color:var(--frl-accent);font-size:.60rem;font-weight:820;letter-spacing:.14em;text-transform:uppercase;'>Players</div>", unsafe_allow_html=True)

        home_rows = [r for r in player_rows if r.get("source_team") == home]
        away_rows = [r for r in player_rows if r.get("source_team") == away]

        home_col, away_col = st.columns(2, gap="medium")
        with home_col:
            st.markdown(f"**{home}**")
            with st.expander("Starting XI", expanded=True):
                _render_player_group(home_rows, "starting")
            with st.expander("Used substitutes", expanded=False):
                _render_player_group(home_rows, "sub_in")
            with st.expander("Unused substitutes", expanded=False):
                _render_player_group(home_rows, "bench")

        with away_col:
            st.markdown(f"**{away}**")
            with st.expander("Starting XI", expanded=True):
                _render_player_group(away_rows, "starting")
            with st.expander("Used substitutes", expanded=False):
                _render_player_group(away_rows, "sub_in")
            with st.expander("Unused substitutes", expanded=False):
                _render_player_group(away_rows, "bench")

        with st.expander(f"All player-match evidence · {len(evidence['players']['source_fields'])} source fields"):
            raw = pd.DataFrame(player_display_rows(player_rows))
            st.dataframe(raw, width="stretch", hide_index=True)
            st.caption("Source player IDs remain source-local. Canonical player identity is only established where the FRL identity layer verifies the relationship.")
    else:
        st.info("Player-match evidence is not available in the local evidence materialisation for this fixture.")

    with st.expander("Match provenance & evidence state"):
        st.write(
            {
                "Canonical fixture ID": fixture_id,
                "Season": season,
                "PL source match ID": stats.get("source_match_id"),
                "Canonical fixture source": detail.get("provenance", {}).get("canonical_source"),
                "Identity source": detail.get("provenance", {}).get("identity_source"),
                "Correction source": detail.get("provenance", {}).get("correction_source"),
                "Team evidence rows": evidence["availability"]["team_rows"],
                "Player evidence rows": evidence["availability"]["player_rows"],
            }
        )
