import streamlit as st
import pandas as pd
from datetime import datetime
from datetime import date
from streamlit_extras.chart_container import chart_container
from streamlit_extras.app_logo import add_logo
from dateutil.relativedelta import relativedelta
from streamlit_extras.metric_cards import style_metric_cards
import plotly.figure_factory as ff
import plotly.express as px
from math import ceil
import plotly.graph_objects as go
from scripts.db import sektor_yoy, growth_month, subsektor


if "darkmode" not in st.session_state:
    st.session_state["darkmode"] = "off"

if st.session_state["darkmode"] == "on":
    with open("style/pages_alco_darkmode.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
else:
    with open("style/pages_alco.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
conn = st.experimental_connection("ppmpkm", type="sql")


def list_to_sql(column, value):
    value_str = ",".join([f"'{x}'" for x in value])
    sql_filter = f'"{column}" IN ({value_str})'
    return sql_filter


def cek_filter(start, end, kpp, map, sektor, segmen, wp):
    filter_gabungan = []
    filter_gabungan22 = []
    if start:
        filter_start = f""""DATEBAYAR">='{start}' """
        filter_gabungan.append(filter_start)
        # tahun-1
        filter_start22 = start - relativedelta(years=1)
        filter_gabungan22.append(f""""DATEBAYAR">='{filter_start22}' """)
    if end:
        filter_end = f""""DATEBAYAR"<='{end}' """
        filter_gabungan.append(filter_end)
        # tahun-1
        filter_end22 = end - relativedelta(years=1)
        filter_gabungan22.append(f""""DATEBAYAR"<='{filter_end22}' """)
    if kpp:
        filter_kpp = list_to_sql("ADMIN", kpp)
        filter_gabungan.append(filter_kpp)
        filter_gabungan22.append(filter_kpp)
    if map:
        filter_map = list_to_sql("MAP", map)
        filter_gabungan.append(filter_map)
        filter_gabungan22.append(filter_map)
    if sektor:
        filter_sektor = list_to_sql("NM_KATEGORI", sektor)
        filter_gabungan.append(filter_sektor)
        filter_gabungan22.append(filter_sektor)
    if segmen:
        filter_segmen = list_to_sql("SEGMENTASI_WP", segmen)
        filter_gabungan.append(filter_segmen)
        filter_gabungan22.append(filter_segmen)
    if wp:
        filter_wp = list_to_sql("NAMA_WP", wp)
        filter_gabungan.append(filter_wp)
        filter_gabungan22.append(filter_wp)
    return [filter_gabungan, filter_gabungan22]


def format_number(x):
    if x / 1000000000000 > 1:
        number = "{:,.1f}T".format(x / 1000000000000)
    elif x / 1000000000 > 1:
        number = "{:,.1f}M".format(x / 1000000000)
    else:
        number = "{:,.1f}Jt".format(x / 1000000)
    return number


if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = None

if st.session_state["authentication_status"] is None:
    st.warning("🚨🚨Ke Beranda atau Login Duluuu🚨🚨")

else:
    with st.sidebar:
        add_logo("assets/unit.png", height=150)
        st.text(f"Salam Satu Bahu {st.session_state['name']}")
        urutan = st.radio(
            "Urut Berdasarkan:", options=["2023", "2022", "tumbuh"], horizontal=True
        )
        mindate = datetime.strptime("2023-01-01", "%Y-%m-%d")
        start = st.date_input("Tgl Mulai", min_value=mindate, value=mindate)
        end = st.date_input("Tgl Akhir", max_value=date.today())
        kpp = conn.query('select distinct "ADMIN" from ppmpkm where "ADMIN" notnull')
        kpp = st.multiselect("KPP", options=kpp.iloc[:, 0].tolist())
        map = conn.query('select distinct "MAP" from ppmpkm where "MAP" notnull')
        map = st.multiselect("MAP", options=map.iloc[:, 0].tolist())
        sektor = conn.query(
            'select distinct "NM_KATEGORI" from ppmpkm where "NM_KATEGORI" notnull'
        )
        sektor = st.multiselect("SEKTOR", options=sektor.iloc[:, 0].tolist())
        segmen = conn.query(
            """select distinct "SEGMENTASI_WP" from ppmpkm where "SEGMENTASI_WP" notnull and "SEGMENTASI_WP"!='' """
        )
        segmen = st.multiselect("SEGMENTASI", options=segmen.iloc[:, 0].tolist())
        # wp
        wp = conn.query(
            """select distinct "NAMA_WP" from ppmpkm where "NAMA_WP" notnull and "NAMA_WP"!=''
            """
        )
        wp = st.multiselect("Wajib Pajak", wp["NAMA_WP"].tolist())

    # filterdata
    filter_gabungan = cek_filter(start, end, kpp, map, sektor, segmen, wp)
    filter = "and".join(x for x in filter_gabungan[0])
    filter22 = "and".join(x for x in filter_gabungan[1])

    # Main apps
    style_metric_cards(
        background_color="rgba(0,0,0,0)",
        border_color="rgba(0,0,0,0)",
        border_left_color="rgba(0,0,0,0)",
    )

    # SEKTORRRR CARD
    sektor = sektor_yoy(filter, filter22, includewp=False)
    *_, sektor_mom, sektor_yoy = sektor

    # st.dataframe(sektor)
    sektor_yoy["%kontribusi"] = (sektor_yoy["2023"] / sektor_yoy["2023"].sum()) * 100

    sektor_yoy1 = sektor_yoy[sektor_yoy["NM_KATEGORI"] != "KLU ERROR"]
    sektor_yoy["rank"] = sektor_yoy[f"{urutan}"].rank(ascending=False)

    sektor_plus = sektor_yoy1[sektor_yoy1["selisih"] > 0]
    sektor_plus["rank"] = sektor_plus[f"{urutan}"].rank(ascending=False)
    sektor_plus.set_index("rank", inplace=True)
    sektor_min = sektor_yoy1[sektor_yoy1["selisih"] < 0]
    sektor_min["rank"] = sektor_min[f"{urutan}"].rank(ascending=False)
    sektor_min.set_index("rank", inplace=True)

    # CONTAINER SEKTOR SURPLUS
    rows = ceil(len(sektor_plus) / 4)
    st.subheader(f"💡 Sektor Surplus {start} s.d. {end}")
    container = {}
    counter = 1
    for row in range(1, rows + 1):
        container[row] = st.container()
        with container[row]:
            cekisi = len(sektor_plus)
            cek_baris = ceil(cekisi / 4)
            sisa4 = cekisi % 4
            if row < cek_baris:
                col = st.columns(4)
            elif sisa4 == 1:
                col = st.columns([25, 75])
            elif sisa4 == 2:
                col = st.columns([25, 25, 75])
            else:
                col = st.columns([25, 25, 25, 25])
            for x in range(1, 5):
                if counter <= len(sektor_plus):
                    with col[x - 1]:
                        data_col = sektor_plus[sektor_plus.index == counter]
                        gridkat = data_col.loc[counter, "NM_KATEGORI"]
                        sektor_mom_select = sektor_mom[
                            sektor_mom["NM_KATEGORI"] == gridkat
                        ]
                        sektor_mom_select.drop(columns="NM_KATEGORI", inplace=True)
                        sektor_mom_select = (
                            sektor_mom_select.groupby("BULANBAYAR").sum().reset_index()
                        )
                        sektor_mom_select = sektor_mom_select.melt(
                            id_vars="BULANBAYAR", value_name="NOMINAL"
                        )
                        # st.dataframe(sektor_mom_select)
                        spark = px.line(
                            sektor_mom_select,
                            x="BULANBAYAR",
                            y="NOMINAL",
                            color="TAHUNBAYAR",
                            markers=True,
                            height=100,
                            width=200,
                            # color_discrete_sequence=["#ffc91b", "#005FAC"],
                        )

                        spark.update_layout(
                            template=None,
                            xaxis_title="",
                            yaxis_title="",
                            yaxis={"visible": False},
                            xaxis={"visible": False},
                            margin=dict(l=0, r=0, t=0, b=0),
                            paper_bgcolor="rgba(0, 0, 0, 0)",
                            plot_bgcolor="rgba(0, 0, 0, 0)",
                            autosize=True,
                            showlegend=False,
                        )
                        st.plotly_chart(spark, use_container_width=True)
                        st.metric(
                            data_col.loc[counter, "NM_KATEGORI"],
                            value=format_number(data_col.loc[counter, "2023"]),
                            delta="{:,.2f}%".format(data_col.loc[counter, "tumbuh"]),
                        )

                    counter += 1

    # SEKTOR MINUS
    rows = ceil(len(sektor_min) / 4)
    st.subheader(f"💡 Sektor Shortfall {start} s.d. {end}")
    container = {}
    counter = 1
    for row in range(1, rows + 1):
        container[row] = st.container()
        with container[row]:
            cekisi = len(sektor_plus)
            cek_baris = ceil(cekisi / 4)
            sisa4 = cekisi % 4
            if row < cek_baris:
                col = st.columns(4)
            elif sisa4 == 1:
                col = st.columns([25, 75])
            elif sisa4 == 2:
                col = st.columns([25, 25, 75])
            else:
                col = st.columns([25, 25, 25, 25])

            for x in range(1, 5):
                if counter <= len(sektor_min):
                    with col[x - 1]:
                        data_col = sektor_min[sektor_min.index == counter]
                        gridkat = data_col.loc[counter, "NM_KATEGORI"]

                        sektor_mom_select = sektor_mom[
                            sektor_mom["NM_KATEGORI"] == gridkat
                        ]
                        sektor_mom_select.drop(columns="NM_KATEGORI", inplace=True)
                        sektor_mom_select = (
                            sektor_mom_select.groupby("BULANBAYAR").sum().reset_index()
                        )
                        sektor_mom_select = sektor_mom_select.melt(
                            id_vars="BULANBAYAR", value_name="NOMINAL"
                        )

                        spark = px.line(
                            sektor_mom_select,
                            x="BULANBAYAR",
                            y="NOMINAL",
                            color="TAHUNBAYAR",
                            markers=True,
                            height=100,
                            width=200,
                        )
                        spark.update_layout(
                            template=None,
                            xaxis_title="",
                            yaxis_title="",
                            yaxis={"visible": False},
                            xaxis={"visible": False},
                            margin=dict(l=0, r=0, t=0, b=0),
                            paper_bgcolor="rgba(0, 0, 0, 0)",
                            plot_bgcolor="rgba(0, 0, 0, 0)",
                            autosize=True,
                            showlegend=False,
                        )
                        st.plotly_chart(spark, use_container_width=True)
                        st.metric(
                            data_col.loc[counter, "NM_KATEGORI"],
                            value=format_number(data_col.loc[counter, "2023"]),
                            delta="{:,.2f}%".format(data_col.loc[counter, "tumbuh"]),
                        )
                    counter += 1

    with st.expander("Detail Data"):
        sektor_yoy.sort_values(by="rank", ascending=True, inplace=True)
        with chart_container(sektor_yoy):
            st.dataframe(sektor_yoy)

    # SUBSEKTOR---------------------------------------------------------------------------
    st.subheader("🚧 SubSektor(under construction)🚧")
    data_subsektor = subsektor(filter, filter22)
    with chart_container(data_subsektor):
        nama_sektor = data_subsektor["NM_KATEGORI"].unique().tolist()
        tab_subsekstor = st.selectbox("Pilih Sektor:", nama_sektor)

        subsektor_df = data_subsektor[data_subsektor["NM_KATEGORI"] == tab_subsekstor]
        subsektor_table = subsektor_df.drop(columns=["NM_KATEGORI", "NAMA_KLU"])
        subsektor_table = subsektor_table.groupby("Sub Sektor").sum().reset_index()
        subsektor_table["Selisih"] = subsektor_table["2023"] - subsektor_table["2022"]
        subsektor_table["Tumbuh"] = (
            subsektor_table["Selisih"] / subsektor_table["2022"]
        ) * 100

        klu_df = subsektor_df.drop(columns=["NM_KATEGORI"])
        klu_df = klu_df.groupby("NAMA_KLU").sum().reset_index()
        klu_df["Selisih"] = klu_df["2023"] - klu_df["2022"]
        klu_df["Tumbuh"] = (klu_df["Selisih"] / klu_df["2022"]) * 100
        # # subsektor_df.loc[:,'2022']
        # colorscale = [[0, "#005FAC"], [0.5, "#f2e5ff"], [1, "#ffffff"]]
        # subsektor_df = ff.create_table(subsektor_df, colorscale=colorscale)

        st.dataframe(subsektor_table, use_container_width=True)
        st.dataframe(klu_df, use_container_width=True)
    # TUMBUH BULANAN-----------------------------------------------------------------------
    st.subheader("💡 Pertumbuhan Bulanan")
    tumbuh_bulanan = growth_month(filter, filter22)

    tumbuh_bulanan.reset_index(inplace=True)
    tumbuh_bulanan.rename(columns={"index": "Growth"}, inplace=True)

    tumbuh_bulanan.fillna(0, inplace=True)
    tumbuh_bulanan.iloc[:, 1:] = tumbuh_bulanan.iloc[:, 1:].applymap(
        lambda x: "{:,.2f}%".format(x)
    )

    with chart_container(tumbuh_bulanan):
        colorscale = [[0, "#2c5a7b"], [0.5, "#f2e5ff"], [1, "#ffffff"]]
        tumbuh = ff.create_table(tumbuh_bulanan, colorscale=colorscale)

        st.plotly_chart(tumbuh, use_container_width=True)
