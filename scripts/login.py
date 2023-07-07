import streamlit as st
from PIL import Image
import sqlite3
import random
import string
import hashlib

conn_sqlite = sqlite3.connect("credentials.db")
c = conn_sqlite.cursor()


def unique_key(seed: int):
    random.seed(seed)
    return random.choice(list(range(1, 1000)))


def generate_random_string(char, length):
    random.seed(10)
    temp = []
    for i in range(0, length):
        letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
        hmm = "".join(random.choice(letters) for _ in range(char))
        temp.append(hmm)
    return temp


def login_user(username, password):
    c.execute(
        "SELECT * FROM user WHERE usernameS =? AND password = ?",
        (username, password),
    )
    data = c.fetchall()
    return data


def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()


def login_page():
    image = Image.open("assets/unit.png")
    if "user" not in st.session_state:
        st.session_state["user"] = " "
    with st.form(key="Login", clear_on_submit=True):
        # st.subheader("👋Login-TRMS👋")
        st.image(image)
        user = st.text_input("Masukkan Username")
        password = st.text_input("Password", type="password")
        # login = st.button("login", key=unique_key(4))
        login = st.form_submit_button("Login")

    if login:
        pass_hashed = make_hashes(password)
        cek = login_user(user, pass_hashed)
        length_passs = len(cek)
        if len(user) == 0 or len(password) == 0:
            st.warning("🚨Isi Username dan Password 🚨")
        elif length_passs == 0:
            st.warning("Akun Tidak Ditemukan🤖")
        elif cek:
            st.success("Login Suksess")
            st.session_state["user"] = {
                "nama": cek[0][1],
                "kpp": cek[0][3],
                "kantor": cek[0][4],
            }
    else:
        st.session_state["user"] = {
            "nama": "",
            "kpp": "",
            "kantor": "",
        }
    return [
        st.session_state["user"]["nama"],
        st.session_state["user"]["kpp"],
        st.session_state["user"]["kantor"],
    ]


# nama, kpp, kantor = login_page()
# c.execute("select * from user limit 3")
# users = c.fetchall()

# print(users)
# usernames = [user[0] for user in users]
# length = len(usernames)
# email = generate_random_string(char=10, length=length)
# names = [user[1] for user in users]
# hashed_passwords = [user[2] for user in users]


# print(email)
# print(usernames)
# for username, mail, name, passw in zip(usernames, email, names, hashed_passwords):
#     data = [username, mail, name, passw]

# print(data)


# zip_dict = dict(zip(usernames, zip(email, names, hashed_passwords)))


# print(zip_dict)

# for user in zip_dict:
#     temp = {"usernames": {zip_dict[user]["email"][0]: zip_dict[user][0]}}
# print(temp)


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
