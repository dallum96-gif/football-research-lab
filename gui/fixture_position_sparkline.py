"""Small presentation helper for the Fixture Explorer header."""


def gw_34_38_positions(season, team, get_fixtures):
    """Return GW34-GW38 league positions for a team, carrying positions forward."""
    rows = get_fixtures(
        season=season,
        team=None,
        opponent=None,
        venue=None,
        result=None,
        limit=5000,
    )["results"]

    rows.sort(
        key=lambda row: (
            int(row.get("gameweek", 0) or 0),
            str(row.get("kickoff_time", "")),
            int(row.get("fixture_id", 0)),
        )
    )

    table = {}
    for row in rows:
        for club in (row.get("home_team_name"), row.get("away_team_name")):
            if club:
                table.setdefault(club, {"points": 0, "gd": 0, "gf": 0})

    if team not in table:
        return []

    def apply_fixture(row):
        home = row.get("home_team_name")
        away = row.get("away_team_name")
        hs = row.get("home_score")
        aw = row.get("away_score")

        if home not in table or away not in table:
            return
        if hs in (None, "") or aw in (None, ""):
            return

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

    prior_rows = []
    by_gameweek = {}
    for row in rows:
        try:
            gameweek = int(row.get("gameweek", 0) or 0)
        except (TypeError, ValueError):
            continue

        if gameweek < 34:
            prior_rows.append(row)
        elif 34 <= gameweek <= 38:
            by_gameweek.setdefault(gameweek, []).append(row)

    for row in prior_rows:
        apply_fixture(row)

    history = []
    current_position = None

    for gameweek in range(34, 39):
        for row in by_gameweek.get(gameweek, []):
            apply_fixture(row)

        ordered = sorted(
            table.items(),
            key=lambda item: (
                -item[1]["points"],
                -item[1]["gd"],
                -item[1]["gf"],
                item[0].casefold(),
            ),
        )
        current_position = next(
            (idx for idx, (club, _) in enumerate(ordered, start=1) if club == team),
            current_position,
        )
        history.append((gameweek, current_position))

    return history


def render_last_five_position_sparkline(season, team, get_fixtures):
    """Render a compact inline SVG sparkline for GW34-GW38 league positions."""
    import html
    import streamlit as st

    history = gw_34_38_positions(season, team, get_fixtures)
    if not history:
        st.markdown(
            "<div style='color:var(--frl-muted-soft);font-size:0.58rem;font-weight:800;letter-spacing:0.10em;text-transform:uppercase;padding-top:0.25rem;'>No league position data</div>",
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
        return pad_x + (plot_width * index / 4)

    def y_for(position):
        span = max(1, max_position - 1)
        return pad_y + ((position - 1) / span) * plot_height

    points = [(x_for(i), y_for(position)) for i, (_, position) in enumerate(history)]
    polyline = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)

    circles = "".join(
        f"<circle cx='{x:.1f}' cy='{y:.1f}' r='3.2' fill='var(--frl-accent)'/>"
        for x, y in points
    )

    labels = "".join(
        f"<text x='{x_for(i):.1f}' y='{height - 1}' text-anchor='middle' fill='var(--frl-muted-soft)' font-size='7' font-weight='800'>GW {gameweek}</text>"
        for i, (gameweek, _) in enumerate(history)
    )

    last_position = history[-1][1]

    st.markdown(
        f"""
        <div style='padding:0.05rem 0.35rem 0;'>
          <div style='display:flex;justify-content:space-between;align-items:center;color:var(--frl-muted-soft);font-size:0.55rem;font-weight:800;letter-spacing:0.10em;text-transform:uppercase;'>
            <span>GW34â€“38 position</span>
            <span>Now Â· {last_position}th</span>
          </div>
          <svg viewBox='0 0 {width} {height}' style='display:block;width:100%;height:3.8rem;margin-top:0.15rem;' role='img' aria-label='League positions for {html.escape(team)} from gameweek 34 to gameweek 38'>
            <line x1='{pad_x}' y1='{pad_y}' x2='{width-pad_x}' y2='{pad_y}' stroke='rgba(24,23,20,0.08)' stroke-width='1'/>
            <polyline points='{polyline}' fill='none' stroke='var(--frl-accent)' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'/>
            {circles}
            {labels}
          </svg>
        </div>
        """,
        unsafe_allow_html=True,
    )

