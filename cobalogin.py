import streamlit as st
import sqlite3
import hashlib

conn_sqlite = sqlite3.connect("credentials.db")
c = conn_sqlite.cursor()


c.execute("select * from user")
users = c.fetchall()
usernames = [user[0] for user in users]
names = [user[1] for user in users]
hashed_passwords = [user[2] for user in users]
email = [" "] * len(names)

zip_dict = dict(zip(usernames, zip(email, names, hashed_passwords)))


print(zip_dict)

for user in zip_dict:
    temp = {"usernames": {zip_dict[user]["email"][0]: zip_dict[user][0]}}
print(temp)


# for username, name, mail, hash_passwords in zip_dict:
# cred.update(dict(zip(username, zip(mail, name, hash_passwords))))

# authenticator = stauth.Authenticate(
#     cred,
#     cookie_name="KilauJaktim@110",
#     key="byGengsu@110",
#     cookie_expiry_days=30,
# )

# name, authentication_status, username = authenticator.login("👋Login-TRMS👋", "main")
# return name, authentication_status, username

# def make_hashes(password):
# 	return hashlib.sha256(str.encode(password)).hexdigest()
# def check_hashes(password,hashed_text):
# 	if make_hashes(password) == hashed_text:
# 		return hashed_text
# 	return False
# def login(username, password):
# 	c.execute('SELECT * FROM user WHERE username=? AND password=?',(username, password))
# 	data = c.fetchall()
# 	return data

# username = st.text_input('Masukkan NIP')
# password = st.text_input('Password')
# login_btn = st.button('Login')
# if login_btn :
# 	hashed_passw = make_hashes(password)
# 	cek_login = login(username, check_hashes(password, hashed_passw))
# 	if cek_login:
# 		st.success('')
# with open(".streamlit/login.yaml") as file:
#     config = yaml.load(file, Loader=SafeLoader)
