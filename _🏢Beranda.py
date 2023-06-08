import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
import plotly.express as px
import calendar
from streamlit_extras.chart_container import chart_container
from streamlit_extras.app_logo import add_logo
from streamlit_extras.colored_header import colored_header

# postgres = create_engine(
#     'postgresql+psycopg2://postgres:sgwi2341@localhost:5432/jaktim')

# settings
st.set_page_config(
    page_title="Tax Earning Monitoring Sistem",
    page_icon="🚀",
    layout='wide')
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
# padding = 0
# st.markdown(f""" <style>.reportview-container .main .block-container{{
#         padding-top: {padding}rem;
#         padding-right: {0}rem;
#         padding-left: {0}rem;
#         padding-bottom: {padding}rem;}} </style> """, unsafe_allow_html=True)
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


def data_ket(filter, filter22):
    ket = conn.query(f'''select p."KET",
    sum(case when p."TAHUNBAYAR" =2023 then p."NOMINAL" end ) as "2023"
    from ppmpkm p
    where {filter}
    GROUP BY p."KET"     ''')

    ket22 = conn.query(f'''select p."KET",
    sum(case when p."TAHUNBAYAR" =2022 then p."NOMINAL" end ) as "2022"
    from ppmpkm p
    where {filter22}
    GROUP BY p."KET"     ''')

    ketgab = ket.merge(ket22, on='KET', how='left')
    ketgab['selisih'] = ketgab['2023']-ketgab['2022']
    return ketgab


# Sidebar
with st.sidebar:
    add_logo("unit.png", height=150)
    colored_header(
        label='Tax Earning Monitoring System',
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
# st.title('Tax Earning Monitoring Sistem')

# filterdata
filter_gabungan = cek_filter(start, end, kpp, map, sektor, segmen)
filter = 'and'.join(x for x in filter_gabungan[0])
filter22 = 'and'.join(x for x in filter_gabungan[1])


# # KPI
col_tahun = st.columns(5)
with col_tahun[0]:
    if filter:
        data23 = conn.query(
            f'select sum("NOMINAL") from ppmpkm p where {filter}')["sum"].sum()
    else:
        data23 = conn.query(
            f'''select sum("NOMINAL") from ppmpkm p where {filter_gabungan[0][0] +'and'+ filter_gabungan[0][1]} ''')["sum"].sum()
    if (data23/1000000000000) > 1:
        st.metric('2023', '{:,.1f}T'.format(data23/1000000000000))
    else:
        st.metric('2023', '{:,.1f}M'.format(data23/1000000000))
with col_tahun[1]:
    if filter:
        data22 = conn.query(
            f'select sum("NOMINAL") from ppmpkm p where {filter22}')["sum"].sum()
    else:
        data22 = conn.query(
            f'''select sum("NOMINAL") from ppmpkm p where {filter_gabungan[1][0] +'and'+ filter_gabungan[1][1]} ''')["sum"].sum()
    if (data22/1000000000000) > 1:
        st.metric('2022', '{:,.1f}T'.format(data22/1000000000000))
    else:
        st.metric('2022',  '{:,.1f}M'.format(data22/1000000000))
with col_tahun[2]:
    selisih = (data23-data22)
    if (selisih) > 1000000000000:
        st.metric('Kenaikan', '{:,.1f}T'.format(selisih/1000000000000))
    else:
        st.metric('Kenaikan',  '{:,.1f}M'.format(selisih/1000000000))
with col_tahun[3]:
    selisih = (data23-data22)
    tumbuh = selisih/data22
    st.metric('Tumbuh',  '{:.1f}%'.format(tumbuh*100))
with col_tahun[4]:
    persentase = data23/27601733880000
    st.metric('Kontrib Target Kanwil',  '{:.2f}%'.format(persentase*100))

st.markdown("""<hr style="height:1px;border:none;color:#FFFFFF;background-color:#ffc91b;" /> """,
            unsafe_allow_html=True)
# KET
ket = data_ket(filter, filter22).set_index('KET')

colket = st.columns(5)
with colket[0]:
    format_number = "{:+,.1f}M" if ket.loc['MPN',
                                           'selisih'] >= 0 else "{:-,.1f}M"
    format_number_T = "{:+,.1f}T" if ket.loc['MPN',
                                             'selisih'] >= 0 else "{:-,.1f}T"
    if ket.loc['MPN', 'selisih'] > 1000000000000:
        st.metric('MPN', format_number_T.format(ket.loc['MPN',
                                                        'selisih']/1000000000000))
    else:
        st.metric('MPN', format_number.format(ket.loc['MPN',
                                                      'selisih']/1000000000))
with colket[1]:
    format_number = "{:+,.1f}M" if ket.loc['SPM',
                                           'selisih'] >= 0 else "{:-,.1f}M"
    st.metric('SPM', format_number.format(ket.loc['SPM',
                                                  'selisih']/1000000000))
with colket[2]:
    format_number = "{:+,.1f}M" if ket.loc['PBK KIRIM',
                                           'selisih'] >= 0 else "{:-,.1f}M"
    st.metric('PBK KIRIM', format_number.format(ket.loc['PBK KIRIM',
                                                        'selisih']/1000000000))
with colket[3]:
    format_number = "{:+,.1f}M" if ket.loc['PBK TERIMA',
                                           'selisih'] >= 0 else "{:-,.1f}M"
    st.metric('PBK TERIMA', format_number.format(ket.loc['PBK TERIMA',
                                                         'selisih']/1000000000))
with colket[4]:
    format_number = "{:+,.1f}M" if ket.loc['SPMKP',
                                           'selisih'] >= 0 else "{:-,.1f}M"
    st.metric('SPMKP', format_number.format(ket.loc['SPMKP',
                                                    'selisih']/1000000000))


# title={'text': 'Penerimaan Per Bulan',
#                                'x': 0.5, 'xanchor': 'center', 'yanchor': 'top',
#                                'font': {'size': 24}},

st.markdown("""<hr style="height:1px;border:none;color:#FFFFFF;background-color:#ffc91b;" /> """,
            unsafe_allow_html=True)
# bar
bardata = conn.query(
    f'''select p."BULANBAYAR",p."TAHUNBAYAR",sum("NOMINAL") from ppmpkm p 
            where {filter}
            GROUP BY p."BULANBAYAR",p."TAHUNBAYAR"
            UNION ALL
            select p."BULANBAYAR",p."TAHUNBAYAR",sum("NOMINAL") from ppmpkm p 
            where {filter22}
            GROUP BY p."BULANBAYAR" ,p."TAHUNBAYAR"
            ''')
bardata['TAHUNBAYAR'] = bardata['TAHUNBAYAR'].astype('str')
bardata['text'] = bardata['sum'].apply(lambda x: "{:,.1f}M".format(
    x/1000000000))
barchart = px.bar(data_frame=bardata, x="BULANBAYAR",
                  y='sum', color='TAHUNBAYAR', barmode='group', text='text', width=960, height=380)
barchart.update_layout(xaxis_title='', yaxis_title='',
                       yaxis={'visible': False},
                       xaxis={
                           'tickmode': 'array',
                           'tickvals': [x for x in range(1, 13)],
                           'ticktext': [calendar.month_name[i] for i in range(1, 13)]
                       }, autosize=True)

with chart_container(bardata):
    st.plotly_chart(barchart)
