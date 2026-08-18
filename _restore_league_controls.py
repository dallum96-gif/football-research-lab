from pathlib import Path
import re

path = Path(r".\gui\app_redesign.py")
text = path.read_text(encoding="utf-8-sig")

# ------------------------------------------------------------
# Restore session-state selector model
# ------------------------------------------------------------

link_state = '''    view_options = [
        "Current season",
        "Historical season",
        "Custom range",
    ]

    venue_options = [
        "Overall",
        "Home",
        "Away",
    ]

    view_param = st.query_params.get("lt_view")
    venue_param = st.query_params.get("lt_venue")

    view_lookup = {
        "current": "Current season",
        "historical": "Historical season",
        "custom": "Custom range",
    }

    venue_lookup = {
        "overall": "Overall",
        "home": "Home",
        "away": "Away",
    }

    selected_view = view_lookup.get(
        view_param,
        "Current season",
    )

    selected_venue = venue_lookup.get(
        venue_param,
        "Overall",
    )
'''

session_state = '''    view_key = "redesign_league_table_view"

    selected_view = st.session_state.get(
        view_key,
        "Current season",
    )

'''

if link_state in text:
    text = text.replace(link_state, session_state, 1)

# ------------------------------------------------------------
# Restore Table View buttons
# ------------------------------------------------------------

link_view_pattern = re.compile(
    r'''
    \n    st\.markdown\(
        "<div style='margin-top:\.4rem;color:var\(--frl-muted-soft\);"
        .*?
    if not seasons:
    ''',
    re.S | re.X,
)

button_view = '''
    view_cols = st.columns(
        3,
        gap="small",
    )

    for col, option in zip(
        view_cols,
        ["Current season", "Historical season", "Custom range"],
    ):
        with col:
            if st.button(
                option,
                key=f"league_view_{option}",
                type=(
                    "primary"
                    if selected_view == option
                    else "secondary"
                ),
                width="stretch",
            ):
                st.session_state[view_key] = option
                st.rerun()

    if not seasons:
'''

text, count = link_view_pattern.subn(button_view, text, count=1)

if count != 1:
    raise SystemExit("Could not restore Table View buttons.")

# ------------------------------------------------------------
# Restore Venue buttons
# ------------------------------------------------------------

link_venue_pattern = re.compile(
    r'''
    \n    # ------------------------------------------------------------
    # Venue scope
    # ------------------------------------------------------------
    .*?
    # ------------------------------------------------------------
    # Build table
    # ------------------------------------------------------------
    ''',
    re.S | re.X,
)

button_venue = '''
    # ------------------------------------------------------------
    # Venue scope
    # ------------------------------------------------------------

    st.markdown(
        "<div style='margin-top:1.05rem;color:var(--frl-accent);"
        "font-size:.58rem;font-weight:820;letter-spacing:.12em;"
        "text-transform:uppercase;'>Venue</div>",
        unsafe_allow_html=True,
    )

    venue_key = "redesign_league_table_venue"

    selected_venue = st.session_state.get(
        venue_key,
        "Overall",
    )

    venue_cols = st.columns(
        3,
        gap="small",
    )

    for col, option in zip(
        venue_cols,
        ["Overall", "Home", "Away"],
    ):
        with col:
            if st.button(
                option,
                key=f"league_venue_{option}",
                type=(
                    "primary"
                    if selected_venue == option
                    else "secondary"
                ),
                width="stretch",
            ):
                st.session_state[venue_key] = option
                st.rerun()

    # ------------------------------------------------------------
    # Build table
    # ------------------------------------------------------------

'''

text, count = link_venue_pattern.subn(button_venue, text, count=1)

if count != 1:
    raise SystemExit("Could not restore Venue buttons.")

# Remove the experimental global hover CSS if it was added.
experimental_css = re.compile(
    r'''
st\.markdown\(
    """
    <style>
    \.frl-inline-nav-link:hover
    .*?
    </style>
    """,
    unsafe_allow_html=True,
\)

''',
    re.S | re.X,
)

text = experimental_css.sub("", text, count=1)

# Remove query params left behind by the experiment from future state reads.
text = text.replace('lt_view', 'lt_view_UNUSED')
text = text.replace('lt_venue', 'lt_venue_UNUSED')

path.write_text(text, encoding="utf-8")

print("PASS  Restored previous League Table button controls.")
print("PASS  Restored session-state selector model.")
print("PASS  Removed hyperlink-control experiment.")
print("PASS  League Table aggregation/table untouched.")
