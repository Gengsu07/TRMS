import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
password = quote_plus('kwl@110')
postgres = create_engine(
    f'postgresql+psycopg2://oc:{password}@10.20.254.228:5432/penerimaan')


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
    bruto = pd.read_sql(kueri, con=postgres)
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
