# 内置模块
import uuid
# 第三方模块
import requests
# 本地模块
from launcherCore.auth.baseAuth import BaseAccount


class OfflineAccount(BaseAccount):

    def __init__(self, username):
        self.username = username
        data = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{self.username}")
        if data.status_code != "200":
            self.uuid = uuid.uuid4().hex
        else:
            self.uuid = data.json()["id"]
        self.mc_access_token = "f266a689f9b1424995bc341fc0966560"  # 无效的 token
