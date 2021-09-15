import json

import requests


class MicrosoftAccount:
    auth_code: str
    access_token: str
    refresh_token: str
    xbox_token: str
    user_hash: str
    mc_access_token: str
    uuid: str
    username: str
    is_game_exist: bool

    def __init__(self):
        print("请前往以下网址进行验证，并把重定向之后的网址粘贴回来")
        print(
            "https://login.live.com/oauth20_authorize.srf?client_id=00000000402b5328&response_type=code&scope=service%3A%3Auser.auth.xboxlive.com%3A%3AMBI_SSL&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf")
        while True:
            redirect_url = input("重定向后的URL：")
            if redirect_url != "":
                break
        from urllib import parse
        self.auth_code = parse.parse_qs(parse.urlparse(redirect_url).query)["code"][0]
        self.auth_data = self._get_authenticate().json()
        self.access_token = self.auth_data["access_token"]
        self.refresh_token = self.auth_data["refresh_token"]
        self.xbox_data = self._auth_xbox_live().json()
        self.xbox_token = self.xbox_data["Token"]
        self.user_hash = self.xbox_data["DisplayClaims"]["xui"][0]["uhs"]
        self.xsts_data = self._get_xsts_authenticate().json()
        self.xsts_token = self.xsts_data["Token"]
        self.mc_auth_data = self._get_mc_authenticate().json()
        self.mc_access_token = self.mc_auth_data["access_token"]  # 登录游戏必需参数
        self.is_game_exist = self._check_game_exist()
        self.mc_profile = self._get_mc_profile().json()
        self.uuid = self.mc_profile["id"]  # 登录游戏必需参数
        self.username = self.mc_profile["name"]  # 登录游戏必需参数

    def _get_authenticate(self):
        api_address = "https://login.live.com/oauth20_token.srf"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}  # 固定请求头
        auth_data = dict(client_id="00000000402b5328",
                         code=self.auth_code,
                         grant_type="authorization_code",
                         redirect_uri="https://login.live.com/oauth20_desktop.srf",
                         scope="service::user.auth.xboxlive.com::MBI_SSL"
                         )
        return requests.post(url=api_address, data=auth_data, headers=headers)

    def _refresh_authenticate(self):
        api_address = "https://login.live.com/oauth20_token.srf"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}  # 固定请求头
        auth_data = dict(client_id="00000000402b5328",
                         refresh_token=self.refresh_token,
                         scope="service::user.auth.xboxlive.com::MBI_SSL",
                         grant_type="refresh_token",
                         redirect_uri="https://login.live.com/oauth20_desktop.srf",
                         )
        return requests.post(url=api_address, data=auth_data, headers=headers)

    def _auth_xbox_live(self):
        api_address = "https://user.auth.xboxlive.com/user/authenticate"
        headers = {"Content-Type": "application/json",
                   "Accept": "application/json"}
        xbox_data = dict(Properties=dict(
            AuthMethod="RPS", SiteName="user.auth.xboxlive.com",
            RpsTicket=self.access_token),
            RelyingParty="http://auth.xboxlive.com",
            TokenType="JWT"
        )
        xbox_data = requests.post(url=api_address, data=json.dumps(xbox_data), headers=headers)
        return xbox_data

    def _get_xsts_authenticate(self):
        api_address = "https://xsts.auth.xboxlive.com/xsts/authorize"
        headers = {"Content-Type": "application/json",
                   "Accept": "application/json"}
        xbox_data = dict(
            Properties=dict(SandboxId="RETAIL", UserTokens=[self.xbox_token]),
            RelyingParty="rp://api.minecraftservices.com/",
            TokenType="JWT"
        )
        xsts_data = requests.post(url=api_address, data=json.dumps(xbox_data), headers=headers)
        return xsts_data

    def _get_mc_authenticate(self):
        api_address = "https://api.minecraftservices.com/authentication/login_with_xbox"
        headers = {"Content-Type": "application/json"}
        mc_data = {"identityToken": f"XBL3.0 x={self.user_hash};{self.xsts_token}"}
        mc_auth_data = requests.post(url=api_address, data=json.dumps(mc_data), headers=headers)
        return mc_auth_data

    def _check_game_exist(self):
        api_address = "https://api.minecraftservices.com/entitlements/mcstore"
        headers = {"Authorization": f"Bearer {self.mc_access_token}"}
        game_exist_data = requests.get(url=api_address, headers=headers)
        if "items" not in game_exist_data.json():
            result = False
        else:
            result = True
        return result

    def _get_mc_profile(self):
        api_address = "https://api.minecraftservices.com/minecraft/profile"
        headers = {"Authorization": f"Bearer {self.mc_access_token}"}
        game_profile = requests.get(url=api_address, headers=headers)
        return game_profile
