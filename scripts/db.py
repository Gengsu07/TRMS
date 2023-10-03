import pandas as pd
import calendar
import streamlit as st
import random
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from urllib.parse import quote_plus

load_dotenv()
conn = st.experimental_connection("ppmpkm", type="sql")
# conn_uri = os.environ.get("CONN_URI")
postgres_username = os.environ.get("POSTGRES_USERNAME")
postgres_password = quote_plus(os.environ.get("POSTGRES_PASSWORD"))
postgres_url = os.environ.get("POSTGRES_URL")
postgres_table = os.environ.get("POSTGRES_TABLE")

conn_postgres = create_engine(
    f"postgresql://{postgres_username}:{postgres_password}@{postgres_url}/{postgres_table}"
)

dict_sektor = {
    "A": "PERTANIAN, KEHUTANAN DAN PERIKANAN",
    "Z": "PEJABAT NEGARA, KARYAWAN, PENSIUNAN",
    "M": "AKTIVITAS PROFESIONAL, ILMIAH DAN TEKNIS",
    "S": "AKTIVITAS JASA LAINNYA",
    "U": "BADAN INTER DAN EXTRA INTERNASIONAL",
    "J": "INFORMASI DAN KOMUNIKASI",
    "D": "PENGADAAN LISTRIK, GAS, UAP/AIR PANAS DAN UDARA DINGIN",
    "O": "ADMIN. PEMERINTAHAN & JAMINAN SOSIAL",
    "G": "PERDAGANGAN BESAR ECERAN & PERAWATAN MOBIL",
    "K": "AKTIVITAS KEUANGAN DAN ASURANSI",
    "F": "KONSTRUKSI",
    "Q": "KESEHATAN MANUSIA & AKTIVITAS SOSIAL",
    "E": "TREATMENT AIR,LIMBAH",
    "P": "PENDIDIKAN",
    "R": "KESENIAN, HIBURAN DAN REKREASI",
    "H": "PENGANGKUTAN DAN PERGUDANGAN",
    "L": "REAL ESTAT",
    "": "",
    "C": "INDUSTRI PENGOLAHAN",
    "I": "PENYEDIAAN AKOMODASI DAN PENYEDIAAN MAKAN MINUM",
    "B": "PERTAMBANGAN DAN PENGGALIAN",
    "N": "PENYEWAAN & SGU TANPA HAK OPSI",
    "T": "RUMAH TANGGA PEMBERI KERJA",
}
target2023 = {
    "001": 608265424000,
    "002": 542401593000,
    "003": 1150993826000,
    "004": 843373880000,
    "005": 1481697044000,
    "007": 11518776933000,
    "008": 616125873000,
    "009": 1634143550000,
    "097": 9205955757000,
}
target2022 = {
    "001": 477310544000,
    "002": 1180601400000,
    "003": 1001261091000,
    "004": 679223200000,
    "005": 1041766662000,
    "007": 8574702940000,
    "008": 608619845000,
    "009": 1200824695000,
    "097": 7892063178000,
}


def format_angka(value):
    cek = value / 1000
    if (cek > 1000000000) or (cek < -1000000000):  # >1 1T
        nominal = "{:,.2f}T".format(value / 1000000000000)
    elif (cek > 1000000) or (cek < -1000000):  # >1M
        nominal = "{:,.2f}M".format(value / 1000000000)
    elif (cek > 1000) or (cek < -1000):  # > 1Jt
        nominal = "{:,.2f}Jt".format(value / 1000000)
    else:
        nominal = "{:,.0f}".format(value)
    return nominal


@st.cache_data
def bruto(filter):
    kueri = f""" 
    select 
    p."NPWP",
    p."NAMA_WP" , 
    sum(p."NOMINAL") as "BRUTO"
    from ppmpkm p 
    where 
    p."KET" in ('MPN','SPM','PBK KIRIM','PBK TERIMA') and {filter}
    group by p."NPWP" ,p."NAMA_WP" 
    order by "BRUTO" desc
    """
    bruto = conn.query(kueri)
    # brutomin = bruto[bruto['BRUTO']<0].index.tolist()
    row = bruto.shape[0] + 1
    # rowplus = row-len(brutomin)

    bruto_a = bruto.nlargest(10, columns="BRUTO")
    bruto_b = pd.DataFrame(
        [["Penerimaan 10 WP Terbesar", bruto_a["BRUTO"].sum()]],
        columns=["NAMA_WP", "BRUTO"],
    )
    bruto_c = pd.DataFrame(
        [["Penerimaan 11 s.d. 100 WP Terbesar", bruto.iloc[10:100,]["BRUTO"].sum()]],
        columns=["NAMA_WP", "BRUTO"],
    )
    bruto_d = pd.DataFrame(
        [["Penerimaan 101 s.d. 500 WP Terbesar", bruto.iloc[100:500,]["BRUTO"].sum()]],
        columns=["NAMA_WP", "BRUTO"],
    )
    bruto_e = pd.DataFrame(
        [
            [
                "Penerimaan 501 s.d. {} WP Terbesar".format(row),
                bruto.iloc[500:row,]["BRUTO"].sum(),
            ]
        ],
        columns=["NAMA_WP", "BRUTO"],
    )
    bruto_g = pd.DataFrame(
        [["Total", bruto["BRUTO"].sum()]], columns=["NAMA_WP", "BRUTO"]
    )
    # bruto_g = pd.DataFrame([['Total',bruto['bruto'].sum()]],columns=['NAMA_WP','bruto'])

    bruto_ok = pd.concat(
        [bruto_a, bruto_b, bruto_c, bruto_d, bruto_e, bruto_g],
        axis=0,
        ignore_index=True,
    )
    bruto_ok["KONTRIBUSI"] = (bruto_ok["BRUTO"] / bruto["BRUTO"].sum()) * 100
    return bruto_ok


@st.cache_data
def sektor(filter):
    data_sektor = conn.query(
        f"""
        SELECT 
        kat."NM_KATEGORI", kat."NETTO",sum(kat."BRUTO") as "BRUTO"
        FROM (
                SELECT 
                p."NM_KATEGORI" , 
                sum(CASE WHEN p."KET" in('MPN','SPM') THEN p."NOMINAL" END ) AS "BRUTO",
                sum(p."NOMINAL") AS "NETTO" 
                FROM 
                public.ppmpkm p 
                WHERE {filter} 
                GROUP BY p."NM_KATEGORI" 
                ORDER BY sum(p."NOMINAL") DESC 
        )kat
        GROUP BY kat."NM_KATEGORI",kat."NETTO"
        ORDER BY sum(kat."BRUTO") ASC """
    )

    data_sektor["NM_KATEGORI"] = data_sektor["NM_KATEGORI"].map(dict_sektor)
    return data_sektor


@st.cache_data
def sektor_yoy(filter, filter22, includewp: bool):
    if includewp:
        kueri = f"""
        SELECT p."NAMA_WP",
        p."KD_KATEGORI" ,p."NM_KATEGORI",p."TAHUNBAYAR",p."BULANBAYAR",p."JENIS_WP",
        sum(p."NOMINAL") AS "NETTO",
        sum(case when p."KET" in('MPN','SPM') then p."NOMINAL" end) as "BRUTO"
        FROM 
        ppmpkm p 
        WHERE {filter}
        GROUP BY p."NAMA_WP",p."KD_KATEGORI",p."NM_KATEGORI" ,p."TAHUNBAYAR",p."BULANBAYAR",p."JENIS_WP"
        UNION ALL 
        SELECT p."NAMA_WP",
        p."KD_KATEGORI",p."NM_KATEGORI" , p."TAHUNBAYAR",p."BULANBAYAR",p."JENIS_WP",
        sum(p."NOMINAL") AS "NETTO",
        sum(case when p."KET" in('MPN','SPM') then p."NOMINAL" end) as "BRUTO"
        FROM 
        ppmpkm p 
        WHERE {filter22}
        GROUP BY p."NAMA_WP",p."KD_KATEGORI" ,p."NM_KATEGORI",p."TAHUNBAYAR",p."BULANBAYAR",p."JENIS_WP"
        """
        data = conn.query(kueri)
        data["NM_KATEGORI"] = data["KD_KATEGORI"].map(dict_sektor)
        data["TAHUNBAYAR"] = data["TAHUNBAYAR"].astype("str")

        sektor_yoy = data.pivot_table(
            index=["NAMA_WP", "NM_KATEGORI"],
            columns="TAHUNBAYAR",
            values=["NETTO", "BRUTO"],
            aggfunc="sum",
        ).reset_index()

        sektor_yoy = sektor_yoy.sort_values(by=("BRUTO", "2023"), ascending=False)
        sektor_yoy["NaikBruto"] = round(
            sektor_yoy[("BRUTO", "2023")] - sektor_yoy[("BRUTO", "2022")], 0
        )
        sektor_yoy["NaikNetto"] = round(
            sektor_yoy[("NETTO", "2023")] - sektor_yoy[("NETTO", "2022")], 0
        )
        sektor_yoy["TumbuhBruto"] = (
            sektor_yoy["NaikBruto"] / sektor_yoy[("BRUTO", "2022")]
        ) * 100
        sektor_yoy.columns = sektor_yoy.columns.map("".join)

        sektor_mom = data.pivot_table(
            index=["NM_KATEGORI", "BULANBAYAR"],
            columns="TAHUNBAYAR",
            values=["BRUTO", "NETTO"],
            aggfunc="sum",
        ).reset_index()
        sektor_mom.columns = sektor_mom.columns.map("".join)
    else:
        kueri = f"""
        SELECT p."NAMA_WP",
        p."KD_KATEGORI",p."NM_KATEGORI" ,p."TAHUNBAYAR",p."BULANBAYAR",p."JENIS_WP",
        sum(p."NOMINAL") AS "NETTO",
        sum(case when p."KET" in('MPN','SPM') then p."NOMINAL" end) as "BRUTO"
        FROM 
        ppmpkm p 
        WHERE {filter}
        GROUP BY p."NAMA_WP",p."KD_KATEGORI",p."NM_KATEGORI" ,p."TAHUNBAYAR",p."BULANBAYAR",p."JENIS_WP"
        UNION ALL 
        SELECT p."NAMA_WP",p."KD_KATEGORI",
        p."NM_KATEGORI", p."TAHUNBAYAR",p."BULANBAYAR",p."JENIS_WP",
        sum(p."NOMINAL") AS "NETTO",
        sum(case when p."KET" in('MPN','SPM') then p."NOMINAL" end) as "BRUTO"
        FROM 
        ppmpkm p 
        WHERE {filter22}
        GROUP BY p."NAMA_WP",p."KD_KATEGORI",p."NM_KATEGORI" ,p."TAHUNBAYAR",p."BULANBAYAR",p."JENIS_WP"
        """
        data = conn.query(kueri)
        data["NM_KATEGORI"] = data["KD_KATEGORI"].map(dict_sektor)
        data["TAHUNBAYAR"] = data["TAHUNBAYAR"].astype("str")

        sektor_yoy = data.pivot_table(
            index=["NM_KATEGORI"],
            columns="TAHUNBAYAR",
            values=["NETTO", "BRUTO"],
            aggfunc="sum",
        ).reset_index()

        sektor_yoy = sektor_yoy.sort_values(by=("BRUTO", "2023"), ascending=False)
        sektor_yoy["NaikBruto"] = round(
            sektor_yoy[("BRUTO", "2023")] - sektor_yoy[("BRUTO", "2022")], 0
        )
        sektor_yoy["NaikNetto"] = round(
            sektor_yoy[("NETTO", "2023")] - sektor_yoy[("NETTO", "2022")], 0
        )
        sektor_yoy["TumbuhBruto"] = (
            sektor_yoy["NaikBruto"] / sektor_yoy[("BRUTO", "2022")]
        ) * 100
        sektor_yoy.columns = sektor_yoy.columns.map("".join)

        sektor_mom = data.pivot_table(
            index=["NM_KATEGORI", "BULANBAYAR"],
            columns="TAHUNBAYAR",
            values=["BRUTO", "NETTO"],
            aggfunc="sum",
        ).reset_index()
        sektor_mom.columns = sektor_mom.columns.map("".join)

    # sektor yoy[2]
    sektor_yoy9 = sektor_yoy.nlargest(12, "NETTO2023")
    sektor_lain = sektor_yoy[
        ~sektor_yoy["NM_KATEGORI"].isin(sektor_yoy9["NM_KATEGORI"].tolist())
    ]

    sektor_lain_agg = pd.DataFrame(
        [
            [
                "LAINNYA",
                sektor_lain["BRUTO2022"].sum(),
                sektor_lain["BRUTO2023"].sum(),
                sektor_lain["NETTO2022"].sum(),
                sektor_lain["NETTO2023"].sum(),
            ]
        ],
        columns=["NM_KATEGORI", "BRUTO2022", "BRUTO2023", "NETTO2022", "NETTO2023"],
    )
    sektor_lain_agg["NaikBruto"] = round(
        sektor_lain_agg["BRUTO2023"] - sektor_lain_agg["BRUTO2022"], 0
    )
    sektor_lain_agg["NaikNetto"] = round(
        sektor_lain_agg["NETTO2023"] - sektor_lain_agg["NETTO2022"], 0
    )
    sektor_lain_agg["TumbuhBruto"] = (
        sektor_lain_agg["NaikBruto"] / sektor_lain_agg["BRUTO2022"]
    ) * 100

    sektor_yoy9 = pd.concat([sektor_yoy9, sektor_lain_agg], axis=0, ignore_index=False)
    sektor_yoy9 = sektor_yoy9.assign(
        text22=sektor_yoy9["BRUTO2022"].apply(lambda x: format_angka(x)),
        text23=sektor_yoy9["BRUTO2023"].apply(lambda x: format_angka(x)),
        Kontribusi2023=(sektor_yoy9["BRUTO2023"] / sektor_yoy["BRUTO2023"].sum()) * 100,
        Kontribusi2022=(sektor_yoy9["BRUTO2022"] / sektor_yoy["BRUTO2022"].sum()) * 100,
    )
    sektor_yoy9 = sektor_yoy9.assign(
        kontrib2023=sektor_yoy9["Kontribusi2023"].apply(lambda x: "{:,.1f}%".format(x))
    ).assign(
        kontrib2022=sektor_yoy9["Kontribusi2022"].apply(lambda x: "{:,.1f}%".format(x))
    )
    sektor_yoy9.sort_values(by="BRUTO2023", ascending=True, inplace=True)
    sektor_yoy9["TumbuhBruto_f"] = sektor_yoy9["TumbuhBruto"].apply(
        lambda x: "{:,.1f}%".format(x)
    )
    return [sektor_yoy9, sektor_mom, sektor_yoy]


@st.cache_data
def sektor2023(filter):
    kueri = f"""
    SELECT 
    p."DATEBAYAR",p."NM_KATEGORI" , sum(p."NOMINAL") AS "NOMINAL"
    FROM 
    ppmpkm p 
    WHERE p."KET" in('MPN','SPM') and {filter}
    GROUP BY p."DATEBAYAR",p."NM_KATEGORI" 
    """
    sektor2023 = conn.query(kueri)
    return sektor2023


def klu(filter):
    kueri = f""" 
        SELECT
        p."NM_KATEGORI",p."NAMA_KLU" ,sum(p."NOMINAL") as "BRUTO"
        FROM 
        ppmpkm p
        WHERE  p."KET" in('MPN','SPM') and {filter}
        GROUP BY p."NM_KATEGORI",p."NAMA_KLU" 
        ORDER BY sum(p."NOMINAL")"""
    klu = conn.query(kueri)
    return klu


def jns_pajak(filter, filter22, includewp: bool):
    kueri = f"""
    SELECT 
    p."NAMA_WP",p."MAP" , p."TAHUNBAYAR",p."JENIS_WP",
    sum(p."NOMINAL") AS "NETTO" ,
    sum(case when  p."KET" in('MPN','SPM') then p."NOMINAL" end) as "BRUTO"
    FROM 
    public.ppmpkm p 
    WHERE {filter} 
    GROUP BY p."NAMA_WP", p."MAP" ,p."TAHUNBAYAR",p."JENIS_WP"
    UNION ALL
    SELECT 
    p."NAMA_WP",p."MAP" , p."TAHUNBAYAR",p."JENIS_WP",
    sum(p."NOMINAL") AS "NETTO" ,
    sum(case when  p."KET" in('MPN','SPM') then p."NOMINAL" end) as "BRUTO"
    FROM 
    public.ppmpkm p 
    WHERE {filter22} 
    GROUP BY p."NAMA_WP",p."MAP" ,p."TAHUNBAYAR" ,p."JENIS_WP"
    """
    jenis = conn.query(kueri)
    if includewp:
        jenis_wp = (
            jenis.groupby(["NAMA_WP", "MAP", "TAHUNBAYAR", "JENIS_WP"])
            .sum()
            .reset_index()
        )
        jenis_wp["TAHUNBAYAR"] = jenis_wp["TAHUNBAYAR"].astype("str")
        jenis_wp = pd.pivot_table(
            jenis_wp,
            index=["NAMA_WP", "MAP", "JENIS_WP"],
            columns="TAHUNBAYAR",
            values=["NETTO", "BRUTO"],
            aggfunc="sum",
        ).reset_index()
        jenis_wp.columns = jenis_wp.columns.map("".join)
        jenis_wp = (
            jenis_wp.assign(
                TUMBUH=round(
                    (
                        (jenis_wp["BRUTO2023"] - jenis_wp["BRUTO2022"])
                        / jenis_wp["BRUTO2022"]
                        * 100
                    ),
                    2,
                )
            )
            .assign(
                KONTRIBUSI2023=round(
                    (jenis_wp["BRUTO2023"] / jenis_wp["BRUTO2023"].sum() * 100), 2
                )
            )
            .assign(
                KONTRIBUSI2022=round(
                    (jenis_wp["BRUTO2022"] / jenis_wp["BRUTO2022"].sum() * 100), 2
                )
            )
            .sort_values(by="BRUTO2023", ascending=False)
        )
        jenis_wp.loc[:, "BRUTO2022":"NETTO2023"] = jenis_wp.loc[
            :, "BRUTO2022":"NETTO2023"
        ].applymap(lambda x: round(x, 0))
        jenis_wp9 = jenis_wp.nlargest(10, "BRUTO2023")

        jenis_wp9 = jenis_wp9.assign(
            text23=jenis_wp9["BRUTO2023"].apply(
                lambda x: "{:,.1f}M".format(x / 1000000000)
            )
        )
        jenis_wp9 = jenis_wp9.sort_values(by="BRUTO2023", ascending=False)
        return [jenis_wp, jenis_wp9]

    else:
        jenis_nwp = jenis.groupby(["MAP", "TAHUNBAYAR"]).sum().reset_index()
        jenis_nwp["TAHUNBAYAR"] = jenis_nwp["TAHUNBAYAR"].astype("str")
        jenis_nwp = pd.pivot_table(
            jenis_nwp,
            index=["MAP"],
            columns="TAHUNBAYAR",
            values=["NETTO", "BRUTO"],
            aggfunc="sum",
        ).reset_index()
        jenis_nwp.columns = jenis_nwp.columns.map("".join)
        jenis_nwp = (
            jenis_nwp.assign(
                TUMBUH=round(
                    (
                        (jenis_nwp["BRUTO2023"] - jenis_nwp["BRUTO2022"])
                        / jenis_nwp["BRUTO2022"]
                        * 100
                    ),
                    2,
                )
            )
            .assign(
                KONTRIBUSI2023=round(
                    (jenis_nwp["BRUTO2023"] / jenis_nwp["BRUTO2023"].sum() * 100), 2
                )
            )
            .assign(
                KONTRIBUSI2022=round(
                    (jenis_nwp["BRUTO2022"] / jenis_nwp["BRUTO2022"].sum() * 100), 2
                )
            )
            .sort_values(by="BRUTO2023", ascending=False)
        )
        jenis_nwp.loc[:, "BRUTO2022":"NETTO2023"] = jenis_nwp.loc[
            :, "BRUTO2022":"NETTO2023"
        ].applymap(lambda x: round(x, 0))
        jenis_nwp9 = jenis_nwp.nlargest(10, "BRUTO2023")

        jenis_nwp9 = jenis_nwp9.assign(
            text23=jenis_nwp9["BRUTO2023"].apply(
                lambda x: "{:,.1f}M".format(x / 1000000000)
            )
        )
        jenis_nwp9 = jenis_nwp9.sort_values(by="BRUTO2023", ascending=False)
        return [jenis_nwp, jenis_nwp9]


def kjs(filter):
    kueri = f""" 
        SELECT
        p."MAP",p."KDBAYAR" ,sum(p."NOMINAL") as "BRUTO"
        FROM 
        ppmpkm p
        WHERE  p."KET" in('MPN','SPM') and {filter}
        GROUP BY p."MAP",p."KDBAYAR"  """
    kjs = conn.query(kueri)
    return kjs


@st.cache_data
def kpi(filter, filter22, filter_date, filter_date22):
    mpn23 = conn.query(
        f""" SELECT
            sum( CASE WHEN p."KET" !='SPMKP' THEN p."NOMINAL" END) AS "BRUTO" ,
            sum( p."NOMINAL") AS "NETTO" ,
            (sum( p."NOMINAL" ) / 
            (
            SELECT
                Sum( "NOMINAL" )
            FROM
                ppmpkm
            WHERE {filter_date}
                )) AS "KONTRIBUSI"
            FROM
                ppmpkm p
            WHERE
               {filter}
                """
    )
    mpn22 = conn.query(
        f""" SELECT
            sum( CASE WHEN p."KET" !='SPMKP' THEN p."NOMINAL" END) AS "BRUTO" ,
            sum( p."NOMINAL") AS "NETTO" ,
            (sum( p."NOMINAL") / 
            (
            SELECT
                Sum( "NOMINAL" )
            FROM
                ppmpkm
            WHERE {filter_date22}
                )) AS "KONTRIBUSI"
            FROM
                ppmpkm p
            WHERE
               {filter22}
                """
    )
    return [mpn23, mpn22]


@st.cache_data
def linedata(filter, filter22):
    linedata = conn.query(
        f"""select p."BULANBAYAR",p."TAHUNBAYAR",sum("NOMINAL") from ppmpkm p 
                where {filter}
                GROUP BY p."BULANBAYAR",p."TAHUNBAYAR"
                UNION ALL
                select p."BULANBAYAR",p."TAHUNBAYAR",sum("NOMINAL") from ppmpkm p 
                where {filter22}
                GROUP BY p."BULANBAYAR" ,p."TAHUNBAYAR"
                """
    )
    linedata["TAHUNBAYAR"] = linedata["TAHUNBAYAR"].astype("str")
    return linedata


@st.cache_data
def naikturun(filter, filter22):
    kueri = f""" 
     SELECT
	p."NPWP15",
	p."NAMA_WP",
    p."TAHUNBAYAR",
	SUM (p."NOMINAL") AS "NOMINAL"
    FROM
        ppmpkm p
    WHERE
        p."KET" in('MPN','SPM') AND {filter}
    GROUP BY
        p."NPWP15",
        p."NAMA_WP",
        p."TAHUNBAYAR"
    UNION ALL
         SELECT
	p."NPWP15",
	p."NAMA_WP",
    p."TAHUNBAYAR",
	SUM (p."NOMINAL") AS "NOMINAL"
    FROM
        ppmpkm p
    WHERE
        p."KET" in('MPN','SPM') AND {filter22}
    GROUP BY
        p."NPWP15",
        p."NAMA_WP",
        p."TAHUNBAYAR"
        """
    data = conn.query(kueri)
    data["TAHUNBAYAR"] = data["TAHUNBAYAR"].astype("str")
    # data = (
    #     data.groupby(["NPWP", "NAMA_WP", "TAHUNBAYAR"])["NOMINAL"].sum().reset_index()
    # )
    data = data.pivot_table(
        index=["NPWP15", "NAMA_WP"],
        columns="TAHUNBAYAR",
        values="NOMINAL",
        aggfunc="sum",
    ).reset_index()

    data["SELISIH"] = data["2023"] - data["2022"]
    top10 = data.nlargest(10, "SELISIH")
    bot10 = data.nsmallest(10, "SELISIH")
    return [top10, bot10]


@st.cache_data
def proporsi(filter):
    kueri = f""" 
    select 
    p."NPWP15",
    p."NAMA_WP" , p."JENIS_WP",
    sum(p."NOMINAL") as "NETTO",
    sum(case when p."KET" in('MPN','SPM') then p."NOMINAL" end) as "BRUTO"
    from ppmpkm p 
    where {filter}
    group by p."NPWP15" ,p."NAMA_WP"  , p."JENIS_WP"
    order by "NETTO" desc
    """
    bruto_raw = conn.query(kueri)
    # bruto_nol = bruto[bruto['NPWP'].str.startswith('00000000')]
    row = bruto_raw.shape[0] + 1
    # # rowplus = row-len(brutomin)

    bruto = bruto_raw.drop(columns="JENIS_WP")
    bruto = (
        bruto.groupby(["NPWP15", "NAMA_WP"])
        .sum()
        .reset_index()
        .sort_values(by="NETTO", ascending=False)
    )
    bruto_a = bruto.nlargest(10, columns="NETTO")
    bruto_b = pd.DataFrame(
        [["Penerimaan 10 WP Terbesar", bruto_a["NETTO"].sum(), bruto_a["BRUTO"].sum()]],
        columns=["NAMA_WP", "NETTO", "BRUTO"],
    )
    bruto_c = pd.DataFrame(
        [
            [
                "Penerimaan 11 s.d. 100 WP Terbesar",
                bruto.iloc[10:100,]["NETTO"].sum(),
                bruto.iloc[10:100,]["BRUTO"].sum(),
            ]
        ],
        columns=["NAMA_WP", "NETTO", "BRUTO"],
    )
    bruto_d = pd.DataFrame(
        [
            [
                "Penerimaan 101 s.d. 500 WP Terbesar",
                bruto.iloc[100:500,]["NETTO"].sum(),
                bruto.iloc[100:500,]["BRUTO"].sum(),
            ]
        ],
        columns=["NAMA_WP", "NETTO", "BRUTO"],
    )
    bruto_e = pd.DataFrame(
        [
            [
                "Penerimaan 501 s.d. {} WP Terbesar".format(row),
                bruto.iloc[500:row,]["NETTO"].sum(),
                bruto.iloc[500:row,]["BRUTO"].sum(),
            ]
        ],
        columns=["NAMA_WP", "NETTO", "BRUTO"],
    )
    bruto_g = pd.DataFrame(
        [["Total", bruto["NETTO"].sum(), bruto["BRUTO"].sum()]],
        columns=["NAMA_WP", "NETTO", "BRUTO"],
    )
    bruto_ok = pd.concat(
        [bruto_a, bruto_b, bruto_c, bruto_d, bruto_e, bruto_g],
        axis=0,
        ignore_index=True,
    )
    bruto_ok["KONTRIBUSI"] = (bruto_ok["BRUTO"] / bruto["BRUTO"].sum()) * 100
    return [bruto_ok, bruto]


@st.cache_data
def growth_month(filter, filter22):
    cy_kueri = f""" 
    SELECT
        p."BULANBAYAR" ,
        sum(CASE WHEN p."KET" in('MPN','SPM') AND p."TAHUNBAYAR" = EXTRACT(YEAR FROM CURRENT_DATE) THEN p."NOMINAL" END) AS "CY_BRUTO",
        sum(CASE WHEN p."TAHUNBAYAR" =  EXTRACT(YEAR FROM CURRENT_DATE) THEN p."NOMINAL" END) AS "CY_NETTO" ,
        abs(sum(CASE WHEN p."KET" in('MPN','SPM') AND p."TAHUNBAYAR" =  EXTRACT(YEAR FROM CURRENT_DATE) THEN p."NOMINAL" END)) AS "CY_RESTITUSI"
    FROM
        ppmpkm p
    WHERE {filter} 
    GROUP BY
        p."BULANBAYAR"
    """
    py_kueri = f""" 
         SELECT
        p."BULANBAYAR" ,
        sum(CASE WHEN p."KET" in('MPN','SPM') AND p."TAHUNBAYAR" =  EXTRACT(YEAR FROM CURRENT_DATE)-1 THEN p."NOMINAL" END) AS "PY_BRUTO",
        sum(CASE WHEN p."TAHUNBAYAR" =  EXTRACT(YEAR FROM CURRENT_DATE)-1 THEN p."NOMINAL" END) AS "PY_NETTO" ,
        abs(sum(CASE WHEN p."KET" in('MPN','SPM') AND p."TAHUNBAYAR" =  EXTRACT(YEAR FROM CURRENT_DATE)-1 THEN p."NOMINAL" END)) AS "PY_RESTITUSI"
    FROM
        ppmpkm p
    WHERE {filter22} 
    GROUP BY
        p."BULANBAYAR"
    """

    cy_data = conn.query(cy_kueri)
    maks_bulan = cy_data["BULANBAYAR"].count()
    py_data = conn.query(py_kueri)
    data = cy_data.merge(py_data, on="BULANBAYAR", how="inner")
    data["Tumbuh Bruto"] = (
        (data["CY_BRUTO"] - data["PY_BRUTO"]) / data["PY_BRUTO"]
    ) * 100
    data["Tumbuh Netto"] = (
        (data["CY_NETTO"] - data["PY_NETTO"]) / data["PY_NETTO"]
    ) * 100
    data["Tumbuh Restitusi"] = (
        (data["CY_RESTITUSI"] - data["PY_RESTITUSI"]) / data["PY_RESTITUSI"]
    ) * 100
    data = data[["Tumbuh Bruto", "Tumbuh Netto", "Tumbuh Restitusi"]]
    data = data.transpose()
    data.columns = [calendar.month_name[i] for i in range(1, maks_bulan + 1)]
    return data


@st.cache_data
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


@st.cache_data
def target(kpp):
    target2023 = {
        "001": 608265424000,
        "002": 542401593000,
        "003": 1150993826000,
        "004": 843373880000,
        "005": 1481697044000,
        "007": 11518776933000,
        "008": 616125873000,
        "009": 1634143550000,
        "097": 9205955757000,
    }
    target2022 = {
        "001": 477310544000,
        "002": 1180601400000,
        "003": 1001261091000,
        "004": 679223200000,
        "005": 1041766662000,
        "007": 8574702940000,
        "008": 608619845000,
        "009": 1200824695000,
        "097": 7892063178000,
    }

    if kpp:
        target2023 = {key: target2023[key] for key in target2023.keys() if key in kpp}
        target2022 = {key: target2022[key] for key in target2022.keys() if key in kpp}
    else:
        target2023 = {"110": 27601733880000}
        target2022 = {"110": 22656373555000}
    return [target2023, target2022]


@st.cache_data
def cluster(filter, filter22, kpp):
    target2023 = {
        "001": 608265424000,
        "002": 542401593000,
        "003": 1150993826000,
        "004": 843373880000,
        "005": 1481697044000,
        "007": 11518776933000,
        "008": 616125873000,
        "009": 1634143550000,
        "097": 9205955757000,
    }
    target2022 = {
        "001": 477310544000,
        "002": 1180601400000,
        "003": 1001261091000,
        "004": 679223200000,
        "005": 1041766662000,
        "007": 8574702940000,
        "008": 608619845000,
        "009": 1200824695000,
        "097": 7892063178000,
    }

    if kpp:
        target2023 = {key: target2023[key] for key in target2023.keys() if key in kpp}
        target2022 = {key: target2022[key] for key in target2022.keys() if key in kpp}

    target2023 = (
        pd.DataFrame(data=target2023, index=["TARGET2023"]).transpose().reset_index()
    )
    target2022 = (
        pd.DataFrame(data=target2022, index=["TARGET2022"]).transpose().reset_index()
    )
    target = pd.merge(target2023, target2022, on="index", how="inner").rename(
        columns={"index": "ADMIN"}
    )

    kueri = f"""
        SELECT
        p."ADMIN" ,p."TAHUNBAYAR" ,
        sum("NOMINAL" )AS netto
        FROM
        ppmpkm p
        WHERE  {filter}
        GROUP BY p."ADMIN" ,p."TAHUNBAYAR"
        UNION ALL
        SELECT
        p."ADMIN" ,p."TAHUNBAYAR" ,
        sum("NOMINAL" )AS netto
        FROM
        ppmpkm p
        WHERE  {filter22}
        GROUP BY p."ADMIN" ,p."TAHUNBAYAR"
    """
    realisasi = conn.query(kueri)
    realisasi = (
        realisasi.pivot_table(
            index="ADMIN", columns="TAHUNBAYAR", values="netto", aggfunc="sum"
        )
        .reset_index()
        .rename(columns={2023: "REALISASI2023", 2022: "REALISASI2022"})
    )

    capaian = pd.merge(target, realisasi, on="ADMIN", how="inner")
    capaian = capaian.assign(
        capaian=(capaian["REALISASI2023"] / capaian["TARGET2023"]) * 100
    ).assign(
        tumbuh=(
            (capaian["REALISASI2023"] - capaian["REALISASI2022"])
            / capaian["TARGET2022"]
        )
        * 100
    )
    return capaian


def subsektor(filter, filter22):
    kueri = f"""
    SELECT 
    p."NM_KATEGORI" , p."NM_GOLPOK",p."NAMA_KLU" ,p."TAHUNBAYAR" ,
    sum(p."NOMINAL") "BRUTO"
    FROM 
    ppmpkm p 
    WHERE p."KET"  in('MPN','SPM')  AND  {filter}
    GROUP BY p."NM_KATEGORI" , p."NM_GOLPOK",p."NAMA_KLU", p."TAHUNBAYAR" 
    UNION ALL 
    SELECT 
    p."NM_KATEGORI" , p."NM_GOLPOK" ,p."NAMA_KLU", p."TAHUNBAYAR" ,
    sum(p."NOMINAL") "BRUTO"
    FROM 
    ppmpkm p 
    WHERE p."KET"  in('MPN','SPM') AND {filter22}
    GROUP BY p."NM_KATEGORI" , p."NM_GOLPOK",p."NAMA_KLU", p."TAHUNBAYAR"   """
    data = conn.query(kueri)
    data.rename(columns={"NM_GOLPOK": "Sub Sektor"}, inplace=True)
    data["TAHUNBAYAR"] = data["TAHUNBAYAR"].astype("str")
    data = data.pivot_table(
        index=["NM_KATEGORI", "Sub Sektor", "NAMA_KLU"],
        columns="TAHUNBAYAR",
        values="BRUTO",
        aggfunc="sum",
    ).reset_index()
    data = data.sort_values(by="2023", ascending=False)
    # data["Naik/Turun"] = data["2023"] - data["2022"]
    # data["Tumbuh"] = round((data["Naik/Turun"] / data["2022"]) * 100, 2)

    return data


def data_sankey(filter):
    kueri = f"""
    SELECT 
    p."NM_KATEGORI" , p."MAP" , sum(p."NOMINAL") 
    FROM 
    ppmpkm p 
    WHERE  {filter}
    GROUP BY p."NM_KATEGORI" , p."MAP" 
    """
    data = conn.query(kueri)
    data_node = pd.DataFrame(
        pd.concat(
            [pd.Series(data["NM_KATEGORI"].unique()), pd.Series(data["MAP"].unique())],
            ignore_index=True,
            axis=0,
        ),
        columns=["label"],
    ).reset_index()
    data = data.merge(
        data_node[["index", "label"]],
        left_on="NM_KATEGORI",
        right_on="label",
        how="left",
    )
    data = data.merge(
        data_node[["index", "label"]], left_on="MAP", right_on="label", how="left"
    )
    data.rename(
        columns={"index_x": "source", "index_y": "target", "sum": "value"}, inplace=True
    )
    data.drop(columns=["label_x", "label_y"], inplace=True)
    return [data, data_node]


def sankey_subsektor(df: pd.DataFrame, tab_subsektor):
    if tab_subsektor:
        df = df[df["NM_KATEGORI"] == tab_subsektor]
        node_subsektor = pd.DataFrame(
            pd.concat(
                [
                    pd.Series(df["NM_KATEGORI"].unique()),
                    pd.Series(df["Sub Sektor"].unique()),
                ],
                ignore_index=True,
                axis=0,
            ),
            columns=["label"],
        ).reset_index()
    else:
        df = df.copy()
        node_subsektor = pd.DataFrame(
            pd.concat(
                [
                    pd.Series(df["NM_KATEGORI"].unique()),
                    pd.Series(df["Sub Sektor"].unique()),
                ],
                ignore_index=True,
                axis=0,
            ),
            columns=["label"],
        ).reset_index()

    df = df.merge(
        node_subsektor[["index", "label"]],
        left_on="NM_KATEGORI",
        right_on="label",
        how="left",
    )
    df = df.merge(
        node_subsektor[["index", "label"]],
        left_on="Sub Sektor",
        right_on="label",
        how="left",
    )

    df.rename(
        columns={"index_x": "source", "index_y": "target", "sum": "value"}, inplace=True
    )
    df.drop(columns=["label_x", "label_y"], inplace=True)

    return [node_subsektor, df]


def generate_rgba_colors(n, a):
    colors = []
    for _ in range(n):
        r, g, b = random.uniform(1, 255), random.uniform(1, 255), random.uniform(1, 255)
        colors.append((r, g, b))
    colors = pd.DataFrame(colors, columns=["r", "g", "b"])
    colors.iloc[:, :] = colors.iloc[:, :].applymap(lambda x: "{:.0f}".format(x))

    colors["rgba"] = (
        "rgba("
        + colors["r"]
        + ","
        + colors["g"]
        + ","
        + colors["b"]
        + ","
        + str(a)
        + ")"
    )
    return colors


def top10kpp(filter_date, filter_date22, filter_cat):
    if filter_cat:
        kueri = f""" 
        WITH df AS (SELECT 
        p."NPWP15", p."NAMA_WP" , p."ADMIN" ,
        sum(CASE WHEN p."TAHUNBAYAR"=EXTRACT (YEAR FROM current_date) THEN p."NOMINAL" END )AS "CY", 
        sum(CASE WHEN p."TAHUNBAYAR"=EXTRACT (YEAR FROM current_date)-1 THEN p."NOMINAL" END )AS "PY",
        row_number() over(PARTITION BY "ADMIN" ORDER BY 
        sum(CASE WHEN p."TAHUNBAYAR"=EXTRACT (YEAR FROM current_date) THEN p."NOMINAL" END ) DESC) AS "URUT"
        FROM ppmpkm p 
        WHERE "KET" in('MPN','SPM')  AND "NPWP15" NOT LIKE '000000000%' and (({filter_date})or ({filter_date22})) and {filter_cat}
        GROUP BY p."NPWP15", p."NAMA_WP" ,p."ADMIN" 
        HAVING sum(CASE WHEN p."TAHUNBAYAR"=EXTRACT (YEAR FROM current_date) THEN p."NOMINAL" END ) NOTNULL )
        SELECT * , (("CY"-"PY")/"PY")*100 AS "TUMBUH"
        FROM df
        WHERE "URUT" <=10
        """
    else:
        kueri = f""" 
        WITH df AS (SELECT 
        p."NPWP15", p."NAMA_WP" , p."ADMIN" ,
        sum(CASE WHEN p."TAHUNBAYAR"=EXTRACT (YEAR FROM current_date) THEN p."NOMINAL" END )AS "CY", 
        sum(CASE WHEN p."TAHUNBAYAR"=EXTRACT (YEAR FROM current_date)-1 THEN p."NOMINAL" END )AS "PY",
        row_number() over(PARTITION BY "ADMIN" ORDER BY 
        sum(CASE WHEN p."TAHUNBAYAR"=EXTRACT (YEAR FROM current_date) THEN p."NOMINAL" END ) DESC) AS "URUT"
        FROM ppmpkm p 
        WHERE "KET" in('MPN','SPM')  AND "NPWP15" NOT LIKE '000000000%' and (({filter_date})or ({filter_date22}))
        GROUP BY p."NPWP15", p."NAMA_WP" ,p."ADMIN" 
        HAVING sum(CASE WHEN p."TAHUNBAYAR"=EXTRACT (YEAR FROM current_date) THEN p."NOMINAL" END ) NOTNULL )
        SELECT * , (("CY"-"PY")/"PY")*100 AS "TUMBUH"
        FROM df
        WHERE "URUT" <=10
        """
    data = conn.query(kueri)
    # data["TUMBUH"] = data["TUMBUH"].round(2)
    return data


def explore_data(filter_date, filter_date22, filter_cat) -> pd.DataFrame:
    if filter_cat:
        kueri = f"""
        SELECT 
        p."ADMIN" ,p."NAMA_WP" ,p."MAP",p."KDBAYAR" ,p."NM_KATEGORI",p."NM_GOLPOK" ,p."NAMA_KLU" , p."KET" ,
        p."BULANBAYAR" ,p."TAHUNBAYAR" ,p."DATEBAYAR" ,p."NAMA_AR" ,p."SEKSI" ,p."SEGMENTASI_WP" 
        ,sum(p."NOMINAL") as "NOMINAL"
        FROM  ppmpkm p 
        where {filter_cat} and({filter_date}) 
        GROUP BY p."ADMIN" ,p."NAMA_WP" ,p."MAP",p."KDBAYAR" ,p."NM_KATEGORI",p."NM_GOLPOK" ,p."NAMA_KLU" , p."KET" ,
        p."BULANBAYAR" ,p."TAHUNBAYAR" ,p."DATEBAYAR" ,p."NAMA_AR" ,p."SEKSI" ,p."SEGMENTASI_WP"
        ORDER BY sum(p."NOMINAL") desc
        """
    else:
        kueri = f"""
        SELECT 
        p."ADMIN" ,p."NAMA_WP" ,p."MAP",p."KDBAYAR" ,p."NM_KATEGORI",p."NM_GOLPOK" ,p."NAMA_KLU" , p."KET" ,
        p."BULANBAYAR" ,p."TAHUNBAYAR" ,p."DATEBAYAR" ,p."NAMA_AR" ,p."SEKSI" ,p."SEGMENTASI_WP"
        ,sum(p."NOMINAL") as "NOMINAL"
        FROM  ppmpkm p 
        where ({filter_date}) 
        GROUP BY p."ADMIN" ,p."NAMA_WP" ,p."MAP",p."KDBAYAR" ,p."NM_KATEGORI",p."NM_GOLPOK" ,p."NAMA_KLU" , p."KET" ,
        p."BULANBAYAR" ,p."TAHUNBAYAR" ,p."DATEBAYAR" ,p."NAMA_AR" ,p."SEKSI" ,p."SEGMENTASI_WP"
        ORDER BY sum(p."NOMINAL") desc
        """
    # data = pl.read_database(query=kueri, connection_uri=conn_uri, engine="adbc")
    data = conn.query(kueri)
    return data


def map_mom(filter):
    kueri = f"""
    SELECT 
    p."MAP" ,p."BULANBAYAR" , sum(p."NOMINAL") AS "NOMINAL" 
    FROM ppmpkm p 
    WHERE {filter} and p."KET" in('MPN','SPM')
    GROUP BY p."MAP" ,p."BULANBAYAR"
    ORDER BY p."MAP" ,p."BULANBAYAR" ASC 
"""
    data = conn.query(kueri)
    return data


def fetch_all():
    login = pd.read_sql("select * from public.users", con=conn_postgres)
    login_list = []
    for n in login.values:
        temp = tuple(n)
        login_list.insert(len(login_list), temp)
    return login_list


def kluxmap(filter):
    kueri = f""" 
     select p."NM_KATEGORI"::varchar,
       p."ADMIN"::varchar,
       p."MAP",
       p."KDBAYAR",
       p."TAHUNBAYAR" ,
       p."BULANBAYAR" ,
       p."NPWP15",
       p."NAMA_WP",
       sum(case when  p."KET" IN ('MPN', 'SPM') then p."NOMINAL" end) as "Bruto",
       sum( p."NOMINAL" )                               as "Netto"
from ppmpkm p
where {filter}
group by p."NM_KATEGORI"::varchar,
         p."ADMIN"::varchar,
         p."MAP",
         p."KDBAYAR",
         p."TAHUNBAYAR" ,
         p."BULANBAYAR",
         p."NPWP15",
         p."NAMA_WP"
    """
    data = conn.query(kueri)
    return data


def klu_rank(filter_date, filter_date22):
    kueri = f""" 
    SELECT 
    p."NAMA_KLU" ,
    sum(CASE WHEN p."TAHUNBAYAR" = date_part('year', current_date) THEN p."NOMINAL" END )"CY" ,
    sum(CASE WHEN p."TAHUNBAYAR" = (date_part('year', current_date)-1) THEN p."NOMINAL" END )"PY"
    FROM ppmpkm p 
    WHERE  p."KET" IN('MPN','SPM')
    AND (
            {filter_date}
        )
        or (
            {filter_date22}
            )
        
    GROUP BY p."NAMA_KLU" 
"""
    data = conn.query(kueri)
    data["Naik/Turun"] = data["CY"] - data["PY"]
    data["%"] = round((data["Naik/Turun"] / data["PY"]) * 100, 2)
    data.sort_values(by="Naik/Turun", ascending=False, inplace=True)
    return data


def tren_kwl(filter):
    kueri = f""" 
        select
       p."ADMIN"::varchar,
       p."SEKSI",
       p."NAMA_AR",
       p."TAHUNBAYAR" ,
       p."BULANBAYAR" ,
       sum(case when  p."KET" IN ('MPN', 'SPM') then p."NOMINAL" end) as "Bruto",
       sum( p."NOMINAL" )                               as "Netto"
        from ppmpkm p 
        where {filter} and p."SEGMENTASI_WP"='KEWILAYAHAN'
        group by
       p."ADMIN"::varchar,
       p."NM_KATEGORI"::varchar,
       p."MAP",
       p."SEKSI",
       p."NAMA_AR",
       p."TAHUNBAYAR" ,
       p."BULANBAYAR"
"""
    data = conn.query(kueri)
    return data


def detail_wp(filter_sekmap):
    kueri = f"""select
    p."NPWP15", p."NAMA_WP",p."TAHUNBAYAR",p."NAMA_KLU",p."BULANBAYAR",sum(p."NOMINAL")
    from ppmpkm p
    where p."TAHUNBAYAR" >=2021 and "NPWP15" not like '000000000%' and p."KET" in ('MPN','SPM')
    and {filter_sekmap}
    group by p."NPWP15",p."NAMA_WP",p."TAHUNBAYAR",p."NAMA_KLU",p."BULANBAYAR" """
    data = conn.query(kueri)
    return data


def stats_data():
    lastUpdate = conn.query('select max(p."DATEBAYAR") from ppmpkm p')
    return lastUpdate.iloc[0, 0]


if __name__ == "__main__":
    filter = """"DATEBAYAR">='2023-01-01' and"DATEBAYAR"<='2023-06-25' and"ADMIN" IN ('007') """
    filter22 = """ "DATEBAYAR">='2022-01-01' and"DATEBAYAR"<='2022-06-25' and"ADMIN" IN ('007') """
    *_, sektor_yo = sektor_yoy(filter, filter22, includewp=False)
    print(sektor_yo)
