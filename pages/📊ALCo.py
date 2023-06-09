import streamlit as st
import pandas as pd
from datetime import datetime
from datetime import date
from streamlit_extras.chart_container import chart_container
from streamlit_extras.app_logo import add_logo
from streamlit_extras.colored_header import colored_header
import os

st.set_page_config(
    page_title="Tax Revenue Monitoring Sistem",
    page_icon="🚀",
    layout='wide')
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

conn = st.experimental_connection('ppmpkm', type='sql')

with st.sidebar:
    add_logo("unit.png", height=150)
    colored_header(
        label='ALCo Data Filter',
        description='Pilih Filter Data',
        color_name='yellow-80')
    mindate = datetime.strptime('2023-01-01', "%Y-%m-%d")
    start = st.date_input(
        "Tgl Mulai", min_value=mindate, value=mindate)
    end = st.date_input(
        "Tgl Akhir", max_value=date.today())
    kpp = conn.query(
        'select distinct "ADMIN" from ppmpkm where "ADMIN" notnull')
    kpp = st.multiselect('KPP', options=kpp.iloc[:, 0].tolist())
    map = conn.query('select distinct "MAP" from ppmpkm where "MAP" notnull')
    map = st.multiselect('MAP', options=map.iloc[:, 0].tolist())
    sektor = conn.query(
        'select distinct "NM_KATEGORI" from ppmpkm where "NM_KATEGORI" notnull')
    sektor = st.multiselect('SEKTOR', options=sektor.iloc[:, 0].tolist())
    segmen = conn.query(
        '''select distinct "SEGMENTASI_WP" from ppmpkm where "SEGMENTASI_WP" notnull and "SEGMENTASI_WP"!='' ''')
    segmen = st.multiselect('SEGMENTASI', options=segmen.iloc[:, 0].tolist())

# Main apps
st.subheader('ALCo Data Analysis')
