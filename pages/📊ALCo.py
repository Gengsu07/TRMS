import os
import streamlit as st
import pandas as pd
from datetime import datetime
from datetime import date
from streamlit_extras.chart_container import chart_container
from streamlit_extras.app_logo import add_logo
from streamlit_extras.colored_header import colored_header

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
conn = st.experimental_connection('ppmpkm', type='sql')

if st.session_state["authentication_status"] is None:
    st.warning('Login Duluuu🚨🚨')

else:

    with st.sidebar:
        add_logo("unit.png", height=150)
        st.text(f"Salam Satu Bahu {st.session_state['name']}")
        mindate = datetime.strptime('2023-01-01', "%Y-%m-%d")
        start = st.date_input(
            "Tgl Mulai", min_value=mindate, value=mindate)
        end = st.date_input(
            "Tgl Akhir", max_value=date.today())
        kpp = conn.query(
            'select distinct "ADMIN" from ppmpkm where "ADMIN" notnull')
        kpp = st.multiselect('KPP', options=kpp.iloc[:, 0].tolist())
        map = conn.query(
            'select distinct "MAP" from ppmpkm where "MAP" notnull')
        map = st.multiselect('MAP', options=map.iloc[:, 0].tolist())
        sektor = conn.query(
            'select distinct "NM_KATEGORI" from ppmpkm where "NM_KATEGORI" notnull')
        sektor = st.multiselect('SEKTOR', options=sektor.iloc[:, 0].tolist())
        segmen = conn.query(
            '''select distinct "SEGMENTASI_WP" from ppmpkm where "SEGMENTASI_WP" notnull and "SEGMENTASI_WP"!='' ''')
        segmen = st.multiselect(
            'SEGMENTASI', options=segmen.iloc[:, 0].tolist())

    # Main apps
    st.subheader('ALCo Data Analysis')
