import asyncio
import logging
import os
import platform
import tqdm

import aiofiles
from aiohttp import ClientSession, connector

mirror = {"mojang": {"launchermeta.mojang.com": "launchermeta.mojang.com",
                     "launcher.mojang.com": "launcher.mojang.com",
                     "resources.download.minecraft.net": "resources.download.minecraft.net",
                     "libraries.minecraft.net": "libraries.minecraft.net",
                     "files.minecraftforge.net/maven": "files.minecraftforge.net/maven"},

          "bmclapi": {"launchermeta.mojang.com": "bmclapi2.bangbang93.com",
                      "launcher.mojang.com": "bmclapi2.bangbang93.com",
                      "resources.download.minecraft.net": "bmclapi2.bangbang93.com/assets",
                      "libraries.minecraft.net": "bmclapi2.bangbang93.com/maven",
                      "files.minecraftforge.net/maven": "bmclapi2.bangbang93.com/maven"},

          "mcbbs": {"launchermeta.mojang.com": "download.mcbbs.net",
                    "launcher.mojang.com": "download.mcbbs.net",
                    "resources.download.minecraft.net": "download.mcbbs.net/assets",
                    "libraries.minecraft.net": "download.mcbbs.net/maven",
                    "files.minecraftforge.net/maven": "download.mcbbs.net/maven"}}


class DownloadError(Exception):
    pass


class VersionNotFound(DownloadError):
    """未在 version_manifest.json 中找到指定版本引发此异常"""

    def __init__(self, version):
        self.version = version

    def __str__(self):
        return f"Version {self.version} not found"


class Downloader:
    mc_path: str
    version: str
    mc_version: str
    src: str
    # mojang bmclapi mcbbs
    version_json: dict
    system: str
    # Linux Windows Darwin
    download_temp_folder: str
    natives_path: str

    def __init__(self, mc_path, version, mc_version, src="mojang"):
        self.mc_path = mc_path
        self.version = version
        self.mc_version = mc_version
        self.src = src
        self.version_json = asyncio.get_event_loop().run_until_complete(self._get_version_json())
        self.system = platform.system()
        self.download_temp_folder = f"{os.getcwd()}\\downloadTemp"
        self.natives_path = f"{self.mc_path}\\versions\\{self.version}\\natives"

    async def fetch(self, session, url, file_path, pbar=None, headers=None):
        """
        用于异步分块下载文件
        来自：https://github.com/cxapython/mp4download
        """
        if headers:
            async with session.get(url, headers=headers) as r:
                if not os.path.exists(file_path):
                    p, __ = os.path.split(file_path)
                    try:
                        os.makedirs(p)
                    except FileExistsError:
                        pass
                    with open(file_path, "w") as __:
                        pass
                async with aiofiles.open(file_path, 'ab') as f:
                    while True:
                        chunk = await r.content.read(1024)
                        if not chunk:
                            break
                        await f.write(chunk)
                        pbar.update(1024)
                pbar.close()
        else:
            # 没有 headers 说明是刚开始下载，直接返回用于获取文件信息
            async with session.get(url) as r:
                return r

    async def async_download_from_url(self, url, file_name):
        file_path = f"{self.download_temp_folder}\\{file_name}"
        async with connector.TCPConnector(limit=300, force_close=True, enable_cleanup_closed=True) as tcp:
            async with ClientSession(connector=tcp) as session:
                r = await self.fetch(session, url, file_path)
                file_size = int(r.headers['content-length'])
                logging.info(f"获取文件总长度:{file_size}")
                if os.path.exists(file_path):
                    first_byte = os.path.getsize(file_path)
                else:
                    first_byte = 0
                if first_byte >= file_size:
                    # 本地已下载文件的总容量和网络文件的实际大小进行比较，如果大于或者等于则表示已经下载完成，通过return退出函数，否则继续下载。
                    return file_size
                header = {"Range": f"bytes={first_byte}-{file_size}"}
                pbar = tqdm.tqdm(
                    total=file_size, initial=first_byte,
                    unit='B', unit_scale=True, desc=file_path)
                await self.fetch(session, url, file_path, pbar=pbar, headers=header)

    async def get_version_manifest(self):
        async with ClientSession() as session:
            url = f"https://{mirror[self.src]['launchermeta.mojang.com']}/mc/game/version_manifest.json"
            async with session.get(url) as r:
                return await r.json()

    async def get_version_json_url(self):
        manifest_json = await self.get_version_manifest()
        for i in manifest_json["versions"]:
            if i["id"] == self.mc_version:
                url = i["url"].replace("launchermeta.mojang.com", mirror[self.src]['launchermeta.mojang.com'])
                return url
        raise VersionNotFound(self.mc_version)

    async def _get_version_json(self):
        async with ClientSession() as session:
            url = await self.get_version_json_url()
            async with session.get(url) as r:
                return await r.json()

    async def download_version_json(self):
        json = await self._get_version_json()
        file_path = f"{self.mc_path}/versions/{self.version}/{self.mc_version}.json"
        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await json.dump(f)

    async def _get_natives_list(self):
        natives_list = []
        for i in self.version_json["libraries"]:
            if "classifiers" in i["downloads"]:
                natives_list.append(i["downloads"]["classifiers"])
        return natives_list

    async def download_natives(self):
        if self.system == "Linux":
            natives_system = "natives-linux"
        elif self.system == "Windows":
            natives_system = "natives-windows"
        elif self.system == "Darwin":
            natives_system = "natives-osx"
        for i in await self._get_natives_list():
            if natives_system in i:
                url = i[natives_system]["url"].replace("launchermeta.minecraft.net", mirror[self.src]['launchermeta.mojang.com'])
                file_name = i[natives_system]["path"].replace("/", "\\")
                await self.async_download_from_url(url, file_name)


if __name__ == '__main__':
    t = Downloader(mc_path=r"C:\Users\Daniel\Documents\MC\HMCL\.minecraft", version="1.12.2", mc_version="1.12.2", src="mojang")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(t.download_natives())


