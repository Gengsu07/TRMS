import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
postgres = create_engine('postgresql+psycopg2://postgres:sgwi2341@localhost:5432/jaktim')

#settings
st.set_page_config(
page_title="TEMS",
page_icon="🧠",
layout='wide')
conn = st.experimental_connection('ppmpkm', type='sql')


#Sidebar
with st.sidebar:
    kpp = conn.query('select distinct "ADMIN" from ppmpkm where "ADMIN" notnull')
    kpp = st.multiselect('KPP',options=kpp.iloc[:,0].tolist())
    map = conn.query('select distinct "MAP" from ppmpkm where "MAP" notnull')
    map = st.multiselect('MAP',options=map.iloc[:,0].tolist())
    sektor = conn.query('select distinct "NM_KATEGORI" from ppmpkm where "NM_KATEGORI" notnull')
    sektor = st.multiselect('SEKTOR',options=sektor.iloc[:,0].tolist())
    segmen = conn.query('select distinct "SEGMENTASI_WP" from ppmpkm where "SEGMENTASI_WP" notnull')
    segmen = st.multiselect('SEGMENTASI',options=segmen.iloc[:,0].tolist())


#Main apps    
st.title('Tax Earning Monitoring Sistem')
