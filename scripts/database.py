import os

from deta import Deta  # pip install deta

from dotenv import load_dotenv  # pip install python-dotenv


# Load the environment variables
load_dotenv()
DETA_KEY = os.getenv("DETA_KEY")

# Initialize with a project key
deta = Deta(DETA_KEY)

# This is how to create/connect a database
db = deta.Base("trms-user")


def insert_user(username, name, password):
    """Returns the user on a successful user creation, otherwise raises and error"""
    return db.put({"key": username, "name": name, "password": password})


def fetch_all_users():
    """Returns a dict of all users"""
    res = db.fetch()
    return res.items


def get_user(username):
    """If not found, the function will return None"""
    return db.get(username)


def update_user(username, updates):
    """If the item is updated, returns None. Otherwise, an exception is raised"""
    return db.update(updates, username)


def delete_user(username):
    """Always returns None, even if the key does not exist"""
    return db.delete(username)


if __name__ == "__main__":
    users = fetch_all_users()
    temp_dict = {}
    list_dict = []
    for user in users:
        mask_dict = {
            "usernames": {
                user["key"]: {
                    "email": None,
                    "name": user["name"],
                    "password": user["password"],
                }
            }
        }

        list_dict.append(mask_dict)
    combined_dict = {}
    for d in list_dict:
        for key, value in d.items():
            combined_dict.setdefault(key, {}).update(value)

    print(combined_dict)
    # print(list_dict)
