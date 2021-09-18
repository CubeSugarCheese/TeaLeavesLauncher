import aiohttp
import asyncio


class AuthlibInjectorAccount:
    api_address: str
    username: str  # 此处为邮箱或以外的账户标识
    password: str
    uuid: str

    def __init__(self,
                 api_address,
                 username,
                 password,
                 client_token: str = None):
        self.client_token = client_token
        self.username = username
        self.password = password
        self.api_address = api_address
        self.api_address = asyncio.get_event_loop().run_until_complete(self._get_reality_api_address())
        self.auth_data = asyncio.get_event_loop().run_until_complete(self._get_authenticate())

    async def _get_reality_api_address(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_address) as response:
                headers = response.headers
                if "x-authlib-injector-api-location" in headers:
                    api_address = headers["x-authlib-injector-api-location"]
                else:
                    api_address = self.api_address
                return api_address

    async def _get_authenticate(self):
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
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(address, data=data) as response:
                t = await response.json()
                return t
