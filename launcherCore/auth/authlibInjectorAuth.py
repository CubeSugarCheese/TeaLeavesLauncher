# 第三方模块
import httpx
from loguru import logger
# 本地模块
from .baseAuth import BaseAccount
from .exceptions import RefreshTokenError


class AuthlibInjectorAccount(BaseAccount):
    api_address: str
    # username: str  # 此处为邮箱或以外的账户标识
    password: str

    def __init__(self,
                 api_address,
                 username=None,
                 password=None,
                 mc_access_token=None,
                 uuid=None,
                 client_token: str = None):
        self.client_token = client_token
        self.username = username
        self.password = password
        self.api_address = api_address
        self.api_address = self._get_reality_api_address()
        if mc_access_token is not None:
            self.mc_access_token = mc_access_token
            self.mc_access_token = self._get_mc_access_token()
            self.username = username
            self.uuid = uuid
        else:
            self.auth_data = self._get_authenticate().json()
            self.mc_access_token = self._get_mc_access_token()
            self.available_profiles = self.auth_data["availableProfiles"]
            self.profile = self._select_profile()
            self.username = self.profile["name"]  # 此处将 username 从登录凭据转换为角色名用以生成启动参数
            self.uuid = self.profile["id"]

    def _get_reality_api_address(self):
        response = httpx.get(self.api_address)
        headers = response.headers
        if "x-authlib-injector-api-location" in headers:
            api_address = headers["x-authlib-injector-api-location"]
        else:
            api_address = self.api_address
        return api_address

    def _get_authenticate(self):
        address = f"{self.api_address}/authserver/authenticate"
        headers = {"Content-Type": "application/json"}
        if self.client_token is not None:
            data = dict(username=self.username,
                        password=self.password,
                        clientToken=self.client_token,
                        agent={"name": "Minecraft", "version": 1})
        else:
            data = dict(username=self.username,
                        password=self.password,
                        agent={"name": "Minecraft", "version": 1})
        response = httpx.post(address, data=data, headers=headers)
        return response

    def _refresh_access_token(self):
        address = f"{self.api_address}/authserver/refresh"
        headers = {"Content-Type": "application/json"}
        if self.client_token is not None:
            data = dict(accessToken=self.mc_access_token,
                        clientToken=self.client_token)
        else:
            data = dict(accessToken=self.mc_access_token)
        response = httpx.post(address, data=data, headers=headers)
        return response

    def _check_access_token_is_available(self):
        address = f"{self.api_address}/authserver/validate"
        headers = {"Content-Type": "application/json"}
        if self.client_token is not None:
            data = dict(accessToken=self.mc_access_token,
                        clientToken=self.client_token)
        else:
            data = dict(accessToken=self.mc_access_token)
        response = httpx.post(address, data=data, headers=headers)
        if response.status_code == 204:
            result = True
        else:
            result = False
        return result

    def _select_profile(self):
        if len(self.available_profiles) == 1:
            selected_profile = self.available_profiles[0]
        else:
            print("检测到有多个可用的角色，请选择一个登录：")
            for i in self.available_profiles:
                print(f"【{self.available_profiles.index(i)}】{i['name']}")
            selected_profile = self.available_profiles[(input("选择："))]
        return selected_profile

    def _get_mc_access_token(self):
        if self.username is not None and self.password is not None:
            token = self.auth_data["accessToken"]
        elif self.mc_access_token is not None:
            if self._check_access_token_is_available():
                token = self.mc_access_token
            else:
                response = self._refresh_access_token()
                if response.status_code == 200:
                    token = response.json()["accessToken"]
                else:
                    logger.warning("登录凭据已失效，需要重新登录")
                    raise RefreshTokenError
        return token
