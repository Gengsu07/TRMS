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

def data_awal():
    adm = conn.query('select distinct p."ADMIN" from ppmpkm p')
    map = conn.query('select distinct p."MAP" from ppmpkm p')
    kat = conn.query('select distinct p."NM_KATEGORI" from ppmpkm p')
    seg = conn.query('select distinct p."SEGMENTASI_WP" from ppmpkm p')
    data = pd.concat([adm, map, kat, seg], axis=1, ignore_index=True)
    data.columns = ['adm','map','kat','seg']
    return data 

def list_to_sql(column, value):
    value_str = ','.join([f"'{x}'"  for x in value])
    sql_filter = f'"{column}" IN ({value_str})'
    return sql_filter

def filter_gabungan():
    filter_gabungan = []
    if kpp :
        filter_kpp = list_to_sql('ADMIN',kpp)
        filter_gabungan.append(filter_kpp)
    if map:
        filter_map = list_to_sql('MAP',map)
        filter_gabungan.append(filter_map)
    if sektor:
        filter_sektor = list_to_sql('NM_KATEGORI',sektor)
        filter_gabungan.append(filter_sektor)
    if segmen:
        filter_segmen = list_to_sql('SEGMENTASI_WP',segmen)
        filter_gabungan.append(filter_segmen)

    # colgab = '"ADMIN","KDMAP","KDBAYAR","TANGGALBAYAR","BULANBAYAR","TAHUNBAYAR","DATEBAYAR","NOMINAL","KET","NPWP","NAMA_WP","NAMA_AR","SEKSI","SEGMENTASI_WP","NM_KLU","KET_KLU","NM_KATEGORI","MAP"'

    #     data = conn.query(f'select {colgab} from ppmpkm p where {filter} and "TAHUNBAYAR">2021')
    # else:
    #     data = conn.query(f'select {colgab} from ppmpkm p where "TAHUNBAYAR">2021')
    filter = filterpool(filter_gabungan)
    return filter

def filterpool(x):
        if x:
            filterpool = 'and'.join(x)
        else:
            filterpool = ''
        return filterpool

#Sidebar
with st.sidebar:
    data_awal = data_awal()
    kpp = st.multiselect('KPP',options=data_awal['adm'].unique().tolist())
    map = st.multiselect('MAP',options=data_awal['map'].unique().tolist())
    sektor = st.multiselect('SEKTOR',options=data_awal['kat'].unique().tolist())
    segmen = st.multiselect('SEGMENTASI',options=data_awal['seg'].unique().tolist())


#Main apps    
st.title('Tax Earning Monitoring Sistem')


col_tahun = st.columns(3)
with col_tahun[0]:
    data23 = conn.query('select sum("NOMINAL") from ppmpkm p where and p."TAHUNBAYAR"=2023')["sum"].sum()
    st.metric('2023', data23)
with col_tahun[1]:
    data22 = conn.query('select sum("NOMINAL") from ppmpkm p where p."TAHUNBAYAR"=2022')["sum"].sum()
    st.metric('2022',data22)
with col_tahun[2]:
    selisih = data23-data22
    st.metric('Kenaikan',selisih)



st.dataframe(data)



