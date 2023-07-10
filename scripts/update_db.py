from sqlalchemy import create_engine
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime
from urllib.parse import quote_plus
import pytz

# from realisasi import alco_perbulan
load_dotenv()
postgres_username = os.environ.get("POSTGRES_USERNAME")
postgres_password = os.environ.get("POSTGRES_PASSWORD")
postgres_url = os.environ.get("POSTGRES_URL")
postgres_table = os.environ.get("POSTGRES_TABLE")
password = quote_plus(f"{postgres_password}")
conn_postgres = create_engine(
    f"postgresql://{postgres_username}:{password}@{postgres_url}/{postgres_table}"
)
mysql_username = os.environ.get("MYSQL_USERNAME")
mysql_password = os.environ.get("MYSQL_PASSWORD")
mysql_url = os.environ.get("MYSQL_URL")
mysql_table = os.environ.get("MYSQL_TABLE")
mpninfo_con = create_engine(
    f"mysql://{mysql_username}:{mysql_password}@{mysql_url}:3306/{mysql_table}"
)


def kdmap(df):
    kdmap_kueri = """ 
    select "KDMAP","MAP" from dimensi.map_polos
    """
    kdmap = pd.read_sql(kdmap_kueri, conn_postgres)
    df = df.merge(kdmap, on="KDMAP", how="left")
    return df


def union_data():
    kueri = """
    SELECT admin,
    npwp,
    kpp,
    cabang,
    nama,
    kdmap,
    kdbayar,
    masa,
    masa2,
    tahun,
    tanggalbayar,
    bulanbayar,
    tahunbayar,
    datebayar,
    nominal,
    ntpn,
    bank,
    nosk,
    nospm,
    CASE WHEN SOURCE = 1 THEN 'MPN' ELSE 'SPM' END AS ket 
    FROM MPN WHERE TAHUNBAYAR>2020
    UNION ALL 
    SELECT admin,
    npwp,
    kpp,
    cabang,
    '',
    kdmap,
    '',
    '',
    '',
    '',
    DAY(tanggal) AS TANGGALBAYAR,
    BULAN,
    TAHUN,
    tanggal,
    NOMINAL*-1,
    '',
    '',
    '',
    '',
    'SPMKP' AS 'ket' 
    FROM spmkp WHERE TAHUN>2020
    UNION ALL 
    SELECT A.admin,
    A.npwp,
    A.kpp,
    A.cabang,
    A.nama,
    kdmap,
    kdbayar,
    masapajak,
    masapajak,
    tahunpajak,
    DAY(TANGGALDOC) AS TANGGALBAYAR,
    MONTH(TANGGALDOC) BULAN,
    YEAR(TANGGALDOC) TAHUN,
    TANGGALDOC,
    NOMINAL*-1 as "NOMINAL",
    ntpn,
    '',
    nopbk,
    '',
    'PBK KIRIM' AS ket 
    FROM PBK A 
    WHERE admin = kpp_admin AND kpp_admin = admin and TAHUN in('2021','2022','2023')
    UNION ALL 
    SELECT A.ADMIN,
    npwp2,
    kpp2,
    cabang2,
    nama2,
    kdmap2,
    kdbayar2,
    masapajak2,
    masapajak2,
    tahunpajak2,
    DAY(TANGGALDOC) AS TANGGALBAYAR,
    MONTH(TANGGALDOC) BULAN,
    YEAR(TANGGALDOC) TAHUN,
    TANGGALDOC,
    NOMINAL,
    ntpn,
    '',
    nopbk,
    '',
    'PBK TERIMA' AS ket 
    FROM PBK A 
    WHERE admin = kpp_admin2 AND kpp_admin2 = admin and TAHUN in('2021','2022','2023')
    """
    gabungan = pd.read_sql(kueri, mpninfo_con)
    print("READ & QUERy FROM MYSQL :OK")
    return gabungan


def etl(df):
    mfwp_kueri = """ 
    SELECT
	m.NPWP15,
	m.KPPADM ,
	m.NAMA_WP ,
	m.NAMA_AR ,
	m.SEKSI ,
	m.SEGMENTASI_WP 
    ,
	m.JENIS_WP,
	m.KODE_KLU ,
	m.NAMA_KLU ,
	dk.KD_KATEGORI ,
	dk.NM_KATEGORI ,
	dk.KD_GOLPOK ,
	dk.NM_GOLPOK
    FROM
        registrasi.sidjp_masterfile m
    LEFT JOIN dimensi.dim_klu dk ON
	m.KODE_KLU = dk.KD_KLU
    """
    kdmap_kueri = """ 
    select "KDMAP","MAP" from dimensi.map_polos
    """
    kdmap = pd.read_sql(kdmap_kueri, conn_postgres)
    data = df
    data["npwpfull"] = data["npwp"] + data["kpp"] + data["cabang"]
    data.drop(columns=["npwp", "kpp", "cabang"], inplace=True)
    data.rename(columns={"npwpfull": "npwp"}, inplace=True)
    mfwp = pd.read_sql(mfwp_kueri, con=mpninfo_con)
    data.columns = [column.upper() for column in data.columns]
    print("===READ DATA:OK===")
    gabungan = data.merge(mfwp, left_on="NPWP", right_on="NPWP15", how="left")
    gabungan.drop(columns=["NAMA"], inplace=True)
    gabungan["tahunsk"] = gabungan["NOSK"].str[-2:]
    gabungan["tahunsk"] = gabungan["tahunsk"].fillna(0)
    gabungan["tahunsk"] = gabungan["tahunsk"].replace(["", "-", "0ui", "ui", "J."], 0)
    gabungan["tahunsk"] = gabungan["tahunsk"].astype("int")
    kpp = {
        "001": "PRATAMA JAKARTA MATRAMAN",
        "002": "PRATAMA JAKARTA JATINEGARA",
        "003": "PRATAMA JAKARTA PULOGADUNG",
        "004": "PRATAMA JAKARTA CAKUNG",
        "005": "PRATAMA JAKARTA KRAMATJATI",
        "007": "MADYA JAKARTA TIMUR",
        "008": "PRATAMA JAKARTA DUREN SAWIT",
        "009": "PRATAMA JAKARTA PASAR REBO",
        "097": "MADYA DUA JAKARTA TIMUR",
    }
    gabungan["KPP"] = gabungan["ADMIN"].map(kpp)
    gabungan.columns = [column.upper() for column in gabungan.columns]
    gabungan["TAHUN"] = gabungan["TAHUN"].str.replace("", "0")
    gabungan["TAHUN"] = gabungan["TAHUN"].str.replace("-", "0")
    gabungan["TAHUN"] = gabungan["TAHUN"].astype("int")
    gabungan = gabungan.merge(kdmap, on="KDMAP", how="left")
    print("===TRANSFORM DATA:OK===")
    return gabungan


if __name__ == "__main__":
    union = union_data()

    data = etl(union)

    data.fillna("", inplace=True)
    print("WAIT LOAD TO POSTGRES")

    data.to_sql(
        "ppmpkm", con=conn_postgres, schema="public", index=False, if_exists="replace"
    )
    tz_jkt = pytz("Asia/Jakarta")
    print(f'SUKSESS at:{datetime.now(tz_jkt).strftime("%m/%d/%Y, %H:%M:%S")}')
    # export_postgres(data, sql_table="ppmpkm", schema="public")
