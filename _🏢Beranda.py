from yaml.loader import SafeLoader
import yaml
import streamlit_authenticator as stauth
import streamlit as st
import pandas as pd
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
import plotly.express as px
import calendar
from streamlit_extras.chart_container import chart_container
from streamlit_extras.app_logo import add_logo
from streamlit_extras.colored_header import colored_header
from streamlit_extras.metric_cards import style_metric_cards
import altair as alt
import importlib
prep = importlib.import_module('db')
passw = importlib.import_module('login')

# settings
st.set_page_config(
    page_title="Tax Revenue Monitoring Sistem",
    page_icon="🚀",
    layout='wide')
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


conn = st.experimental_connection('ppmpkm', type='sql')

# Function/module


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


# ---AUTHENTICATION---
with open('.streamlit/login.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

names = passw.names()
usernames = passw.usernames()

hashed_password = passw.load_pass()
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)
name, authentication_status, username = authenticator.login(
    "👋Login-TRMS👋", 'main')
if st.session_state['authentication_status'] is False:
    st.error("Username atau Password salah 🫢")
elif st.session_state["authentication_status"] is None:
    st.warning('Masukan username dan password yang sesuai')
elif st.session_state['authentication_status']:

    # Sidebar
    with st.sidebar:
        if st.session_state["authentication_status"]:
            authenticator.logout('Logout', 'sidebar')
            st.text(f'Salam Satu Bahu: {name}')
        add_logo("unit.png", height=150)
        # colored_header(
        #     label='Tax Revenue Monitoring System',
        #     description='Pilih Filter Data',
        #     color_name='yellow-80')
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
    st.subheader('Tax Revenue Monitoring Sistem')

# filterdata
    filter_gabungan = cek_filter(start, end, kpp, map, sektor, segmen)
    filter = 'and'.join(x for x in filter_gabungan[0])
    filter22 = 'and'.join(x for x in filter_gabungan[1])

    linedata = conn.query(
        f'''select p."BULANBAYAR",p."TAHUNBAYAR",sum("NOMINAL") from ppmpkm p 
                where {filter}
                GROUP BY p."BULANBAYAR",p."TAHUNBAYAR"
                UNION ALL
                select p."BULANBAYAR",p."TAHUNBAYAR",sum("NOMINAL") from ppmpkm p 
                where {filter22}
                GROUP BY p."BULANBAYAR" ,p."TAHUNBAYAR"
                ''')
    linedata['TAHUNBAYAR'] = linedata['TAHUNBAYAR'].astype('str')
    linedata = linedata.groupby(['TAHUNBAYAR', 'BULANBAYAR'])[
        'sum'].sum().reset_index()
    linedata['text'] = linedata['sum'].apply(lambda x: "{:,.1f}M".format(
        x/1000000000))
    linechart = px.area(data_frame=linedata, x="BULANBAYAR",
                        y='sum', color='TAHUNBAYAR', text='text', width=1024, height=380)
    linechart.update_layout(xaxis_title='', yaxis_title='',
                            yaxis={'visible': False},
                            xaxis={
                                'tickmode': 'array',
                                'tickvals': [x for x in range(1, 13)],
                                'ticktext': [calendar.month_name[i] for i in range(1, 13)]
                            }, autosize=True)

    with chart_container(linedata):
        st.plotly_chart(linechart)

# KPI
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
        if (data22 == 0) | (selisih == 0):
            tumbuh = 0
        else:
            tumbuh = selisih/data22
        st.metric('Tumbuh',  '{:.1f}%'.format(tumbuh*100))
    with col_tahun[4]:
        persentase = data23/27601733880000
        st.metric('Kontrib Target Kanwil',  '{:.2f}%'.format(persentase*100))

    style_metric_cards(background_color='#FFFFFF',
                       border_color='#ffc91b', border_left_color='#ffc91b')
    st.markdown("""<hr style="height:1px;border:none;color:#FFFFFF;background-color:#ffc91b;" /> """,
                unsafe_allow_html=True)
# KET
    ket = data_ket(filter, filter22).set_index('KET')

    colket = st.columns(5)
    with colket[0]:

        if 'MPN' in ket.index:
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
        else:
            st.metric('MPN', '0M')
    with colket[1]:
        if 'SPM' in ket.index:
            format_number = "{:+,.1f}M" if ket.loc['SPM',
                                                   'selisih'] >= 0 else "{:-,.1f}M"
            st.metric('SPM', format_number.format(ket.loc['SPM',
                                                          'selisih']/1000000000))
        else:
            st.metric('SPM', "0.0M")
    with colket[2]:
        if 'PBK KIRIM' in ket.index:
            format_number = "{:+,.1f}M" if ket.loc['PBK KIRIM',
                                                   'selisih'] >= 0 else "{:-,.1f}M"
            st.metric('PBK KIRIM', format_number.format(ket.loc['PBK KIRIM',
                                                                'selisih']/1000000000))
        else:
            st.metric('PBK KIRIM', "0.0M")
    with colket[3]:
        if 'PBK TERIMA' in ket.index:
            format_number = "{:+,.1f}M" if ket.loc['PBK TERIMA',
                                                   'selisih'] >= 0 else "{:-,.1f}M"
            st.metric('PBK TERIMA', format_number.format(ket.loc['PBK TERIMA',
                                                                 'selisih']/1000000000))
        else:
            st.metric('PBK TERIMA', "0.0M")
    with colket[4]:
        if 'SPMKP' in ket.index:
            format_number = "{:+,.1f}M" if ket.loc['SPMKP',
                                                   'selisih'] >= 0 else "{:-,.1f}M"
            st.metric('SPMKP', format_number.format(ket.loc['SPMKP',
                                                            'selisih']/1000000000))
        else:
            st.metric('SPMKP', '0.0M')

    st.markdown("""<hr style="height:1px;border:none;color:#FFFFFF;background-color:#ffc91b;" /> """,
                unsafe_allow_html=True)

    data_sektor_awal = prep.sektor(filter)
    # data_sektor = data_sektor_awal.melt(
    #     id_vars='NM_KATEGORI', var_name='JENIS', value_name='NOMINAL', value_vars=['NETTO', 'BRUTO'])

    # sektor = alt.Chart(data_sektor).mark_bar().encode(
    #     x=alt.X('sum(NOMINAL)', stack='normalize'),
    #     y='NM_KATEGORI',
    #     color='JENIS'
    # )
    # st.altair_chart(sektor)
    data_sektor_awal = data_sektor_awal.groupby(
        ['NM_KATEGORI'])['NETTO'].sum().reset_index().sort_values(by='NETTO', ascending=True)
    data_sektor_awal['text'] = data_sektor_awal['NETTO'].apply(
        lambda x: '{:,.1f}M'.format(x/1000000000))
    bar_sektor = px.bar(data_sektor_awal, y='NM_KATEGORI', x='NETTO', title="Per Sektor", orientation='h', text='text',
                        width=1024, height=1024)
    bar_sektor.update_layout(xaxis_title='', yaxis_title='',
                             xaxis={'visible': False},
                             title={
                                 'x': 0.5,
                                 'font_size': 24
                             },
                             autosize=True, showlegend=False)
    st.plotly_chart(bar_sektor)
    st.dataframe(data_sektor_awal)

    data_funnel = prep.bruto(filter)
    data_funnel_chart = data_funnel.loc[:9,]
    data_funnel_chart['x'] = data_funnel_chart['BRUTO']/1000000000
    funnel_chart = px.funnel(data_funnel_chart, x='x',
                             y='NAMA_WP', text='KONTRIBUSI', width=1280, height=640,
                             log_x=True, title='10 WP Penyumbang Penerimaan Terbesar Bruto')
    funnel_chart.update_traces(
        texttemplate='%{x:,.2f}M <br> (%{customdata:.2f}%)', customdata=data_funnel_chart['KONTRIBUSI'])
    funnel_chart.update_layout(xaxis_title='', yaxis_title='',
                               title={
                                   'x': 0.5,
                                   'font_size': 24
                               },
                               autosize=True)

    with chart_container(data_funnel):
        st.plotly_chart(funnel_chart)
