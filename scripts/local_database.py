import streamlit_authenticator as stauth
import pandas as pd
import sqlite3
import psycopg2
from urllib.parse import quote_plus

password = quote_plus("kwl@110")
postgre_con = "postgres://oc:{}@10.20.254.228/penerimaan".format(password)
pg_conn = psycopg2.connect(postgre_con)
cur = pg_conn.cursor()

conn_sqlite = sqlite3.connect("login.db")
c = conn_sqlite.cursor()
url_data = r"D:\DATA\adduser.xlsx"


def read_data(url_data):
    data = pd.read_excel(
        url_data,
        dtype={"NIP": "str", "Adm": "str"},
    )
    data["Password"] = data["NIP"] + "@" + "110"

    usernames = data["NIP"].tolist()
    names = data["Nama"].tolist()
    passwords = data["Password"]
    hashed_passwords = stauth.Hasher(passwords).generate()
    adm = data["Adm"].tolist()
    return usernames, names, hashed_passwords, adm


def insert_user(username, name, hash_password, adm):
    cur.execute(
        "INSERT INTO trms.users(username, name, password, adm) VALUES(%s,%s,%s,%s)",
        (username, name, hash_password, adm),
    )
    pg_conn.commit()


def create_table():
    c.execute(
        "CREATE TABLE IF NOT EXISTS users(username TEXT,name TEXT,password TEXT, adm TEXT )"
    )


def fetch_all():
    c.execute("SELECT * FROM users")
    data = c.fetchall()
    return data


# create_table()
if __name__ == "__main__":
    # create_table()

    usernames, names, hashed_passwords, adm = read_data(url_data)
    i = 1
    for username, name, hash_password, kdkpp in zip(
        usernames, names, hashed_passwords, adm
    ):
        print(i)
        insert_user(username, name, hash_password, kdkpp)

        i += 1
