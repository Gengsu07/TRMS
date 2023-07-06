import plotly.figure_factory as ff
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.app_logo import add_logo
from streamlit_extras.chart_container import chart_container
import calendar
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
from dateutil.relativedelta import relativedelta
from datetime import date
from datetime import datetime
import pandas as pd
from yaml.loader import SafeLoader
import yaml
import streamlit_authenticator as stauth
import streamlit as st
import random
from streamlit_toggle import st_toggle_switch
from streamlit_option_menu import option_menu
from math import ceil
import duckdb

st.set_page_config(
    page_title="Tax Revenue Monitoring Sistem",
    page_icon="assets\logo_djo.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)
from scripts.login import names, usernames
from scripts.db import (
    data_ket,
    target,
    sektor,
    klu,
    sektor_yoy,
    jns_pajak,
    kjs,
    kpi,
    linedata,
    naikturun,
    proporsi,
    cluster,
    data_sankey,
    generate_rgba_colors,
    top10kpp,
)
from scripts.db import (
    sektor_yoy,
    growth_month,
    subsektor,
    sankey_subsektor,
    generate_rgba_colors,
)
from scripts.filter_dataframe import filter_dataframe
cred = duckdb.connect('credentials.duckdb')
# settings

with open("style/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


conn = st.experimental_connection("ppmpkm", type="sql")


# Function/module
def credential():
    users = cred.execute('select * from credentials ').df()
    usernames = [user["NIP"] for user in users]
    names = [user["Nama"] for user in users]
    hashed_passwords = [user["PASS_HASHED"] for user in users]

    authenticator = stauth.Authenticate(
    names,
    usernames,
    hashed_passwords,
    'KilauJaktim@110','byGengsu@110',
    cookie_expiry_days=30)

    name, authentication_status, username = authenticator.login("👋Login-TRMS👋", "main")
    return name, authentication_status, username

def unique_key(seed: int):
    random.seed(seed)
    return random.choice(list(range(1, 1000)))


def n_color(df):
    # opacity_sankey = st.select_slider(
    #     "kecerahan",
    #     options=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
    #     value=0.5,
    # )
    n_color = generate_rgba_colors(len(df), 0.5)
    n_color = n_color["rgba"]
    return n_color


@st.cache_resource
def list_to_sql(column, value):
    value_str = ",".join([f"'{x}'" for x in value])
    sql_filter = f'"{column}" IN ({value_str})'
    return sql_filter


@st.cache_resource
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


def tumbuh_zerodev(x, y):
    if y:
        tumbuh_bruto = (x - y) / y
    elif x > 0:
        tumbuh_bruto = 1
    else:
        tumbuh_bruto = 0
    return tumbuh_bruto


def format_angka(value):
    cek = value / 1000
    if (cek > 1000000000) or (cek < -1000000000):  # >1 1T
        nominal = "{:,.3f}T".format(value / 1000000000000)
    elif (cek > 1000000) or (cek < -1000000):  # >1M
        nominal = "{:,.3f}M".format(value / 1000000000)
    elif (cek > 1000) or (cek < -1000):  # > 1Jt
        nominal = "{:,.3f}Jt".format(value / 1000000)
    else:
        nominal = "{:,.0f}".format(value)
    return nominal

def format_number(x):
    if x / 1000000000000 > 1:
        number = "{:,.1f}T".format(x / 1000000000000)
    elif x / 1000000000 > 1:
        number = "{:,.1f}M".format(x / 1000000000)
    else:
        number = "{:,.1f}Jt".format(x / 1000000)
    return number


# ---AUTHENTICATION-------------------------------------------------------
# with open(".streamlit/login.yaml") as file:
#     config = yaml.load(file, Loader=SafeLoader)

# names = names()
# usernames = usernames()
# names = passw.names()
# usernames = passw.usernames()
if "darkmode" not in st.session_state:
    st.session_state["darkmode"] = "off"


name, authentication_status, username = credential()
st.write(authentication_status)
if st.authentication_status == False:
    st.error("Username atau Password salah 🫢")
elif authentication_status == None:
    st.warning("Masukan username dan password yang sesuai")
elif authentication_status:
        # Sidebar----------------------------------------------------------------------------
        # Main apps-----------------------------------------------------------------------
        tabs = option_menu(None,['Dashboard','ALCo','AskData'],
                           icons=["bi bi-speedometer","bi bi-bar-chart","bi bi-messenger"],
                           menu_icon='cast', default_index=0, orientation='horizontal',
                           styles={
                            "container": {"padding": "3!important", "background-color": "#005fac","max-width":'2560px'},
                            "icon": {"color": "orange", "font-size": "14px"}, 
                            "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
                            "nav-link-selected": {"background-color": "#ffc91b"},
                            "menu-title" :{"background-color":"#018da2"},
    })
        if tabs == "Dashboard":
            colmain = st.columns([1, 4, 1])
            with colmain[0]:
                st.image("assets/unit.png", width=150)
                switch = st_toggle_switch(
                    label="Darkmode",
                    key="switch_1",
                    default_value=False,
                    label_after=False,
                    inactive_color="#D3D3D3",  # optional
                    active_color="#11567f",  # optional
                    track_color="#29B5E8",  # optional
                )

            with colmain[1]:
                st.header("Tax Revenue Monitoring Sistem🚀")
                st.text(f" Salam Satu Bahu: {name}")
            with colmain[2]:
                if st.session_state["authentication_status"]:
                    authenticator.logout("Logout", "main")

                if switch:
                    with open("style/darkmode.css") as f:
                        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
                    st.session_state["darkmode"] = "on"
                else:
                    st.session_state["darkmode"] = "off"

            # st.markdown(
            #     """<hr style="height:1px;border:none;color:#FFFFFF;background-color:#ffc91b;" /> """,
            #     unsafe_allow_html=True,
            # )
            col_filter = st.columns([1, 1, 1, 2, 2, 2, 2])
            with col_filter[0]:
                mindate = datetime.strptime("2023-01-01", "%Y-%m-%d")
                start = st.date_input("Tgl Mulai", min_value=mindate, value=mindate)
            with col_filter[1]:
                end = st.date_input("Tgl Akhir", max_value=date.today())
            with col_filter[2]:
                kpp = conn.query(
                    'select distinct "ADMIN" from ppmpkm where "ADMIN" notnull'
                )
                kpp = st.multiselect("KPP", options=kpp.iloc[:, 0].tolist())
            with col_filter[3]:
                map = conn.query('select distinct "MAP" from ppmpkm where "MAP" notnull')
                map = st.multiselect("MAP", options=map.iloc[:, 0].tolist())
            with col_filter[4]:
                sektor = conn.query(
                    'select distinct "NM_KATEGORI" from ppmpkm where "NM_KATEGORI" notnull'
                )
                sektor = st.multiselect("SEKTOR", options=sektor.iloc[:, 0].tolist())
            with col_filter[5]:
                segmen = conn.query(
                    """select distinct "SEGMENTASI_WP" from ppmpkm where "SEGMENTASI_WP" notnull and "SEGMENTASI_WP"!='' """
                )
                segmen = st.multiselect("SEGMENTASI", options=segmen.iloc[:, 0].tolist())
            with col_filter[6]:
                # wp
                wp = conn.query(
                    """select distinct "NAMA_WP" from ppmpkm where "NAMA_WP" notnull and "NAMA_WP"!=''
                    """
                )
                wp = st.multiselect("Wajib Pajak", wp["NAMA_WP"].tolist())

            # filterdata
            filter_gabungan = cek_filter(start, end, kpp, map, sektor, segmen, wp)
            filter = "and".join(x for x in filter_gabungan[0])
            filter_date = "and".join(x for x in filter_gabungan[0][:2])
            filter_date22 = "and".join(x for x in filter_gabungan[1][:2])
            filter_cat = "and".join(x for x in filter_gabungan[1][2:])
            filter22 = "and".join(x for x in filter_gabungan[1])

            # KPI-----------------------------------------------------------------------------------
            style_metric_cards(
                background_color="#FFFFFF",
                border_color="#005FAC",
                border_left_color="#005FAC",
            )
            data_kpi = kpi(filter, filter22, filter_date, filter_date22)
            data23, data22 = data_kpi
            col_tahun = st.columns(5)

            with col_tahun[0]:
                capaian = target(kpp)
                target2023, target2022 = capaian
                target2023 = sum(target2023.values())
                target2022 = sum(target2022.values())
                naik_target = ((target2023 - target2022) / target2022) * 100
                if (target2023 / 1000000000000) > 1:
                    st.metric(
                        "Target",
                        "{:,.2f}T".format(target2023 / 1000000000000),
                        delta="{:,.2f}%".format(naik_target),
                    )
                else:
                    st.metric(
                        "Target",
                        "{:,.2f}M".format(target2023 / 1000000000),
                        delta="{:,.2f}%".format(naik_target),
                    )
            with col_tahun[1]:
                bruto23 = data23["BRUTO"].sum()
                bruto22 = data22["BRUTO"].sum()

                tumbuh_bruto = tumbuh_zerodev(bruto23, bruto22)
                st.metric(
                    "Bruto",
                    format_angka(bruto23),
                    delta="{:,.2f}%".format(tumbuh_bruto * 100),
                )
            with col_tahun[2]:
                net23 = data23["NETTO"].sum()
                net22 = data22["NETTO"].sum()
                tumbuh_net = tumbuh_zerodev(net23, net22)
                st.metric(
                    "Netto",
                    format_angka(net23),
                    delta="{:,.2f}%".format(tumbuh_net * 100),
                )

            with col_tahun[3]:
                kontrib = data23["KONTRIBUSI"][0]
                if kontrib:
                    kontrib23 = (kontrib) * 100
                    kontrib22 = (kontrib) * 100
                    st.metric(
                        "Kontrib. Realisasi",
                        f"{kontrib23:,.2f}%",
                        delta=f"{kontrib23 - kontrib22:,.2f}%",
                    )
                else:
                    st.metric(
                        "Kontrib. Realisasi",
                        0,
                        delta=0,
                    )
            with col_tahun[4]:
                persentase23 = net23 / target2023
                persentase22 = net22 / target2022
                tumbuh_persen = persentase23 - persentase22
                st.metric(
                    "Capaian",
                    "{:.2f}%".format(persentase23 * 100),
                    delta="{:.2f}%".format(tumbuh_persen * 100),
                )
            # KET-----------------------------------------------------------------------
            ket = data_ket(filter, filter22).set_index("KET")

            colket = st.columns(5)
            with colket[0]:
                if "MPN" in ket.index:
                    # format_number = "{:,.1f}M" if ket.loc["MPN", "2023"] >= 0 else "{:,.1f}M"
                    # format_number_T = "{:,.1f}T" if ket.loc["MPN", "2023"] >= 0 else "{:,.1f}T"
                    st.metric(
                        "MPN",
                        format_angka(ket.loc["MPN", "2023"]),
                        delta=format_angka(ket.loc["MPN", "selisih"]),
                    )
                else:
                    st.metric("MPN", "0M")
            with colket[1]:
                if "SPM" in ket.index:
                    st.metric(
                        "SPM",
                        format_angka(ket.loc["SPM", "2023"]),
                        delta=format_angka(ket.loc["SPM", "selisih"]),
                    )
                else:
                    st.metric("SPM", "0.0M")
            with colket[2]:
                if "PBK KIRIM" in ket.index:
                    st.metric(
                        "PBK KIRIM",
                        format_angka(ket.loc["PBK KIRIM", "2023"]),
                        delta=format_angka(ket.loc["PBK KIRIM", "2023"]),
                    )
                else:
                    st.metric("PBK KIRIM", "0.0M")
            with colket[3]:
                if "PBK TERIMA" in ket.index:
                    st.metric(
                        "PBK TERIMA",
                        format_angka(ket.loc["PBK TERIMA", "2023"]),
                        delta=format_angka(ket.loc["PBK TERIMA", "selisih"]),
                    )
                else:
                    st.metric("PBK TERIMA", "0.0M")
            with colket[4]:
                if "SPMKP" in ket.index:
                    st.metric(
                        "SPMKP",
                        format_angka(ket.loc["SPMKP", "2023"]),
                        delta=format_angka(ket.loc["SPMKP", "selisih"]),
                    )
                else:
                    st.metric("SPMKP", "0.0M")
            with st.expander("keterangan"):
                keterangan = """
                - Target : Per KPP, atau sesuai KPP yang dipilih, atau Kanwil
                - Bruto : Penerimaan tanpa SPMKP/Restitusi
                - Netto : Semua Penerimaan
                - Kontrib. Realisasi : Kontribusi Realisasi per Total Realisasi Kanwil DJP Jakarta Timur
                - Capaian : Per KPP, atau KPP yg dipilih
                """
                st.markdown(keterangan)
            # st.markdown(
            #     """<hr style="height:1px;border:none;color:#FFFFFF;background-color:#ffc91b;" /> """,
            #     unsafe_allow_html=True,
            # )

            # linechart--------------------

            try:
                linedata = linedata(filter, filter22)
                linedata = (
                    linedata.groupby(["TAHUNBAYAR", "BULANBAYAR"])["sum"]
                    .sum()
                    .reset_index()
                )
                linedata["text"] = linedata["sum"].apply(lambda x: format_angka(x))

                linedata23 = linedata[linedata["TAHUNBAYAR"] == "2023"]

                linedata23["kumulatif"] = linedata23["sum"].cumsum()
                linedata23["capaian_kumulatif"] = (
                    linedata23["kumulatif"] / 27601733880000
                ) * 100

                linedata22 = linedata[linedata["TAHUNBAYAR"] == "2022"]
                linedata22["kumulatif"] = linedata22["sum"].cumsum()
                linedata22["capaian_kumulatif"] = (
                    linedata22["kumulatif"] / 22656373555000
                ) * 100
                linedata = pd.concat([linedata23, linedata22], axis=0, ignore_index=True)

                linechart = px.bar(
                    data_frame=linedata,
                    x="BULANBAYAR",
                    y="sum",
                    color="TAHUNBAYAR",
                    text="text",
                    height=380,
                    barmode="group",
                    custom_data=["TAHUNBAYAR"],
                )

                hovertemplate = (
                    "<b>%{x}</b><br><br>"
                    + "NOMINAL: %{text} <br>"
                    + "TAHUNBAYAR: %{customdata[0]} <extra></extra>"
                )
                linechart.update_traces(hovertemplate=hovertemplate)
                linechart.update_layout(
                    xaxis_title="",
                    yaxis_title="",
                    yaxis={"visible": False},
                    xaxis={
                        "tickmode": "array",
                        "tickvals": [x for x in range(1, 13)],
                        "ticktext": [calendar.month_name[i] for i in range(1, 13)],
                        # "tickfont": {"color": "#fff"},
                    },
                    paper_bgcolor="rgba(0, 0, 0, 0)",
                    plot_bgcolor="rgba(0, 0, 0, 0)",
                    autosize=True,
                )
                line = px.line(
                    linedata,
                    x="BULANBAYAR",
                    y=linedata["capaian_kumulatif"],
                    color="TAHUNBAYAR",
                    text=linedata["capaian_kumulatif"].apply(
                        lambda x: "{:,.2f}%".format(x)
                    ),
                    height=380,
                    color_discrete_sequence=["#ffc91b", "#005FAC"],
                    markers=True,
                    custom_data=[
                        "TAHUNBAYAR",
                        linedata["kumulatif"].apply(lambda x: format_angka(x)),
                    ],
                )
                hovertemplate = (
                    "<b>%{x}</b><br><br>"
                    + "TAHUNBAYAR: %{customdata[0]} <br>"
                    + "KUMULATIF: %{customdata[1]} <br><extra></extra>"
                )
                line.update_traces(hovertemplate=hovertemplate)
                line.update_layout(
                    xaxis_title="",
                    yaxis_title="",
                    yaxis={"visible": False},
                    xaxis={
                        "tickmode": "array",
                        "tickvals": [x for x in range(1, 13)],
                        "ticktext": [calendar.month_name[i] for i in range(1, 13)],
                        # "tickfont": {"color": "#fff"},
                    },
                    paper_bgcolor="rgba(0, 0, 0, 0)",
                    plot_bgcolor="rgba(0, 0, 0, 0)",
                    autosize=True,
                )
                with chart_container(linedata):
                    timeseries = st.columns(2)
                    with timeseries[0]:
                        st.plotly_chart(linechart, use_container_width=True)
                    with timeseries[1]:
                        st.plotly_chart(line, use_container_width=True)
            except:
                st.subheader("🪂No Data Available🪂")

            # ----------------------------------------------------------------------------------------------
            data_sankey, data_node = data_sankey(filter)
            label = ["<b>" + label + "</b>" for label in data_node["label"].tolist()]
            sankey_chart = go.Figure(
                data=[
                    go.Sankey(
                        node=dict(
                            pad=15,
                            thickness=20,
                            line=dict(color="blue", width=0.5),
                            label=label,
                            color=n_color(data_sankey),
                        ),
                        link=dict(
                            source=data_sankey["source"],
                            target=data_sankey["target"],
                            value=data_sankey["value"],
                            color=n_color(data_sankey),
                        ),
                        valueformat=".2s",
                    )
                ]
            )
            sankey_chart.update_layout(
                height=860,
                title=dict(
                    text="Sebaran Penerimaan Sektor ke Jenis Pajak",
                    font=dict(color="slategrey", size=26),
                    x=0.3,
                    y=0.95,
                ),
                paper_bgcolor="rgba(0, 0, 0, 0)",
                plot_bgcolor="rgba(0, 0, 0, 0)",
            )
            with chart_container(data_sankey):
                st.plotly_chart(sankey_chart, use_container_width=True)

            # PERSEKTOR-------------------------------------------------------------------------------
            try:
                data_sektor_awal = sektor_yoy(filter, filter22, includewp=False)
                data_sektor = data_sektor_awal[0]

                sektor23 = go.Bar(
                    x=data_sektor["BRUTO2023"] / 1000000000,
                    y=data_sektor["NM_KATEGORI"],
                    customdata=["text23"],
                    name="2023",
                    orientation="h",
                    text=data_sektor["kontrib2023"],
                    texttemplate="%{x:,.2f}M <br> (%{text})",
                    textposition="auto",
                    marker=dict(color="#005FAC"),
                    textangle=0,
                    base=0,
                )

                sektor22 = go.Bar(
                    x=data_sektor["BRUTO2022"] / 1000000000,
                    y=data_sektor["NM_KATEGORI"],
                    name="2022",
                    orientation="h",
                    text=data_sektor["kontrib2022"],
                    textposition="auto",
                    texttemplate="%{x:,.2f}M<br> (%{text})",
                    marker=dict(color="#ffc91b"),
                    textangle=0,
                    base=0,
                )
                sektor_data = [sektor22, sektor23]
                sektor_layout = go.Layout(
                    barmode="group",
                    height=860,
                    bargap=0.1,
                    xaxis=dict(visible=False),
                    title=dict(
                        text="Per Sektor (Bruto)",
                        font=dict(color="slategrey", size=26),
                        x=0.5,
                        y=0.95,
                    ),
                    showlegend=True,
                    font=dict(
                        family="Arial",
                        size=14,
                        color="slategrey",
                    ),
                    legend=dict(font=dict(color="slategray")),
                    paper_bgcolor="rgba(0, 0, 0, 0)",
                    plot_bgcolor="rgba(0, 0, 0, 0)",
                )
                sektor_chart = go.Figure(data=sektor_data, layout=sektor_layout)

                # sektor_bar.update_xaxes(visible=False)

                # kontribusi_bar = go.Bar(
                #     x=data_sektor["kontribusi"],
                #     y=data_sektor["NM_KATEGORI"],
                #     name="kontribusi",
                #     orientation="h",
                #     text=data_sektor["kontrib_persen"],
                #     textposition="auto",
                #     marker=dict(color="#499894"),
                #     textangle=0,
                #     base=0,
                #     showlegend=False,
                # )
                # kontrib_layout = go.Layout()
                # kontribusi_chart = go.Figure(data=kontribusi_bar, layout=kontrib_layout)

                # kontribusi_chart.update_xaxes(visible=False)
                sektor_chart.update_xaxes(showticklabels=True)  # autorange="reversed"
                sektor_chart.update_yaxes(
                    showticklabels=True, griddash="dot", gridcolor="slategrey"
                )  # autorange="reversed"
                with chart_container(data_sektor):
                    st.plotly_chart(sektor_chart, use_container_width=True)
            except:
                st.subheader("🪂 No Data Available🪂")
                # data
            try:
                data_sektor_table = sektor_yoy(filter, filter22, includewp=True)[2]
                data_sektor_table = data_sektor_table[
                    [
                        "NAMA_WP",
                        "NM_KATEGORI",
                        "BRUTO2022",
                        "BRUTO2023",
                        "NETTO2022",
                        "NETTO2023",
                        "NaikBruto",
                        "NaikNetto",
                        "TumbuhBruto",
                    ]
                ]

                with chart_container(data_sektor_table):
                    st.dataframe(
                        filter_dataframe(data_sektor_table, key=unique_key(5)),
                        use_container_width=True,
                        hide_index=True,
                    )

                klu_data = klu(filter)
                klu = klu_data.copy()
                klu["BRUTO_M"] = klu["BRUTO"] / 1000000000
                klu["Kontribusi"] = ((klu["BRUTO"] / klu["BRUTO"].sum()) * 100).apply(
                    lambda x: "{:,.2f}%".format(x)
                )
                kluchart = px.treemap(
                    klu,
                    labels="NAMA_KLU",
                    values="BRUTO_M",
                    path=["NAMA_KLU"],
                    color="NM_KATEGORI",
                    color_discrete_sequence=px.colors.qualitative.Safe,
                    height=560,
                    custom_data=["Kontribusi"],
                    title="Proporsi Penerimaan per KLU",
                )
                kluchart.update_traces(
                    hovertemplate="<b>%{label}</b>(%{customdata[0]})<br><br>"
                    + "NAMA KLU: %{id}<br>"
                    + "BRUTO: %{value:,.1f}M <extra></extra>"
                )

                kluchart.update_layout(
                    paper_bgcolor="rgba(0, 0, 0, 0)",
                    plot_bgcolor="rgba(0, 0, 0, 0)",
                    xaxis_title="",
                    yaxis_title="",
                    title=dict(
                        text="Proporsi Klasifikasi Lapangan Usaha (Bruto)",
                        font=dict(color="slategrey", size=26),
                        x=0.5,
                        y=0.95,
                    ),
                )
                with chart_container(klu_data.sort_values(by="BRUTO", ascending=False)):
                    st.plotly_chart(kluchart, use_container_width=True)

                st.markdown(
                    """<hr style="height:1px;border:none;color:#FFFFFF;background-color:#ffc91b;" /> """,
                    unsafe_allow_html=True,
                )
                # JENIS PAJAK----------------------------------------------------------------------------------------
                jenis_pajak, jenis_pajak9 = jns_pajak(filter, filter22, includewp=False)

                jenis_pajak9 = jenis_pajak9.sort_values(by="BRUTO2023", ascending=True)
                mapbar23 = go.Bar(
                    x=jenis_pajak9["BRUTO2023"] / 1000000000,
                    y=jenis_pajak9["MAP"],
                    name="2023",
                    orientation="h",
                    text=jenis_pajak9["KONTRIBUSI2023"],
                    texttemplate="%{x:,.1f}M (%{text})%",
                    textposition="outside",
                    marker=dict(color="#005FAC"),  # ffc91b
                    width=0.5,
                )

                mapbar22 = go.Bar(
                    x=jenis_pajak9["BRUTO2022"] / 1000000000,
                    y=jenis_pajak9["MAP"],
                    name="2022",
                    orientation="h",
                    text=jenis_pajak9["KONTRIBUSI2022"],
                    texttemplate="%{x:,.1f}M (%{text}%)",
                    textposition="auto",
                    base=0,
                    marker=dict(color="#ffc91b"),  # ffc91b
                    width=0.5,
                )
                data_map = [mapbar22, mapbar23]
                map_layout = go.Layout(
                    barmode="group",
                    height=820,
                    xaxis=dict(visible=False),
                    # yaxis=dict(tickfont=dict(color="#fff")),
                    title=dict(
                        text="Per Jenis(Bruto)",
                        # font=dict(color="#4d5b69"),
                        x=0.5,
                        y=0.95,
                        font=dict(size=26, color="slategrey"),
                    ),
                    showlegend=True,
                    bargap=0.2,
                    font=dict(
                        family="Arial",
                        size=12,
                        color="slategrey",
                    ),
                    paper_bgcolor="rgba(0, 0, 0, 0)",
                    plot_bgcolor="rgba(0, 0, 0, 0)",
                )
                mapchart = go.Figure(data=data_map, layout=map_layout)

                with chart_container(jenis_pajak9):
                    st.plotly_chart(mapchart, use_container_width=True)

                jenis_wp, *_ = jns_pajak(filter, filter22, includewp=True)
                with chart_container(jenis_wp.reset_index()):
                    # jenis_pajak = jenis_pajak[
                    #     ["NAMA_WP", "MAP", "TAHUNBAYAR", "JENIS_WP","2022", "KONTRIBUSI2022", "2023", "KONTRIBUSI2023", "TUMBUH"]
                    # ]
                    st.dataframe(
                        filter_dataframe(jenis_wp, key=unique_key(45)),
                        use_container_width=True,
                        hide_index=True,
                    )

                kjs = kjs(filter)
                kjs["BRUTO_M"] = kjs["BRUTO"] / 1000000000
                kjs["Kontribusi"] = (kjs["BRUTO"] / kjs["BRUTO"].sum()) * 100
                kjschart = px.treemap(
                    kjs,
                    labels="KDBAYAR",
                    values="BRUTO_M",
                    path=["KDBAYAR"],
                    color="MAP",
                    color_discrete_sequence=px.colors.qualitative.Safe,
                    height=560,
                    custom_data=["Kontribusi"],
                    title="Proporsi Penerimaan per Kode Jenis Setoran",
                )
                hovertemplate = (
                    "<b>%{label}</b><br><br>"
                    + "KDBAYAR: %{id}<br>"
                    + "%{customdata[0]:,.2f} persen<br>"
                    + "BRUTO: %{value:,.1f}M <extra></extra>"
                )
                kjschart.update_traces(hovertemplate=hovertemplate)

                kjschart.update_layout(
                    paper_bgcolor="rgba(0, 0, 0, 0)",
                    plot_bgcolor="rgba(0, 0, 0, 0)",
                    xaxis_title="",
                    yaxis_title="",
                    title=dict(
                        font=dict(color="slategrey", size=26),
                        x=0.5,
                        y=0.95,
                    ),
                )
                with chart_container(kjs):
                    st.plotly_chart(kjschart, use_container_width=True)

                st.markdown(
                    """<hr style="height:1px;border:none;color:#FFFFFF;background-color:#ffc91b;" /> """,
                    unsafe_allow_html=True,
                )
            except:
                st.subheader("🪂 No Data Available🪂")

            # TOP10-----------------------------------------------------------------------------------

            try:
                topwp, botwp = naikturun(filter, filter22)

                topwp.iloc[:, 2:] = (topwp.iloc[:, 2:] / 1000000000).applymap(
                    lambda x: "{:,.1f}".format(x)
                )

                botwp.iloc[:, 2:] = (botwp.iloc[:, 2:] / 1000000000).applymap(
                    lambda x: "{:,.1f}".format(x)
                )

                with st.container():
                    tab_wp = st.tabs(["Top 10 WP", "Top 10 Tumbuh", "Bottom 10 WP Tumbuh"])
                    with tab_wp[0]:
                        data_proporsi, bruto = proporsi(filter)
                        data_proporsi["text"] = data_proporsi["BRUTO"].apply(
                            lambda x: format_angka(x)
                        )
                        # data_proporsi["uraian"] = (
                        #     data_proporsi["text"] + "<br>" + str(data_proporsi["KONTRIBUSI"])
                        # )
                        with chart_container(data_proporsi):
                            # PROPORSI--------------------------------------------------------------------
                            row = len(data_proporsi) - 5
                            data_proporsi = data_proporsi.iloc[:row,]
                            proporsi_chart = go.Figure(
                                go.Funnel(
                                    y=data_proporsi["NAMA_WP"],
                                    x=data_proporsi["BRUTO"] / 1000000000,
                                    textposition="inside",
                                    # textinfo="value+percent initial",
                                    text=data_proporsi["KONTRIBUSI"],
                                    texttemplate="%{x:,.2f}M <br> %{text:.2f}%",
                                    opacity=1,
                                    marker={
                                        "color": [
                                            "#005fac",
                                            "#1473af",
                                            "#2888b1",
                                            "#3a9db4",
                                            "#4cb3b7",
                                            "#5ec8ba",
                                            "#70debd",
                                            "#82f3c0",
                                            "#95f8c3",
                                            "#a9fed0",
                                        ],
                                        "line": {
                                            "width": [4, 2, 2, 3, 1, 1],
                                            "color": ["white"] * 10,
                                        },
                                    },
                                    connector={
                                        "line": {
                                            "color": "royalblue",
                                            "dash": "dot",
                                            "width": 3,
                                        }
                                    },
                                )
                            )
                            proporsi_chart.update_layout(
                                height=820,
                                title=dict(
                                    text="10 WP Terbesar Bruto",
                                    x=0.5,
                                    y=0.95,
                                    font=dict(size=26, color="slategrey"),
                                ),
                                paper_bgcolor="rgba(0, 0, 0, 0)",
                                plot_bgcolor="rgba(0, 0, 0, 0)",
                            )
                            st.plotly_chart(proporsi_chart, use_container_width=True)
                        with chart_container(bruto):
                            st.dataframe(
                                filter_dataframe(bruto, key=unique_key(23)),
                                use_container_width=True,
                                hide_index=True,
                            )
                    with tab_wp[1]:
                        with chart_container(topwp):
                            table_top = go.Figure(
                                data=[
                                    go.Table(
                                        columnorder=[1, 2, 3, 4, 5],
                                        columnwidth=[40, 100, 30, 30, 30],
                                        header=dict(
                                            values=[
                                                ["<b>NPWP</b>"],
                                                ["<b>NAMA WP</b>"],
                                                ["<b>2022(M)</b>"],
                                                ["<b>2023(M)</b>"],
                                                ["<b>SELISIH(M)</b>"],
                                            ],
                                            fill_color="#005FAC",
                                            line_color="gray",
                                            align=[
                                                "center",
                                                "center",
                                                "center",
                                                "center",
                                                "center",
                                            ],
                                            font=dict(color="white", size=16),
                                            height=40,
                                        ),
                                        cells=dict(
                                            values=[topwp[x] for x in topwp.columns],
                                            fill=dict(
                                                color=[
                                                    "paleturquoise",
                                                    "paleturquoise",
                                                    "white",
                                                    "white",
                                                    "white",
                                                ]
                                            ),
                                            line_color="darkslategray",
                                            align=[
                                                "left",
                                                "left",
                                                "center",
                                                "center",
                                                "center",
                                            ],
                                            font_size=14,
                                            height=30,
                                        ),
                                    )
                                ]
                            )
                            table_top.update_layout(
                                height=640,
                                width=960,
                                title=dict(
                                    text="10 Tumbuh Terbesar Bruto",
                                    x=0.5,
                                    y=0.95,
                                    font=dict(size=26, color="slategrey"),
                                ),
                            )
                            st.plotly_chart(table_top, use_container_width=True)
                    with tab_wp[2]:
                        table_bot = go.Figure(
                            data=[
                                go.Table(
                                    columnorder=[1, 2, 3, 4, 5],
                                    columnwidth=[40, 100, 30, 30, 30],
                                    header=dict(
                                        values=[
                                            ["<b>NPWP</b>"],
                                            ["<b>NAMA WP</b>"],
                                            ["<b>2022(M)</b>"],
                                            ["<b>2023(M)</b>"],
                                            ["<b>SELISIH(M)</b>"],
                                        ],
                                        fill_color="#f07167",
                                        line_color="gray",
                                        align=[
                                            "center",
                                            "center",
                                            "center",
                                            "center",
                                            "center",
                                        ],
                                        font=dict(color="white", size=16),
                                        height=40,
                                    ),
                                    cells=dict(
                                        values=[botwp[x] for x in botwp.columns],
                                        fill=dict(
                                            color=[
                                                "#fbc4ab",
                                                "#fbc4ab",
                                                "white",
                                                "white",
                                                "white",
                                            ]
                                        ),
                                        line_color="gray",
                                        align=[
                                            "left",
                                            "left",
                                            "center",
                                            "center",
                                            "center",
                                        ],
                                        font_size=14,
                                        height=30,
                                    ),
                                )
                            ]
                        )
                        table_bot.update_layout(
                            height=640,
                            width=1024,
                            title=dict(
                                text="10 Tumbuh Terendah Bruto",
                                x=0.5,
                                y=0.95,
                                font=dict(size=26, color="slategrey"),
                            ),
                        )
                        with chart_container(botwp):
                            st.plotly_chart(table_bot, use_container_width=True)
            except:
                st.subheader("🪂 No Data Available🪂")
                # CLUSTER KPP ------------------------------------------------------------------------------------
            try:
                capaian = cluster(filter, filter22, kpp)
                capaian_table = capaian.copy()
                capaian_table.loc[:, "TARGET2023":"REALISASI2023"] = capaian_table.loc[
                    :, "TARGET2023":"REALISASI2023"
                ].applymap(lambda x: "{:,.2f}M".format(x / 1000000000))
                capaian_table.loc[:, "capaian":] = capaian_table.loc[
                    :, "capaian":
                ].applymap(lambda x: "{:,.2f}%".format(x))
                # capaian_table = ff.create_table(capaian_table)
                avg_capaian = capaian["capaian"].mean()
                avg_tumbuh = capaian["tumbuh"].mean()

                cluster_chart = px.scatter(
                    capaian,
                    x="capaian",
                    y="tumbuh",
                    text="ADMIN",
                    color_continuous_scale=px.colors.diverging.RdBu,
                )
                hovertemplate = (
                    "<b>%{text}</b><br><br>"
                    + "Capaian: %{x:,.2f}persen <br>"
                    + "Tumbuh: %{y:,.2f}persen <extra></extra>"
                )
                cluster_chart.update_traces(
                    marker=dict(size=20, color="#F86F03"),
                    textposition="bottom center",
                    textfont=dict(color="#F86F03", size=14),
                    hovertemplate=hovertemplate,
                )
                cluster_chart.add_hline(
                    y=avg_tumbuh, line_dash="dash", line_color="red", name="Rata2 Tumbuh"
                )
                cluster_chart.add_vline(
                    x=avg_capaian, line_dash="dash", line_color="red", name="Rata2 Capaian"
                )
                cluster_chart.add_trace(
                    go.Scatter(
                        x=[avg_capaian],
                        y=[avg_tumbuh],
                        mode="markers",
                        marker=dict(color="green", symbol="x", size=20),
                        name="Rata-rata",
                    )
                )
                cluster_chart.update_layout(
                    title=dict(
                        text="Clustering Capaian & Tumbuh Unit Kerja(Bruto)",
                        font=dict(color="slategrey", size=26),
                        x=0.3,
                        y=0.95,
                    ),
                    # paper_bgcolor="#F6FFF8",
                    plot_bgcolor="rgba(0, 0, 0, 0)",
                )
                with chart_container(capaian_table):
                    st.plotly_chart(cluster_chart, use_container_width=True)
            except:
                st.subheader("🪂 No Data Available🪂")

            top10kpp = top10kpp(filter_date, filter_date22, filter_cat)
            top10kpp = top10kpp[~top10kpp["ADMIN"].isin(["007", "097"])]
            avg_realisasi = top10kpp["CY"].mean()
            avg_tumbuh_kpp = top10kpp["TUMBUH"].mean()
            cluster_top10kpp = px.scatter(
                top10kpp,
                x="CY",
                y="TUMBUH",
                # text="NAMA_WP",
                color="ADMIN",
                color_continuous_scale=px.colors.diverging.RdBu,
                custom_data=["NAMA_WP", "PY"],
            )
            hovertemplate = (
                "<b>%{customdata[0]}</b><br><br>"
                + "Current Year: %{x:,.0f} <br>"
                + "Prior Year: %{customdata[1]:,.0f}<br>"
                + "Tumbuh: %{y:,.2f}persen <extra></extra>"
            )
            cluster_top10kpp.update_traces(
                marker=dict(size=10),
                textposition="bottom center",
                textfont=dict(color="#F86F03", size=14),
                hovertemplate=hovertemplate,
            )
            cluster_top10kpp.add_hline(
                y=avg_tumbuh_kpp, line_dash="dash", line_color="red", name="Rata2 Tumbuh"
            )
            cluster_top10kpp.add_vline(
                x=avg_realisasi, line_dash="dash", line_color="red", name="Rata2 Capaian"
            )
            cluster_top10kpp.add_trace(
                go.Scatter(
                    x=[avg_realisasi],
                    y=[avg_tumbuh_kpp],
                    mode="markers",
                    marker=dict(color="green", symbol="x", size=20),
                    name="Rata-rata",
                )
            )
            cluster_top10kpp.update_layout(
                title=dict(
                    text="Clustering 10 WP Besar per KPP Pratama(Bruto)",
                    font=dict(color="slategrey", size=26),
                    x=0.3,
                    y=0.95,
                ),
                xaxis={"visible": False},
                yaxis={"visible": False},
                # paper_bgcolor="#F6FFF8",
                plot_bgcolor="rgba(0, 0, 0, 0)",
            )

            with chart_container(top10kpp):
                st.plotly_chart(cluster_top10kpp, use_container_width=True)

    # ALCO=============================================================================================================================
        elif tabs == "ALCo":
            colmain = st.columns([1, 4, 1])
            with colmain[0]:
                st.image("assets/unit.png", width=150)
            with colmain[1]:
                st.header("Tax Revenue Monitoring Sistem🚀")
                name = st.session_state["name"]
                st.text(f" Salam Satu Bahu: {name}")
            with colmain[2]:
                st.image("assets/unit.png", width=150)

            col_filter = st.columns([1, 1, 1, 2, 2, 2, 2])
            with col_filter[0]:
                mindate = datetime.strptime("2023-01-01", "%Y-%m-%d")
                start = st.date_input("Tgl Mulai", min_value=mindate, value=mindate)
            with col_filter[1]:
                end = st.date_input("Tgl Akhir", max_value=date.today())
            with col_filter[2]:
                kpp = conn.query(
                    'select distinct "ADMIN" from ppmpkm where "ADMIN" notnull'
                )
                kpp = st.multiselect("KPP", options=kpp.iloc[:, 0].tolist())
            with col_filter[3]:
                map = conn.query('select distinct "MAP" from ppmpkm where "MAP" notnull')
                map = st.multiselect("MAP", options=map.iloc[:, 0].tolist())
            with col_filter[4]:
                sektor = conn.query(
                    'select distinct "NM_KATEGORI" from ppmpkm where "NM_KATEGORI" notnull'
                )
                sektor = st.multiselect("SEKTOR", options=sektor.iloc[:, 0].tolist())
            with col_filter[5]:
                segmen = conn.query(
                    """select distinct "SEGMENTASI_WP" from ppmpkm where "SEGMENTASI_WP" notnull and "SEGMENTASI_WP"!='' """
                )
                segmen = st.multiselect("SEGMENTASI", options=segmen.iloc[:, 0].tolist())
            with col_filter[6]:
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
            style_metric_cards(
                background_color="rgba(0,0,0,0)",
                border_color="rgba(0,0,0,0)",
                border_left_color="rgba(0,0,0,0)",
            )
            urutan = st.selectbox(
                "Urut Berdasarkan:",
                options=["BRUTO2023", "BRUTO2022", "NETTO2023", "NETTO2022", "TumbuhBruto"],
            )
            # SEKTORRRR CARD
            sektor = sektor_yoy(filter, filter22, includewp=False)
            *_, sektor_mom, sektor_yoy = sektor

            sektor_yoy["%kontribusi"] = (
                sektor_yoy["BRUTO2023"] / sektor_yoy["BRUTO2023"].sum()
            ) * 100

            sektor_yoy1 = sektor_yoy[~sektor_yoy["NM_KATEGORI"].isin(["KLU ERROR", " "])]
            sektor_yoy["Rank"] = sektor_yoy[f"{urutan}"].rank(ascending=False)

            sektor_plus = sektor_yoy1[sektor_yoy1["NaikBruto"] > 0]
            sektor_plus["Rank"] = sektor_plus[f"{urutan}"].rank(ascending=False)
            sektor_plus.set_index("Rank", inplace=True)
            sektor_min = sektor_yoy1[sektor_yoy1["NaikBruto"] < 0]
            sektor_min["Rank"] = sektor_min[f"{urutan}"].rank(ascending=False)
            sektor_min.set_index("Rank", inplace=True)

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
                                    sektor_mom_select.groupby("BULANBAYAR")
                                    .sum()
                                    .reset_index()
                                )
                                # sektor_mom_select = sektor_mom_select.melt(
                                #     id_vars="BULANBAYAR", value_name="NOMINAL", var_name="JENIS"
                                # )
                                # st.dataframe(sektor_mom_select)
                                spark = px.line(
                                    sektor_mom_select,
                                    x="BULANBAYAR",
                                    y=["BRUTO2023", "BRUTO2022"],
                                    markers=True,
                                    height=100,
                                    width=200,
                                    # color_discrete_sequence=["#ffc91b", "#005FAC"],
                                )

                                spark.update_layout(
                                    template=None,
                                    xaxis_title="",
                                    yaxis_title="",
                                    yaxis={"visible": False, "showticklabels": False},
                                    xaxis={"visible": False, "showticklabels": False},
                                    margin=dict(l=0, r=0, t=0, b=0),
                                    paper_bgcolor="rgba(0, 0, 0, 0)",
                                    plot_bgcolor="rgba(0, 0, 0, 0)",
                                    autosize=True,
                                    showlegend=False,
                                )
                                st.plotly_chart(spark, use_container_width=True)
                                st.metric(
                                    data_col.loc[counter, "NM_KATEGORI"],
                                    value=format_number(data_col.loc[counter, "BRUTO2023"]),
                                    delta="{:,.2f}%".format(
                                        data_col.loc[counter, "TumbuhBruto"]
                                    ),
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
                                    sektor_mom_select.groupby("BULANBAYAR")
                                    .sum()
                                    .reset_index()
                                )
                                # sektor_mom_select = sektor_mom_select.melt(
                                #     id_vars="BULANBAYAR", value_name="NOMINAL"
                                # )

                                spark = px.line(
                                    sektor_mom_select,
                                    x="BULANBAYAR",
                                    y=["BRUTO2023", "BRUTO2022"],
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
                                    value=format_number(data_col.loc[counter, "BRUTO2023"]),
                                    delta="{:,.2f}%".format(
                                        data_col.loc[counter, "TumbuhBruto"]
                                    ),
                                )
                            counter += 1

            with st.expander("Detail Data"):
                sektor_yoy.sort_values(by="Rank", ascending=True, inplace=True)
                with chart_container(sektor_yoy):
                    st.dataframe(sektor_yoy)

            # SUBSEKTOR---------------------------------------------------------------------------
            st.subheader("🔭SubSektor🩺")
            data_subsektor = subsektor(filter, filter22)

            with chart_container(data_subsektor):
                nama_sektor = data_subsektor["NM_KATEGORI"].unique().tolist()
                tab_subsekstor = st.selectbox("Pilih Sektor:", nama_sektor)
                if tab_subsekstor:
                    subsektor_df = data_subsektor[
                        data_subsektor["NM_KATEGORI"] == tab_subsekstor
                    ]
                else:
                    subsektor_df = data_subsektor.copy()

                node_subsektor, sankey_subsektor = sankey_subsektor(
                    subsektor_df, tab_subsekstor
                )

                sankey_subsektor.drop(columns="NAMA_KLU", inplace=True)
                sankey_subsektor = sankey_subsektor[sankey_subsektor["NM_KATEGORI"] != ""]
                # sankey_subsektor = (
                #     sankey_subsektor.groupby(["NM_KATEGORI", "Sub Sektor"]).sum().reset_index()
                # )

                sankey_subsektor_chart = go.Figure(
                    data=[
                        go.Sankey(
                            node=dict(
                                pad=15,
                                thickness=20,
                                line=dict(color="blue", width=0.5),
                                label=node_subsektor["label"],
                                color=n_color(sankey_subsektor),
                            ),
                            link=dict(
                                source=sankey_subsektor["source"],
                                target=sankey_subsektor["target"],
                                value=sankey_subsektor["2023"],
                                color=n_color(sankey_subsektor),
                            ),
                            valueformat=".2s",
                        )
                    ]
                )
                sankey_subsektor_chart.update_layout(
                    height=860,
                    title=dict(
                        text="Sebaran Penerimaan Sektor ke Subsektor",
                        font=dict(color="slategrey", size=26),
                        x=0.3,
                        y=0.95,
                    ),
                    paper_bgcolor="rgba(0, 0, 0, 0)",
                    plot_bgcolor="rgba(0, 0, 0, 0)",
                )
                with chart_container(subsektor_df):
                    st.plotly_chart(sankey_subsektor_chart, use_container_width=True)

                subsektor_table = subsektor_df.drop(columns=["NM_KATEGORI", "NAMA_KLU"])
                subsektor_table = subsektor_table.groupby("Sub Sektor").sum().reset_index()
                subsektor_table["Selisih"] = (
                    subsektor_table["2023"] - subsektor_table["2022"]
                )
                subsektor_table["Tumbuh"] = (
                    subsektor_table["Selisih"] / subsektor_table["2022"]
                ) * 100

                klu_df = subsektor_df.drop(columns=["NM_KATEGORI", "Sub Sektor"])
                klu_df = klu_df.groupby("NAMA_KLU").sum().reset_index()
                klu_df["Selisih"] = klu_df["2023"] - klu_df["2022"]
                klu_df["Tumbuh"] = (klu_df["Selisih"] / klu_df["2022"]) * 100
                # # subsektor_df.loc[:,'2022']
                # colorscale = [[0, "#005FAC"], [0.5, "#f2e5ff"], [1, "#ffffff"]]
                # subsektor_df = ff.create_table(subsektor_df, colorscale=colorscale)

                st.dataframe(subsektor_table, use_container_width=True, hide_index=True)
                st.dataframe(klu_df, use_container_width=True, hide_index=True)
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
                colorscale = [[0, "#005fac"], [0.5, "#f2e5ff"], [1, "#ffffff"]]
                tumbuh = ff.create_table(tumbuh_bulanan, colorscale=colorscale)

                st.plotly_chart(tumbuh, use_container_width=True)
