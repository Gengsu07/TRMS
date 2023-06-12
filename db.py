import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import streamlit as st
# password = quote_plus('kwl@110')
# postgres = create_engine(
#     f'postgresql+psycopg2://oc:{password}@10.20.254.228:5432/penerimaan')
conn = st.experimental_connection('ppmpkm', type='sql')
dict_sektor = {
    'PERDAGANGAN BESAR DAN ECERAN; REPARASI DAN PERAWATAN MOBIL DAN SEPEDA MOTOR': 'PERDAGANGAN BESAR ECERAN<br>REPARASI PERAWATAN MOBIL',
    'PENYEDIAAN AKOMODASI DAN PENYEDIAAN MAKAN MINUM': 'PENYEDIAAN AKOMODASI<br>DAN PENYEDIAAN MAKAN MINUM',
    "PENGADAAN LISTRIK, GAS,UAP/AIR PANAS DAN UDARA DINGIN": "PENGADAAN LISTRIK, GAS,UAP/AIR PANAS<br>UDARA DINGIN",
    "PENGADAAN AIR, PENGELOLAAN SAMPAH DAN DAUR ULANG, PEMBUANGAN DAN PEMBERSIHAN LIMBAH DAN SAMPAH": "PENGADAAN AIR, PENGELOLAAN SAMPAH",
    "KEGIATAN BADAN INTERNASIONAL DAN BADAN EKSTRA INTERNASIONAL LAINNYA": "KEGIATAN BADAN INTERNASIONAL",
    "JASA PERSEWAAN, KETENAGAKERJAAN, AGEN PERJALANAN DAN PENUNJANG USAHA LAINNYA": "JASA PERSEWAAN, KETENAGAKERJAAN",
    "JASA PERORANGAN YANG MELAYANI RUMAH TANGGA; KEGIATAN YANG MENGHASILKAN BARANG DAN JASA OLEH RUMAH TANGGA YANG DIGUNAKAN SENDIRI UNTUK MEMENUHI KEBUTUHAN": "JASA PERORANGAN MELAYANI<br>RUMAH TANGGA",
    "ADMINISTRASI PEMERINTAHAN DAN JAMINAN SOSIAL WAJIB": "ADMINISTRASI PEMERINTAHAN<br>JAMINAN SOSIAL WAJIB",
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
    "JASA PROFESIONAL, ILMIAH DAN TEKNIS": "JASA PROFESIONAL,ILMIAH,TEKNIS"
}


def bruto(filter):
    kueri = f''' 
    select 
    p."NPWP",
    p."NAMA_WP" , 
    sum(p."NOMINAL") as "BRUTO"
    from ppmpkm p 
    where 
    p."KET" in ('MPN','SPM','PBK KIRIM','PBK TERIMA') and {filter}
    group by p."NPWP" ,p."NAMA_WP" 
    order by "BRUTO" desc
    '''
    bruto = conn.query(kueri)
    # brutomin = bruto[bruto['BRUTO']<0].index.tolist()
    row = bruto.shape[0]+1
    # rowplus = row-len(brutomin)

    bruto_a = bruto.nlargest(10, columns='BRUTO')
    bruto_b = pd.DataFrame(
        [['Penerimaan 10 WP Terbesar', bruto_a['BRUTO'].sum()]], columns=['NAMA_WP', 'BRUTO'])
    bruto_c = pd.DataFrame([['Penerimaan 11 s.d. 100 WP Terbesar',
                           bruto.iloc[10:100,]['BRUTO'].sum()]], columns=['NAMA_WP', 'BRUTO'])
    bruto_d = pd.DataFrame([['Penerimaan 101 s.d. 500 WP Terbesar',
                           bruto.iloc[100:500,]['BRUTO'].sum()]], columns=['NAMA_WP', 'BRUTO'])
    bruto_e = pd.DataFrame([['Penerimaan 501 s.d. {} WP Terbesar'.format(
        row), bruto.iloc[500:row,]['BRUTO'].sum()]], columns=['NAMA_WP', 'BRUTO'])
    # bruto_nol= pd.DataFrame([['Penerimaan Non WP ADM',bruto_nol['BRUTO'].sum()]],columns=['NAMA_WP','BRUTO'])
    # bruto_e = pd.DataFrame([['Penerimaan 501 s.d. {} WP Terbesar'.format(rowplus),bruto.iloc[501:min(brutomin),]['BRUTO'].sum()]],columns=['NAMA_WP','BRUTO'])
    # bruto_f = pd.DataFrame([['Penerimaan Kurang dari 0',bruto.iloc[min(brutomin):,]['BRUTO'].sum()]],columns=['NAMA_WP','BRUTO'])
    # bruto_x = pd.DataFrame([['{} WP Pusat dan Cabang Penerimaan 0'.format(bruto_nol),'']],columns=['NAMA_WP','bruto'])
    bruto_g = pd.DataFrame([['Total', bruto['BRUTO'].sum()]], columns=[
                           'NAMA_WP', 'BRUTO'])
    # bruto_g = pd.DataFrame([['Total',bruto['bruto'].sum()]],columns=['NAMA_WP','bruto'])

    bruto_ok = pd.concat([bruto_a, bruto_b, bruto_c, bruto_d,
                         bruto_e, bruto_g], axis=0, ignore_index=True)
    bruto_ok['KONTRIBUSI'] = (bruto_ok['BRUTO']/bruto['BRUTO'].sum())*100
    return bruto_ok


def sektor(filter):
    data_sektor = conn.query(f'''
        SELECT 
        kat."NM_KATEGORI", kat."NETTO",sum(kat."BRUTO")
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
        ORDER BY sum(kat."BRUTO") ASC ''')

    data_sektor['NM_KATEGORI'] = data_sektor['NM_KATEGORI'].map(dict_sektor)
    return data_sektor


def sektor_yoy(filter, filter2):
    kueri = f'''
    SELECT 
    p."NM_KATEGORI" ,p."TAHUNBAYAR", sum(p."NOMINAL") AS "NOMINAL"
    FROM 
    ppmpkm p 
    WHERE p."KET" !='SPMKP' and {filter}
    GROUP BY p."NM_KATEGORI" ,p."TAHUNBAYAR"
    UNION ALL 
    SELECT 
    p."NM_KATEGORI" , p."TAHUNBAYAR", sum(p."NOMINAL") AS "NOMINAL"
    FROM 
    ppmpkm p 
    WHERE p."KET" !='SPMKP' and {filter2}
    GROUP BY p."NM_KATEGORI" ,p."TAHUNBAYAR"
    '''
    data = conn.query(kueri)
    data['NM_KATEGORI'] = data['NM_KATEGORI'].map(dict_sektor)
    data['TAHUNBAYAR'] = data['TAHUNBAYAR'].astype('str')
    data = data.pivot_table(index=['NM_KATEGORI'],
                            columns='TAHUNBAYAR', values='NOMINAL').reset_index()
    # data.columns = [x.strip() for x in data.columns]
    data['selisih'] = data['2023']-data['2022']
    data['tumbuh'] = (data['selisih']/data['2022'])*100
    data = data.sort_values(by='2023', ascending=False)
    return data


def sektor2023(filter):
    kueri = f'''
    SELECT 
    p."DATEBAYAR",p."NM_KATEGORI" , sum(p."NOMINAL") AS "NOMINAL"
    FROM 
    ppmpkm p 
    WHERE p."KET" !='SPMKP' and {filter}
    GROUP BY p."DATEBAYAR",p."NM_KATEGORI" 
    '''
    sektor2023 = conn.query(kueri)
    return sektor2023


def jenis_pajak(filter):
    kueri = f'''
    SELECT 
    p."MAP" , sum(p."NOMINAL") AS "NETTO" 
    FROM 
    public.ppmpkm p 
    WHERE {filter}
    GROUP BY p."MAP" 
    ORDER BY sum(p."NOMINAL") DESC  
    '''
    jenis = conn.query(kueri)
    return jenis
