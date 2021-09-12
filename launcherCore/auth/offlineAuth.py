import requests


class OfflineAccount:
    username: str
    uuid: str

    def __init__(self, username):
        self.username = username
        self.uuid = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{self.username}").json()["id"]
