import os
import streamlit as st
import pandas as pd
from datetime import datetime
from datetime import date
from streamlit_extras.chart_container import chart_container
from streamlit_extras.app_logo import add_logo
from streamlit_extras.colored_header import colored_header
from dateutil.relativedelta import relativedelta
from streamlit_extras.altex import sparkline_chart
from streamlit_extras.metric_cards import style_metric_cards
import importlib
prep = importlib.import_module('db')

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
conn = st.experimental_connection('ppmpkm', type='sql')


def list_to_sql(column, value):
    value_str = ','.join([f"'{x}'" for x in value])
    sql_filter = f'"{column}" IN ({value_str})'
    return sql_filter


def cek_filter(start, end, kpp, map, sektor, segmen):
    filter_gabungan = []
    filter_gabungan22 = []
    if start:
        filter_start = f'''"DATEBAYAR">='{start}' '''
        filter_gabungan.append(filter_start)
        # tahun-1
        filter_start22 = start-relativedelta(years=1)
        filter_gabungan22.append(f'''"DATEBAYAR">='{filter_start22}' ''')
    if end:
        filter_end = f'''"DATEBAYAR"<='{end}' '''
        filter_gabungan.append(filter_end)
        # tahun-1
        filter_end22 = end-relativedelta(years=1)
        filter_gabungan22.append(f'''"DATEBAYAR"<='{filter_end22}' ''')
    if kpp:
        filter_kpp = list_to_sql('ADMIN', kpp)
        filter_gabungan.append(filter_kpp)
        filter_gabungan22.append(filter_kpp)
    if map:
        filter_map = list_to_sql('MAP', map)
        filter_gabungan.append(filter_map)
        filter_gabungan22.append(filter_map)
    if sektor:
        filter_sektor = list_to_sql('NM_KATEGORI', sektor)
        filter_gabungan.append(filter_sektor)
        filter_gabungan22.append(filter_sektor)
    if segmen:
        filter_segmen = list_to_sql('SEGMENTASI_WP', segmen)
        filter_gabungan.append(filter_segmen)
        filter_gabungan22.append(filter_segmen)
    return [filter_gabungan, filter_gabungan22]


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

    # filterdata
    filter_gabungan = cek_filter(start, end, kpp, map, sektor, segmen)
    filter = 'and'.join(x for x in filter_gabungan[0])
    filter22 = 'and'.join(x for x in filter_gabungan[1])

    # Main apps
    st.subheader('Year over Year')
    style_metric_cards(background_color='#FFFFFF',
                       border_color='#005FAC', border_left_color='#005FAC')
    sektor_yoy = prep.sektor_yoy(filter, filter22)

    sektor_div1 = st.columns(4)
    with sektor_div1[0]:
        st.metric("{:+,.1f}M".format(sektor_yoy.loc[0, 'NM_KATEGORI']),
                  value=sektor_yoy.loc[0, '2023'], delta=sektor_yoy.loc[0, 'selisih'])
