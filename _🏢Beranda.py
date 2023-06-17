import importlib
import altair as alt
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


st.set_page_config(
    page_title="Tax Revenue Monitoring Sistem",
    page_icon="assets\logo_djo.png",
    layout="wide",
)

prep = importlib.import_module("db")
passw = importlib.import_module("login")

# settings

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


conn = st.experimental_connection("ppmpkm", type="sql")

# Function/module


def list_to_sql(column, value):
    value_str = ",".join([f"'{x}'" for x in value])
    sql_filter = f'"{column}" IN ({value_str})'
    return sql_filter


def cek_filter(start, end, kpp, map, sektor, segmen):
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
    return [filter_gabungan, filter_gabungan22]


def data_ket(filter, filter22):
    ket = conn.query(
        f"""select p."KET",abs(
    sum(case when p."TAHUNBAYAR" =2023 then p."NOMINAL" end )) as "2023"
    from ppmpkm p
    where {filter}
    GROUP BY p."KET"     """
    )

    ket22 = conn.query(
        f"""select p."KET",abs(
    sum(case when p."TAHUNBAYAR" =2022 then p."NOMINAL" end )) as "2022"
    from ppmpkm p
    where {filter22}
    GROUP BY p."KET"     """
    )
    ketgab = ket.merge(ket22, on="KET", how="left")
    ketgab["selisih"] = ketgab["2023"] - ketgab["2022"]
    return ketgab


# ---AUTHENTICATION-------------------------------------------------------
with open(".streamlit/login.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

names = passw.names()
usernames = passw.usernames()


authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
    config["preauthorized"],
)
name, authentication_status, username = authenticator.login("👋Login-TRMS👋", "main")
if st.session_state["authentication_status"] is False:
    st.error("Username atau Password salah 🫢")
elif st.session_state["authentication_status"] is None:
    st.warning("Masukan username dan password yang sesuai")
elif st.session_state["authentication_status"]:
    # Sidebar----------------------------------------------------------------------------
    with st.sidebar:
        if st.session_state["authentication_status"]:
            authenticator.logout("Logout", "sidebar")
            st.text(f"Salam Satu Bahu: {name}")
        # with open('assets\deep-learning.json')as dl:
        #     animasi= json.load(dl)
        add_logo("assets/unit.png", height=150)
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

    # Main apps-----------------------------------------------------------------------
    st.subheader("🚀Tax Revenue Monitoring Sistem")

    # filterdata
    filter_gabungan = cek_filter(start, end, kpp, map, sektor, segmen)
    filter = "and".join(x for x in filter_gabungan[0])
    filter_date = "and".join(x for x in filter_gabungan[0][:2])
    filter_date22 = "and".join(x for x in filter_gabungan[1][:2])
    filter22 = "and".join(x for x in filter_gabungan[1])

    # KPI-----------------------------------------------------------------------------------
    style_metric_cards(
        background_color="#FFFFFF",
        border_color="#005FAC",
        border_left_color="#005FAC",
    )
    data_kpi = prep.kpi(filter, filter22, filter_date, filter_date22)
    data23, data22 = data_kpi
    col_tahun = st.columns(4)

    with col_tahun[0]:
        bruto23 = data23["BRUTO"].sum()
        bruto22 = data22["BRUTO"].sum()
        tumbuh_bruto = (bruto23 - bruto22) / bruto22

        if (bruto23 / 1000000000000) > 1:
            st.metric(
                "Bruto",
                "{:,.2f}T".format(bruto23 / 1000000000000),
                delta="{:,.2f}%".format(tumbuh_bruto * 100),
            )
        else:
            st.metric(
                "Bruto",
                "{:,.2f}M".format(bruto23 / 1000000000),
                delta="{:,.2f}%".format(tumbuh_bruto * 100),
            )
    with col_tahun[1]:
        net23 = data23["NETTO"].sum()
        net22 = data22["NETTO"].sum()
        tumbuh_net = (net23 - net22) / net22

        if (net23 / 1000000000000) > 1:
            st.metric(
                "Netto",
                "{:,.2f}T".format(net23 / 1000000000000),
                delta="{:,.2f}%".format(tumbuh_net * 100),
            )
        else:
            st.metric(
                "Netto",
                "{:,.2f}M".format(net23 / 1000000000),
                delta="{:,.2f}%".format(tumbuh_net * 100),
            )

    with col_tahun[2]:
        kontrib23 = (data23["KONTRIBUSI"][0]) * 100
        kontrib22 = (data22["KONTRIBUSI"][0]) * 100
        st.metric(
            "Kontrib. Realisasi",
            f"{kontrib23:,.2f}%",
            delta=f"{kontrib23 - kontrib22:,.2f}%",
        )
    with col_tahun[3]:
        persentase23 = net23 / 27601733880000
        persentase22 = net22 / 22656373555000
        tumbuh_persen = persentase23 - persentase22
        st.metric(
            "Kontrib. Target Kanwil",
            "{:.2f}%".format(persentase23 * 100),
            delta="{:.2f}%".format(tumbuh_persen * 100),
        )

    st.markdown(
        """<hr style="height:1px;border:none;color:#FFFFFF;background-color:#ffc91b;" /> """,
        unsafe_allow_html=True,
    )

    # linechart--------------------
    linedata = prep.linedata(filter, filter22)
    linedata = linedata.groupby(["TAHUNBAYAR", "BULANBAYAR"])["sum"].sum().reset_index()
    linedata["text"] = linedata["sum"].apply(
        lambda x: "{:,.1f}M".format(x / 1000000000)
    )

    linedata23 = linedata[linedata["TAHUNBAYAR"] == "2023"]

    linedata23["kumulatif"] = linedata23["sum"].cumsum()
    linedata23["capaian_kumulatif"] = (linedata23["kumulatif"] / 27601733880000) * 100

    linedata22 = linedata[linedata["TAHUNBAYAR"] == "2022"]
    linedata22["kumulatif"] = linedata22["sum"].cumsum()
    linedata22["capaian_kumulatif"] = (linedata22["kumulatif"] / 22656373555000) * 100
    linedata = pd.concat([linedata23, linedata22], axis=0, ignore_index=True)

    linechart = px.bar(
        data_frame=linedata,
        x="BULANBAYAR",
        y="sum",
        color="TAHUNBAYAR",
        text="text",
        height=380,
        barmode="group",
    )

    linechart.update_layout(
        xaxis_title="",
        yaxis_title="",
        yaxis={"visible": False},
        xaxis={
            "tickmode": "array",
            "tickvals": [x for x in range(1, 13)],
            "ticktext": [calendar.month_name[i] for i in range(1, 13)],
        },
        autosize=True,
    )

    line = px.line(
        linedata,
        x="BULANBAYAR",
        y="kumulatif",
        color="TAHUNBAYAR",
        text=linedata["capaian_kumulatif"].apply(lambda x: "{:,.2f}%".format(x)),
        height=380,
        color_discrete_sequence=["#ffc91b", "#005FAC"],
        markers=True,
    )
    line.update_layout(
        xaxis_title="",
        yaxis_title="",
        yaxis={"visible": False},
        xaxis={
            "tickmode": "array",
            "tickvals": [x for x in range(1, 13)],
            "ticktext": [calendar.month_name[i] for i in range(1, 13)],
        },
        autosize=True,
    )
    with chart_container(linedata):
        timeseries = st.columns(2)
        with timeseries[0]:
            st.plotly_chart(linechart, use_container_width=True)
        with timeseries[1]:
            st.plotly_chart(line, use_container_width=True)

    # KET-----------------------------------------------------------------------
    ket = data_ket(filter, filter22).set_index("KET")

    colket = st.columns(5)
    with colket[0]:
        if "MPN" in ket.index:
            format_number = "{:,.1f}M" if ket.loc["MPN", "2023"] >= 0 else "{:,.1f}M"
            format_number_T = "{:,.1f}T" if ket.loc["MPN", "2023"] >= 0 else "{:,.1f}T"
            if ket.loc["MPN", "2023"] > 1000000000000:
                st.metric(
                    "MPN",
                    format_number_T.format(ket.loc["MPN", "2023"] / 1000000000000),
                    delta=format_number_T.format(
                        ket.loc["MPN", "selisih"] / 1000000000000
                    ),
                )
            else:
                st.metric(
                    "MPN",
                    format_number.format(ket.loc["MPN", "2023"] / 1000000000),
                    delta=format_number_T.format(
                        ket.loc["MPN", "2023"] / 1000000000000
                    ),
                )
        else:
            st.metric("MPN", "0M")
    with colket[1]:
        if "SPM" in ket.index:
            format_number = "{:,.1f}M" if ket.loc["SPM", "2023"] >= 0 else "{:,.1f}M"
            st.metric(
                "SPM",
                format_number.format(ket.loc["SPM", "2023"] / 1000000000),
                delta=format_number.format(ket.loc["SPM", "selisih"] / 1000000000),
            )
        else:
            st.metric("SPM", "0.0M")
    with colket[2]:
        if "PBK KIRIM" in ket.index:
            format_number = (
                "{:,.1f}M" if ket.loc["PBK KIRIM", "2023"] >= 0 else "{:,.1f}M"
            )
            st.metric(
                "PBK KIRIM",
                format_number.format(ket.loc["PBK KIRIM", "2023"] / 1000000000),
                delta=format_number.format(ket.loc["PBK KIRIM", "2023"] / 1000000000),
            )
        else:
            st.metric("PBK KIRIM", "0.0M")
    with colket[3]:
        if "PBK TERIMA" in ket.index:
            format_number = (
                "{:,.1f}M" if ket.loc["PBK TERIMA", "2023"] >= 0 else "{:,.1f}M"
            )
            st.metric(
                "PBK TERIMA",
                format_number.format(ket.loc["PBK TERIMA", "2023"] / 1000000000),
                delta=format_number.format(
                    ket.loc["PBK TERIMA", "selisih"] / 1000000000
                ),
            )
        else:
            st.metric("PBK TERIMA", "0.0M")
    with colket[4]:
        if "SPMKP" in ket.index:
            format_number = "{:,.1f}M" if ket.loc["SPMKP", "2023"] >= 0 else "{:,.1f}M"
            format_number_T = (
                "{:,.1f}T" if ket.loc["SPMKP", "2023"] >= 0 else "{:,.1f}T"
            )
            if ket.loc["SPMKP", "2023"] > 1000000000000:
                st.metric(
                    "SPMKP",
                    format_number_T.format(ket.loc["SPMKP", "2023"] / 1000000000000),
                    delta=format_number.format(
                        ket.loc["SPMKP", "selisih"] / 1000000000
                    ),
                )
            else:
                st.metric(
                    "SPMKP",
                    format_number.format(ket.loc["SPMKP", "2023"] / 1000000000),
                    delta=format_number.format(
                        ket.loc["SPMKP", "selisih"] / 1000000000
                    ),
                )
        else:
            st.metric("SPMKP", "0.0M")

    # PERSEKTOR-------------------------------------------------------------------------------

    data_sektor_awal = prep.sektor_yoy(filter, filter22)
    data_sektor_awal = data_sektor_awal[0]
    data_sektor_awal = (
        data_sektor_awal.groupby("NM_KATEGORI")
        .sum()
        .reset_index()
        .sort_values(by="2023", ascending=False)
        .reset_index()
        .drop(columns="index")
    )
    # data_sektor_awal['kontribusi'] = data_sektor_awal['2023']/data_sektor_awal['2023'].sum()
    data_sektor9 = data_sektor_awal.nlargest(10, "2023")
    data_sektor_lain = data_sektor_awal[
        ~data_sektor_awal["NM_KATEGORI"].isin(data_sektor9["NM_KATEGORI"])
    ]

    data_sektor_lain = pd.DataFrame(
        [
            [
                "LAINNYA",
                data_sektor_lain["2022"].sum(),
                data_sektor_lain["2023"].sum(),
                data_sektor_lain["selisih"].sum(),
                data_sektor_lain["tumbuh"].sum(),
                # data_sektor_lain['kontribusi'].sum()
            ]
        ],
        columns=["NM_KATEGORI", "2022", "2023", "selisih", "tumbuh"],
    )
    data_sektor = pd.concat([data_sektor9, data_sektor_lain], axis=0, ignore_index=True)

    data_sektor = data_sektor.assign(
        text22=data_sektor["2022"].apply(lambda x: "{:,.0f}M".format(x / 1000000000)),
        text23=data_sektor["2023"].apply(lambda x: "{:,.0f}M".format(x / 1000000000)),
        kontribusi_2023=data_sektor["2023"] / data_sektor["2023"].sum(),
        kontribusi_2022=data_sektor["2022"] / data_sektor["2022"].sum(),
    )
    data_sektor = data_sektor.assign(
        kontrib_persen23=data_sektor["kontribusi_2023"].apply(
            lambda x: "{:,.1f}%".format(x * 100)
        )
    ).assign(
        kontrib_persen22=data_sektor["kontribusi_2022"].apply(
            lambda x: "{:,.1f}%".format(x * 100)
        )
    )

    data_sektor.sort_values(by="2023", ascending=True, inplace=True)

    sektor_chart = make_subplots(
        rows=1,
        cols=2,
        shared_yaxes=True,
        horizontal_spacing=0,
    )
    sektor23 = go.Bar(
        x=data_sektor["2023"] / 1000000000,
        y=data_sektor["NM_KATEGORI"],
        name="2023",
        orientation="h",
        text=data_sektor["kontrib_persen23"],
        texttemplate="%{x:,.1f}M <br> (%{text})",
        textposition="auto",
        marker=dict(color="#005FAC"),
        textangle=0,
        base=0,
    )

    sektor22 = go.Bar(
        x=data_sektor["2022"] / 1000000000,
        y=data_sektor["NM_KATEGORI"],
        name="2022",
        orientation="h",
        text=data_sektor["kontrib_persen22"],
        textposition="auto",
        texttemplate="%{x:,.1f}M<br> (%{text})",
        marker=dict(color="#ffc91b"),
        textangle=0,
        base=0,
    )
    sektor_data = [sektor22, sektor23]
    sektor_layout = go.Layout(barmode="group")
    sektor_bar = go.Figure(data=sektor_data, layout=sektor_layout)

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
    sektor_chart.add_trace(sektor_bar.data[0], row=1, col=1)
    sektor_chart.add_trace(sektor_bar.data[1], row=1, col=2)
    sektor_chart.update_xaxes(row=1, col=1, autorange="reversed", showticklabels=False)
    sektor_chart.update_xaxes(row=1, col=2, showticklabels=False)

    # sektor_chart.add_trace(kontribusi_chart.data[0], row=1, col=2)
    sektor_chart.update_layout(
        height=760,
        title=dict(text="Per Sektor (Bruto)", x=0.5, y=0.95, font=dict(size=26)),
        showlegend=True,
        font=dict(
            family="Arial",
            size=12,
            color="#333333",
        ),
    )

    with chart_container(data_sektor_awal):
        st.plotly_chart(sektor_chart, use_container_width=True)

    st.markdown(
        """<hr style="height:1px;border:none;color:#FFFFFF;background-color:#ffc91b;" /> """,
        unsafe_allow_html=True,
    )

    # JENIS PAJAK----------------------------------------------------------------------
    jenis_pajak = prep.jenis_pajak(filter, filter22)
    jenis_pajak = pd.pivot_table(
        jenis_pajak, index="MAP", columns="TAHUNBAYAR", values="BRUTO"
    )
    jenis_pajak = (
        jenis_pajak.assign(
            tumbuh=round(
                (
                    (jenis_pajak["2023"] - jenis_pajak["2022"])
                    / jenis_pajak["2022"]
                    * 100
                ),
                2,
            )
        )
        .assign(
            kontrib23=round((jenis_pajak["2023"] / jenis_pajak["2023"].sum() * 100), 2)
        )
        .assign(
            kontrib22=round((jenis_pajak["2022"] / jenis_pajak["2022"].sum() * 100), 2)
        )
        .sort_values(by="2023", ascending=False)
    )

    jenis_pajak9 = jenis_pajak.nlargest(10, "2023")

    jenis_pajak9 = jenis_pajak9.assign(
        tbruto=jenis_pajak9["2023"].apply(lambda x: "{:,.1f}M".format(x / 1000000000))
    )
    jenis_pajak9 = jenis_pajak9.sort_values(by="2023", ascending=True)

    # jenis_pajak9_23 = jenis_pajak9[jenis_pajak9["TAHUNBAYAR"] == "2023"].sort_values(
    #     by="BRUTO", ascending=True
    # )
    mapbar23 = go.Bar(
        x=jenis_pajak9["2023"] / 1000000000,
        y=jenis_pajak9.index,
        name="2023",
        orientation="h",
        text=jenis_pajak9["kontrib23"],
        texttemplate="%{x:,.1f}M (%{text})%",
        textposition="outside",
        marker=dict(color="#005FAC"),  # ffc91b
        width=0.5,
    )
    # jenis_pajak9_22 = jenis_pajak9[jenis_pajak9["TAHUNBAYAR"] == "2022"].sort_values(
    #     by="BRUTO", ascending=True
    # )
    mapbar22 = go.Bar(
        x=jenis_pajak9["2022"] / 1000000000,
        y=jenis_pajak9.index,
        name="2022",
        orientation="h",
        text=jenis_pajak9["kontrib22"],
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
        title=dict(text="Per Jenis", x=0.5, y=0.95, font=dict(size=26)),
        showlegend=True,
        bargap=0.2,
        font=dict(
            family="Arial",
            size=12,
            color="#333333",
        ),
    )
    mapchart = go.Figure(data=data_map, layout=map_layout)

    with chart_container(jenis_pajak):
        st.plotly_chart(mapchart, use_container_width=True)

    st.markdown(
        """<hr style="height:1px;border:none;color:#FFFFFF;background-color:#ffc91b;" /> """,
        unsafe_allow_html=True,
    )

    # TOP10-----------------------------------------------------------------------------------
    topwp, botwp = prep.naikturun(filter, filter22)

    topwp.iloc[:, 2:] = (topwp.iloc[:, 2:] / 1000000000).applymap(
        lambda x: "{:,.1f}".format(x)
    )

    botwp.iloc[:, 2:] = (botwp.iloc[:, 2:] / 1000000000).applymap(
        lambda x: "{:,.1f}".format(x)
    )

    with st.container():
        tab_wp = st.tabs(["Top 10 WP", "Top 10 Tumbuh", "Bottom 10 WP Tumbuh"])
        with tab_wp[0]:
            data_proporsi = prep.proporsi(filter)
            with chart_container(data_proporsi):
                # PROPORSI--------------------------------------------------------------------
                data_proporsi = data_proporsi.iloc[:10,]
                proporsi_chart = go.Figure(
                    go.Funnel(
                        y=data_proporsi["NAMA_WP"],
                        x=data_proporsi["BRUTO"] / 1000000000,
                        textposition="inside",
                        # textinfo="value+percent initial",
                        text=data_proporsi["KONTRIBUSI"],
                        texttemplate="%{x:,.1f}M <br> %{text:.1%}",
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
                    height=640,
                    title=dict(
                        text="10 WP Terbesar Bruto",
                        x=0.5,
                        y=0.95,
                        font=dict(size=26),
                    ),
                )
                st.plotly_chart(proporsi_chart, use_container_width=True)
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
                        font=dict(size=26),
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
                            align=["left", "left", "center", "center", "center"],
                            font_size=14,
                            height=30,
                        ),
                    )
                ]
            )
            table_bot.update_layout(height=640, width=1024)
            with chart_container(botwp):
                st.plotly_chart(table_bot, use_container_width=True)
