import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import calendar
import streamlit as st

conn = st.experimental_connection("ppmpkm", type="sql")
dict_sektor = {
    "PERDAGANGAN BESAR DAN ECERAN; REPARASI DAN PERAWATAN MOBIL DAN SEPEDA MOTOR": "PERDAGANGAN BESAR ECERAN <br> REPARASI PERAWATAN MOBIL",
    "PENYEDIAAN AKOMODASI DAN PENYEDIAAN MAKAN MINUM": "PENYEDIAAN AKOMODASI<br>DAN PENYEDIAAN MAKAN MINUM",
    "PENGADAAN LISTRIK, GAS,UAP/AIR PANAS DAN UDARA DINGIN": "PENGADAAN LISTRIK, GAS,UAP/AIR PANAS<br>UDARA DINGIN",
    "PENGADAAN AIR, PENGELOLAAN SAMPAH DAN DAUR ULANG, PEMBUANGAN DAN PEMBERSIHAN LIMBAH DAN SAMPAH": "PENGADAAN AIR, PENGELOLAAN SAMPAH",
    "KEGIATAN BADAN INTERNASIONAL DAN BADAN EKSTRA INTERNASIONAL LAINNYA": "KEGIATAN BADAN INTERNASIONAL",
    "JASA PERSEWAAN, KETENAGAKERJAAN, AGEN PERJALANAN DAN PENUNJANG USAHA LAINNYA": "JASA PERSEWAAN, KETENAGAKERJAAN",
    "JASA PERORANGAN YANG MELAYANI RUMAH TANGGA; KEGIATAN YANG MENGHASILKAN BARANG DAN JASA OLEH RUMAH TANGGA YANG DIGUNAKAN SENDIRI UNTUK MEMENUHI KEBUTUHAN": "JASA PERORANGAN MELAYANI<br>RUMAH TANGGA",
    "ADMINISTRASI PEMERINTAHAN, PERTAHANAN DAN JAMINAN SOSIAL WAJIB": "ADMINISTRASI PEMERINTAHAN<br>JAMINAN SOSIAL WAJIB",
    "JASA PENDIDIKAN": "JASA PENDIDIKAN",
    "INFORMASI DAN KOMUNIKASI": "INFORMASI KOMUNIKASI",
    "TRANSPORTASI DAN PERGUDANGAN": "TRANSPORTASI DAN PERGUDANGAN",
    "JASA KESEHATAN DAN KEGIATAN SOSIAL": "JASA KESEHATAN DAN KEGIATAN SOSIAL",
    "KONSTRUKSI": "KONSTRUKSI",
    "REAL ESTAT": "REAL ESTAT",
    "KEGIATAN JASA LAINNYA": "KEGIATAN JASA LAINNYA",
    "INDUSTRI PENGOLAHAN": "INDUSTRI PENGOLAHAN",
    "KLU ERROR": "KLU ERROR",
    "PERTAMBANGAN DAN PENGGALIAN": "PERTAMBANGAN DAN PENGGALIAN",
    "JASA KEUANGAN DAN ASURANSI": "JASA KEUANGAN DAN ASURANSI",
    "PERTANIAN, KEHUTANAN DAN PERIKANAN": "PERTANIAN,KEHUTANAN,PERIKANAN",
    "JASA PROFESIONAL, ILMIAH DAN TEKNIS": "JASA PROFESIONAL,ILMIAH,TEKNIS",
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
                sum(CASE WHEN p."KET" != 'SPMKP' THEN p."NOMINAL" END ) AS "BRUTO",
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
def sektor_yoy(filter, filter2, includewp: bool):
    if includewp:
        kueri = f"""
        SELECT p."NAMA_WP",
        p."NM_KATEGORI" ,p."TAHUNBAYAR",p."BULANBAYAR", sum(p."NOMINAL") AS "NOMINAL"
        FROM 
        ppmpkm p 
        WHERE p."KET" !='SPMKP' and {filter}
        GROUP BY p."NAMA_WP",p."NM_KATEGORI" ,p."TAHUNBAYAR",p."BULANBAYAR"
        UNION ALL 
        SELECT p."NAMA_WP",
        p."NM_KATEGORI" , p."TAHUNBAYAR",p."BULANBAYAR", sum(p."NOMINAL") AS "NOMINAL"
        FROM 
        ppmpkm p 
        WHERE p."KET" !='SPMKP' and {filter2}
        GROUP BY p."NAMA_WP",p."NM_KATEGORI" ,p."TAHUNBAYAR",p."BULANBAYAR"
        """
        data = conn.query(kueri)
        # if data["NOMINAL"].sum() > 0:
        # data["NM_KATEGORI"] = data["NM_KATEGORI"].map(dict_sektor)
        data["TAHUNBAYAR"] = data["TAHUNBAYAR"].astype("str")

        sektor_yoy = data.pivot_table(
            index=["NAMA_WP", "NM_KATEGORI"], columns="TAHUNBAYAR", values="NOMINAL"
        ).reset_index()
        data.columns = [x.strip() for x in data.columns]

        sektor_yoy = sektor_yoy.sort_values(by="2023", ascending=False)

        sektor_yoy["selisih"] = sektor_yoy["2023"] - sektor_yoy["2022"]
        sektor_yoy["tumbuh"] = sektor_yoy["selisih"] / sektor_yoy["2022"]

        sektor_mom = data[data["TAHUNBAYAR"] == 2023]
        sektor_mom = (
            data.groupby(["NAMA_WP", "NM_KATEGORI", "BULANBAYAR"])["NOMINAL"]
            .sum()
            .reset_index()
        )
    else:
        kueri = f"""
        SELECT 
        p."NM_KATEGORI" ,p."TAHUNBAYAR",p."BULANBAYAR", sum(p."NOMINAL") AS "NOMINAL"
        FROM 
        ppmpkm p 
        WHERE p."KET" !='SPMKP' and {filter}
        GROUP BY p."NM_KATEGORI" ,p."TAHUNBAYAR",p."BULANBAYAR"
        UNION ALL 
        SELECT 
        p."NM_KATEGORI" , p."TAHUNBAYAR",p."BULANBAYAR", sum(p."NOMINAL") AS "NOMINAL"
        FROM 
        ppmpkm p 
        WHERE p."KET" !='SPMKP' and {filter2}
        GROUP BY p."NM_KATEGORI" ,p."TAHUNBAYAR",p."BULANBAYAR"
        """
        data = conn.query(kueri)
        # if data["NOMINAL"].sum() > 0:
        data["NM_KATEGORI"] = data["NM_KATEGORI"].map(dict_sektor)
        data["TAHUNBAYAR"] = data["TAHUNBAYAR"].astype("str")

        sektor_yoy = data.pivot_table(
            index=["NM_KATEGORI"], columns="TAHUNBAYAR", values="NOMINAL"
        ).reset_index()
        # data.columns = [x.strip() for x in data.columns]

        sektor_yoy = sektor_yoy.sort_values(by="2023", ascending=False)
        sektor_yoy["selisih"] = sektor_yoy["2023"] - sektor_yoy["2022"]
        sektor_yoy["tumbuh"] = sektor_yoy["selisih"] / sektor_yoy["2022"]

        sektor_mom = data[data["TAHUNBAYAR"] == 2023]
        sektor_mom = (
            data.groupby(["NM_KATEGORI", "BULANBAYAR"])["NOMINAL"].sum().reset_index()
        )
    # else:
    #     sektor_yoy = pd.DataFrame(
    #         [["", "", "", ""]], columns=["NAMA_WP", "NM_KATEGORI", "2023", "2022"]
    #     )
    #     sektor_yoy["selisih"] = 0
    #     sektor_yoy["tumbuh"] = 0
    #     sektor_mom = pd.DataFrame(
    #         [["", "", "", ""]], columns=["NAMA_WP", "NM_KATEGORI", "2023", "2022"]
    #     )
    #     sektor_mom["selisih"] = 0
    #     sektor_mom["tumbuh"] = 0

    return [sektor_yoy, sektor_mom]


@st.cache_data
def sektor2023(filter):
    kueri = f"""
    SELECT 
    p."DATEBAYAR",p."NM_KATEGORI" , sum(p."NOMINAL") AS "NOMINAL"
    FROM 
    ppmpkm p 
    WHERE p."KET" !='SPMKP' and {filter}
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
        WHERE  p."KET" !='SPMKP' and {filter}
        GROUP BY p."NM_KATEGORI",p."NAMA_KLU" 
        ORDER BY sum(p."NOMINAL")"""
    klu = conn.query(kueri)
    return klu


def jenis_pajak(filter, filter22):
    kueri = f"""
    SELECT 
    p."MAP" , p."TAHUNBAYAR",sum(p."NOMINAL") AS "BRUTO" 
    FROM 
    public.ppmpkm p 
    WHERE {filter} and p."KET" !='SPMKP'
    GROUP BY p."MAP" ,p."TAHUNBAYAR"
    UNION ALL
    SELECT 
    p."MAP" , p."TAHUNBAYAR", sum(p."NOMINAL") AS "BRUTO" 
    FROM 
    public.ppmpkm p 
    WHERE {filter22} and p."KET" !='SPMKP'
    GROUP BY p."MAP" ,p."TAHUNBAYAR" 
    """
    jenis = conn.query(kueri)
    jenis = jenis.groupby(["MAP", "TAHUNBAYAR"])["BRUTO"].sum().reset_index()
    jenis["TAHUNBAYAR"] = jenis["TAHUNBAYAR"].astype("str")
    # jenis = pd.pivot_table(jenis, index="MAP", columns="TAHUNBAYAR", values="BRUTO")
    # jenis.drop(columns="index", inplace=True)

    return jenis


def kjs(filter):
    kueri = f""" 
        SELECT
        p."MAP",p."KDBAYAR" ,sum(p."NOMINAL") as "BRUTO"
        FROM 
        ppmpkm p
        WHERE  p."KET" !='SPMKP' and {filter}
        GROUP BY p."MAP",p."KDBAYAR"  """
    kjs = conn.query(kueri)
    return kjs


@st.cache_data
def kpi(filter, filter22, filter_date, filter_date22):
    mpn23 = conn.query(
        f""" SELECT
            sum( CASE WHEN p."KET" != 'SPMKP' THEN p."NOMINAL" END) AS "BRUTO" ,
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
            sum( CASE WHEN p."KET" != 'SPMKP' THEN p."NOMINAL" END) AS "BRUTO" ,
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
	p."NPWP",
	p."NAMA_WP",
    p."TAHUNBAYAR",
	SUM (p."NOMINAL") AS "NOMINAL"
    FROM
        ppmpkm p
    WHERE
        p."KET" !='SPMKP' AND {filter}
    GROUP BY
        p."NPWP",
        p."NAMA_WP",
        p."TAHUNBAYAR"
    UNION ALL
         SELECT
	p."NPWP",
	p."NAMA_WP",
    p."TAHUNBAYAR",
	SUM (p."NOMINAL") AS "NOMINAL"
    FROM
        ppmpkm p
    WHERE
        p."KET" !='SPMKP' AND {filter22}
    GROUP BY
        p."NPWP",
        p."NAMA_WP",
        p."TAHUNBAYAR"
        """
    data = conn.query(kueri)
    data["TAHUNBAYAR"] = data["TAHUNBAYAR"].astype("str")
    # data = (
    #     data.groupby(["NPWP", "NAMA_WP", "TAHUNBAYAR"])["NOMINAL"].sum().reset_index()
    # )
    data = data.pivot_table(
        index=["NPWP", "NAMA_WP"], columns="TAHUNBAYAR", values="NOMINAL"
    ).reset_index()

    data["SELISIH"] = data["2023"] - data["2022"]
    top10 = data.nlargest(10, "SELISIH")
    bot10 = data.nsmallest(10, "SELISIH")
    return [top10, bot10]


@st.cache_data
def proporsi(filter):
    kueri = f""" 
    select 
    p."NPWP",
    p."NAMA_WP" , 
    sum(p."NOMINAL") as "BRUTO"
    from ppmpkm p 
    where p."KET" in('MPN','SPM') and {filter}
    group by p."NPWP" ,p."NAMA_WP" 
    order by "BRUTO" desc
    """
    bruto = conn.query(kueri)
    # bruto_nol = bruto[bruto['NPWP'].str.startswith('00000000')]
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
    bruto_ok = pd.concat(
        [bruto_a, bruto_b, bruto_c, bruto_d, bruto_e, bruto_g],
        axis=0,
        ignore_index=True,
    )
    bruto_ok["KONTRIBUSI"] = bruto_ok["BRUTO"] / bruto["BRUTO"].sum()
    return [bruto_ok, bruto]


@st.cache_data
def growth_month(filter, filter22):
    cy_kueri = f""" 
    SELECT
        p."BULANBAYAR" ,
        sum(CASE WHEN p."KET" != 'SPMKP' AND p."TAHUNBAYAR" = EXTRACT(YEAR FROM CURRENT_DATE) THEN p."NOMINAL" END) AS "CY_BRUTO",
        sum(CASE WHEN p."TAHUNBAYAR" =  EXTRACT(YEAR FROM CURRENT_DATE) THEN p."NOMINAL" END) AS "CY_NETTO" ,
        abs(sum(CASE WHEN p."KET" = 'SPMKP' AND p."TAHUNBAYAR" =  EXTRACT(YEAR FROM CURRENT_DATE) THEN p."NOMINAL" END)) AS "CY_RESTITUSI"
    FROM
        ppmpkm p
    WHERE {filter} 
    GROUP BY
        p."BULANBAYAR"
    """
    py_kueri = f""" 
         SELECT
        p."BULANBAYAR" ,
        sum(CASE WHEN p."KET" != 'SPMKP' AND p."TAHUNBAYAR" =  EXTRACT(YEAR FROM CURRENT_DATE)-1 THEN p."NOMINAL" END) AS "PY_BRUTO",
        sum(CASE WHEN p."TAHUNBAYAR" =  EXTRACT(YEAR FROM CURRENT_DATE)-1 THEN p."NOMINAL" END) AS "PY_NETTO" ,
        abs(sum(CASE WHEN p."KET" = 'SPMKP' AND p."TAHUNBAYAR" =  EXTRACT(YEAR FROM CURRENT_DATE)-1 THEN p."NOMINAL" END)) AS "PY_RESTITUSI"
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
        realisasi.pivot_table(index="ADMIN", columns="TAHUNBAYAR", values="netto")
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


if __name__ == "__main__":
    sektor_yoy()
