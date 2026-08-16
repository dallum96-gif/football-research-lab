import streamlit as st


st.title("Prediction Lab")
st.caption(
    "Poisson modelling workspace."
)

st.info(
    "The existing Prediction Lab remains available in "
    "Legacy Workspace while this page is migrated into "
    "the new navigation structure."
)

if st.button(
    "Open full Prediction Lab",
    type="primary",
):
    st.switch_page(
        "pages/99_Legacy_Workspace.py"
    )
