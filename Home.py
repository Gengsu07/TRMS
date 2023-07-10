import streamlit as st
from streamlit_toggle import st_toggle_switch

from streamlit_extras.switch_page_button import switch_page


st.set_page_config(
    page_title="Tax Revenue Monitoring Sistem",
    page_icon="assets\logo_djo.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)
with open("style/home.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

with st.sidebar:
    switch = st_toggle_switch(
        label="Darkmode",
        key="switch_1",
        default_value=False,
        label_after=False,
        inactive_color="#D3D3D3",  # optional
        active_color="#11567f",  # optional
        track_color="#29B5E8",  # optional
    )


st.image("assets/unit.png", width=200)
st.title("Tax Revenue Monitoring Sistem🚀")
st.markdown("### Kanwil DJP Jakarta Timur")
st.text(f" Salam Satu Bahu")


# Add login/logout buttons
