from pathlib import Path
import runpy
import streamlit as st

# Apply prototype-only tab contrast before the wrapped page creates its tabs.
st.markdown("""
<style>
/* Streamlit tabs: keep both lineup labels readable on the warm light theme. */
[data-baseweb="tab-list"] button,
[data-baseweb="tab-list"] button div,
[data-baseweb="tab-list"] button p,
[data-baseweb="tab-list"] button span {
    color: var(--frl-text) !important;
    opacity: 1 !important;
}
[data-baseweb="tab-list"] button[aria-selected="true"] {
    color: var(--frl-text) !important;
}
</style>
""", unsafe_allow_html=True)

ROOT = Path(__file__).resolve().parent.parent
runpy.run_path(str(ROOT / "gui" / "fixture_result_prototype_v6.py"), run_name="__main__")
