import pandas as pd
from sqlalchemy import create_engine

postgres = create_engine('postgresql+psycopg2://postgres:sgwi2341@localhost:5432/jaktim')

df = pd.read_parquet("D:\DATA\data.parquet")
df.to_sql('ppmpkm', index=False, con=postgres)



