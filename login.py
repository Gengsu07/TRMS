import pickle
from pathlib import Path
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

with open('.streamlit/login.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)


def create_hash():
    passwords = []
    for username, user_data in config['credentials']['usernames'].items():
        password = user_data['password']
        passwords.append(password)
        print(user_data)

    hashed_password = stauth.Hasher(passwords).generate()
    file_path = Path(__file__).parent/'hashed_pw.pkl'
    with file_path.open('wb') as file:
        pickle.dump(hashed_password, file)


def load_pass():
    file_path = Path(__file__).parent/'hashed_pw.pkl'
    with file_path.open('rb') as file:
        hashed_password = pickle.load(file)
    return hashed_password


def names():
    names = []
    for username, user_data in config['credentials']['usernames'].items():
        name = user_data['name']
        names.append(name)
    return names


def usernames():
    usernames = []
    for username, user_data in config['credentials']['usernames'].items():
        username = username
        usernames.append(username)
    return usernames


if __name__ == '__main__':
    create_hash()
    passw = load_pass()
    print(passw)
