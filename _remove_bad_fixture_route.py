from pathlib import Path

path = Path(r".\gui\app_redesign.py")
text = path.read_text(encoding="utf-8-sig")

text = text.replace(
    "from gui.fixture_detail_view import render_fixture_detail_view\n",
    "",
    1,
)

route = '''fixture_token = st.query_params.get("fixture")

if fixture_token:
    try:
        fixture_season, fixture_id = fixture_token.split(":", 1)
        detail = query_api.fixture_detail(
            season=fixture_season,
            fixture_id=fixture_id,
        )
        render_fixture_detail_view(detail)
        st.stop()
    except Exception as exc:
        st.error(f"Unable to open fixture: {exc}")
        st.stop()

'''

text = text.replace(route, "", 1)

path.write_text(text, encoding="utf-8")
print("Removed invalid fixture-detail import/route.")
