import streamlit_authenticator as stauth
import pandas as pd
import sqlite3

conn_sqlite = sqlite3.connect("login.db")
c = conn_sqlite.cursor()
url_data = r"C:\Users\sugengw07\OneDrive - Kemenkeu\KANWILJAKTIM\DATA\pegawai110.xlsx"


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
    c.execute(
        "INSERT INTO users(username, name, password, adm) VALUES(?,?,?,?)",
        (username, name, hash_password, adm),
    )
    conn_sqlite.commit()


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
