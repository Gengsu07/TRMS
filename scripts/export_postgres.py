from sqlalchemy import create_engine
from urllib.parse import quote_plus

password = quote_plus('kwl@110')
postgre_con = create_engine("postgresql://oc:{}@10.20.254.228/penerimaan".format(password))


def export_postgres(df: object, sql_table: object = postgre_con, schema: object = 'public', index: object = False) -> object:
    """_summary_

    Args:
        df (_type_): dataframe yg akan diexport
        sql_table (_type_, optional): nama table.
        schema (str, optional): nama schema. Defaults to 'public'.
    """
    df.to_sql(sql_table,
              con=postgre_con, 
              schema=schema, 
              index=index,
              if_exists='replace')
    print(f'LOAD TO POSTGRES {sql_table}:OK')
    