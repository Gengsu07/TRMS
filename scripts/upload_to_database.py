import streamlit_authenticator as stauth

import database as db
import pandas as pd

data = pd.read_excel(
    r"C:\Users\sugengw07\OneDrive - Kemenkeu\KANWILJAKTIM\DATA\pegawai110.xlsx",
    dtype={"NIP": "str"},
)
data["Password"] = data["NIP"] + "@" + "110"

usernames = data["NIP"].tolist()
names = data["Nama"].tolist()
passwords = data["Password"]
hashed_passwords = stauth.Hasher(passwords).generate()

i = 1
for username, name, hash_password in zip(usernames, names, hashed_passwords):
    print(i)
    db.insert_user(username, name, hash_password)
    i += 1
