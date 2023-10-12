import streamlit as st
from PIL import Image


st.set_page_config(
    page_title="Tax Revenue Monitoring Sistem",
    page_icon="assets/logo_djo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(
    """
        <style>
               .block-container {
                    margin-top:2rem;
                    padding-top: 0rem;
                    padding-bottom: 0rem;
                    padding-left: 1rem;
                    padding-right: 1rem;
                }
                [data-testid="stHeader"]{
                    display:none
                }
        </style>
        """,
    unsafe_allow_html=True,
)

unit = Image.open("assets/unit.png")
st.image(unit, use_column_width=False)


st.image(Image.open("assets/kj.png"), use_column_width=False, width=280)
st.title("Selamat Datang")
st.markdown("#### Silakan pilih aplikasi di menu sidebar")


# Add login/logout buttons
