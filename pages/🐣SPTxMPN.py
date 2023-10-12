import streamlit as st
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
conn = st.experimental_connection("mysql", type="sql")
conn_pg = st.experimental_connection("ppmpkm", type="sql")
from scripts.db import sptxmpn, filter_dataframe

# st.set_page_config(
#     page_title="Tax Revenue Monitoring Sistem",
#     page_icon="assets/logo_djo.png",
#     layout="centered",
#     initial_sidebar_state="expanded",
# )
st.markdown(
    """
        <style>
               .block-container {
                    margin-top:2rem;
                    padding-top: 0rem;
                    padding-bottom: 0rem;
                    padding-left: 1rem;
                    padding-right: 1rem;
                }
                [data-testid="stHeader"]{
                    display:none
                }
        </style>
        """,
    unsafe_allow_html=True,
)


@st.cache_data
def convert_df(df: pd.DataFrame):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun

    return df.to_csv().encode("utf-8")


def list_to_sql(column, value):
    value_str = ",".join([f"'{x}'" for x in value])
    sql_filter = f"{column} IN ({value_str})"
    return sql_filter


st.title("Data SPT dan Pembayarannya")

colfilter = st.columns([2, 1, 1, 1])
with colfilter[0]:
    spt_opt = [
        "",
        "SPT Masa PPh Pasal 25",
        "SPT Masa PPh Pasal 23/26",
        "SPT Masa PPh Pasal 4 ayat (2)",
        "SPT Tahunan PPh Orang Pribadi",
        "SPT Tahunan PPh Badan",
        "SPT Masa PPh Pasal 21/26",
        "SPT Masa PPh Pasal 22",
        "SPT Masa Pemungut Bea Meterai",
        "SPT Masa PPN dan PPnBM",
        "SPT Masa PPh Pasal 15",
        "SPT Masa PPN Pemungut",
    ]
    spt = st.selectbox(
        label="SPT",
        options=spt_opt,
    )
with colfilter[1]:
    thn_pjk = st.selectbox(
        label="Tahun Pajak",
        options=["", "2021", "2022", "2023"],
    )
with colfilter[2]:
    kppadm = st.selectbox(
        label="KPP",
        options=["", "001", "002", "003", "004", "005", "007", "008", "009", "097"],
    )
with colfilter[3]:
    npwp = st.text_input(label="NPWP15", max_chars=15, type="default")


def kdbayar(spt):
    spt_khusus = ["SPT Masa PPh Pasal 4 ayat (2)", "SPT Masa PPh Pasal 15"]
    if spt in spt_khusus:
        kdbayar = "KDBAYAR not like '3%' AND KDBAYAR not like '5%' "
    else:
        kdbayar = (
            conn_pg.query(
                f"""select distinct "kdbayar" from dimensi.spt_map where spt='{spt}' """
            )
        )["kdbayar"].tolist()
        if kdbayar:
            kdbayar = list_to_sql("KDBAYAR", kdbayar)

    return kdbayar


def filter_ppmpkm(thn_pjk, kdmap, spt, adm, npwp):
    filter_ppmpkm = []
    filter_mf = []
    filter_spt = []

    if thn_pjk:
        filter_thn = f""" TAHUN='{thn_pjk}' """
        filter_ppmpkm.append(filter_thn)
        filter_spt.append(f""" TAHUN_PAJAK ={thn_pjk} """)
    if kdmap:
        filter_map = list_to_sql("KDMAP", kdmap)
        filter_ppmpkm.append(filter_map)
    if spt:
        filter_kjs = kdbayar(spt)
        filter_ppmpkm.append(filter_kjs)
        filter_spt.append(f""" JENIS_SPT = '{spt}' """)
    if adm:
        filter_adm = list_to_sql("ADMIN", [adm])
        filter_ppmpkm.append(filter_adm)
        filter_mf.append(list_to_sql("KPPADM", [adm]))
    if npwp:
        filter_npwp = list_to_sql("NPWP", [npwp])
        filter_ppmpkm.append(filter_npwp)
        filter_mf.append(list_to_sql("NPWP15", [npwp]))
    return [filter_ppmpkm, filter_mf, filter_spt]


kdmap = (
    conn_pg.query(
        f"""select distinct "kdmap" from dimensi.spt_map where spt='{spt}' """
    )
)["kdmap"].tolist()

filter_ppmpkm = filter_ppmpkm(
    thn_pjk=thn_pjk, kdmap=kdmap, spt=spt, adm=kppadm, npwp=npwp
)
if filter_ppmpkm:
    filter_mpn = "and ".join(x for x in filter_ppmpkm[0])
    filter_mf = "and ".join(x for x in filter_ppmpkm[1])
    filter_spt = "and ".join(x for x in filter_ppmpkm[2])

with st.expander(label="Keterangan Data"):
    st.code(
        "SPT berasal dari sidjp_masterspt, secara default jika tidak memilih maka akan memilih semua tahun pajak dan kpp"
    )
    st.code(filter_mpn)
    st.code(filter_mf)
    st.code(filter_spt)

if filter_mpn or filter_mf or filter_spt:
    data = sptxmpn(filter_mpn, filter_mf, filter_spt)
    data.rename(columns={"JML_LAPOR": "SPT"}, inplace=True)
    pv = pd.pivot_table(
        data=data,
        index=["NPWP15", "NAMA_WP", "KPPADM", "STATUS_PKP"],
        columns=["TAHUN_PAJAK", "MASA_PAJAK"],
        values=["NETTO", "SPT"],
        aggfunc="sum",
    ).reset_index()
    pv.fillna(0, inplace=True)
    pv.columns = [f"{col[1]}_{col[2]}_{col[0]}" for col in pv.columns]
    st.dataframe(pv, use_container_width=True)

    filename = f"{spt}_{thn_pjk}_{kppadm}_{npwp}"
    st.download_button(
        label="Download Data",
        data=convert_df(pv),
        file_name=f"SPTxMPN_{filename}.csv",
        mime="text/csv",
    )

    if len(pv) > 0:
        st.dataframe(filter_dataframe(pv, key=1))


# filter = st.checkbox(label="Filter lagi data?")
# if filter:
