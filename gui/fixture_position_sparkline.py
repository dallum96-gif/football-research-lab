"""Small presentation helper for the Fixture Explorer header."""


def last_five_positions(season, team, get_fixtures):
    """Return (gameweek, position) pairs after the team's last five completed matches."""
    rows = get_fixtures(season=season, team=None, opponent=None, venue=None, result=None)["results"]
    rows.sort(key=lambda row: (str(row.get("kickoff_time", "")), int(row.get("fixture_id", 0))))

    team_matches = []
    for row in rows:
        home = row.get("home_team_name")
        away = row.get("away_team_name")
        if team not in (home, away):
            continue
        if row.get("home_score") in (None, "") or row.get("away_score") in (None, ""):
            continue
        team_matches.append(row)

    if not team_matches:
        return []

    table = {}
    for row in rows:
        for club in (row.get("home_team_name"), row.get("away_team_name")):
            if club:
                table.setdefault(club, {"points": 0, "gd": 0, "gf": 0})

    history = []
    for fixture in rows:
        home = fixture.get("home_team_name")
        away = fixture.get("away_team_name")
        hs = fixture.get("home_score")
        aw = fixture.get("away_score")
        if home not in table or away not in table or hs in (None, "") or aw in (None, ""):
            continue

        hs = int(hs)
        aw = int(aw)
        table[home]["gf"] += hs
        table[home]["gd"] += hs - aw
        table[away]["gf"] += aw
        table[away]["gd"] += aw - hs

        if hs > aw:
            table[home]["points"] += 3
        elif aw > hs:
            table[away]["points"] += 3
        else:
            table[home]["points"] += 1
            table[away]["points"] += 1

        if team in (home, away):
            ordered = sorted(
                table.items(),
                key=lambda item: (
                    -item[1]["points"],
                    -item[1]["gd"],
                    -item[1]["gf"],
                    item[0].casefold(),
                ),
            )
            position = next((idx for idx, (club, _) in enumerate(ordered, start=1) if club == team), None)
            if position is not None:
                history.append((fixture.get("gameweek", ""), position))

    return history[-5:]


def render_last_five_position_sparkline(season, team, get_fixtures):
    """Render a compact inline SVG sparkline for the team's last five league positions."""
    import html
    import streamlit as st

    history = last_five_positions(season, team, get_fixtures)
    if not history:
        st.markdown(
            "<div style='color:var(--frl-muted-soft);font-size:0.58rem;font-weight:800;letter-spacing:0.10em;text-transform:uppercase;padding-top:0.25rem;'>No completed fixtures yet</div>",
            unsafe_allow_html=True,
        )
        return

    width = 250
    height = 64
    pad_x = 12
    pad_y = 10
    positions = [position for _, position in history]
    max_position = max(positions)
    plot_height = height - (pad_y * 2)
    plot_width = width - (pad_x * 2)

    def x_for(index):
        if len(history) == 1:
            return width / 2
        return pad_x + (plot_width * index / (len(history) - 1))

    def y_for(position):
        span = max(1, max_position - 1)
        return pad_y + ((position - 1) / span) * plot_height

    points = [(x_for(i), y_for(position)) for i, (_, position) in enumerate(history)]
    polyline = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    last_gw = html.escape(str(history[-1][0]))
    last_position = history[-1][1]

    circles = "".join(
        f"<circle cx='{x:.1f}' cy='{y:.1f}' r='3.2' fill='var(--frl-accent)'/>"
        for x, y in points
    )

    st.markdown(
        f"""
        <div style='padding:0.05rem 0.35rem 0;'>
          <div style='display:flex;justify-content:space-between;align-items:center;color:var(--frl-muted-soft);font-size:0.55rem;font-weight:800;letter-spacing:0.10em;text-transform:uppercase;'>
            <span>Last 5 positions</span>
            <span>GW {last_gw} · {last_position}th</span>
          </div>
          <svg viewBox='0 0 {width} {height}' style='display:block;width:100%;height:3.8rem;margin-top:0.15rem;' role='img' aria-label='Last five league positions for {html.escape(team)}'>
            <line x1='{pad_x}' y1='{pad_y}' x2='{width-pad_x}' y2='{pad_y}' stroke='rgba(24,23,20,0.08)' stroke-width='1'/>
            <polyline points='{polyline}' fill='none' stroke='var(--frl-accent)' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'/>
            {circles}
          </svg>
        </div>
        """,
        unsafe_allow_html=True,
    )
