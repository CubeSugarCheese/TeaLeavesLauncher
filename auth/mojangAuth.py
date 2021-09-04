import json
import requests


class MojangAccount:
    accessToken: str
    username: str
    password: str

    def __init__(self, username: str, password: str, *client_token: str):
        """
        :param username: mojang帐号电子邮箱地址或玩家名
        :param password: mojang帐号密码
        """
        self.username = username
        self.password = password
        self.client_token = client_token

    def _get_authenticate(self):
        api_address = "https://authserver.mojang.com/authenticate"  # 固定请求地址
        headers = {"Content-Type": "application/json"}  # 固定请求头
        if self.client_token is not None:
            auth_data = dict(agent={"name": "Minecraft", "version": 1},
                             username=self.username,
                             password=self.password,
                             clientToken=self.client_token,
                             requestUser=False)
        else:
            auth_data = dict(agent={"name": "Minecraft", "version": 1},
                             username=self.username,
                             password=self.password,
                             requestUser=False)

        return requests.post(url=api_address, data=json.dumps(auth_data), headers=headers)

    def get_access_token(self):
        authenticate = self._get_authenticate()
        return json.loads(authenticate.text)["access_token"]


def check_access_token_is_vaild(access_token: str, *client_token: str):
    api_address = "https://authserver.mojang.com/validate"  # 固定请求地址
    headers = {"Content-Type": "application/json"}  # 固定请求头
    if client_token is not None:
        check_data = dict(accessToken=access_token, clientToken=client_token)
    else:
        check_data = dict(accessToken=access_token)
    result = True if requests.post(url=api_address, data=json.dumps(check_data),
                                   headers=headers).status_code == 200 else False
    return result

def refresh_access_token():
    api_address = "https://authserver.mojang.com/refresh"  # 固定请求地址
    headers = {"Content-Type": "application/json"}  # 固定请求头


if __name__ == '__main__':
    pass
