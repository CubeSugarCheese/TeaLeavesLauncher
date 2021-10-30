import asyncio
import json
import logging
import platform
import zipfile
from pathlib import Path
from typing import Dict, Union, Literal

import aiofiles
import tqdm
from aiohttp import ClientSession, connector

from .download_souces import download_src
from .exceptions import VersionNotFound

path = Path()
loop = asyncio.get_event_loop()
MIRROR = Literal["mojang", "bmclapi", "mcbbs"]
SYSTEM = Literal["Linux", "Windows", "Darwin"]


class Downloader:
    mc_path: Path
    version: str
    mc_version: str
    source: Dict[str, str]
    version_json: dict
    download_temp_folder: Path
    natives_path: Path
    natives_system: Literal["natives-linux", "natives-windows", "natives-osx"]

    def __init__(self,
                 mc_path: Union[Path, str],
                 version: str,
                 mc_version: str,
                 source: MIRROR = "mojang"):
        if type(mc_path) == str:
            self.mc_path = Path(mc_path)
        else:
            self.mc_path = mc_path
        self.version = version
        self.mc_version = mc_version
        self.source = download_src[source]
        self.version_json = loop.run_until_complete(self._get_version_json())
        self.download_temp_folder = Path.cwd() / "downloadTemp"
        self.natives_path = self.mc_path / "versions" / self.version / "natives"
        if platform.system() == "Linux":
            self.natives_system = "natives-linux"
        elif platform.system() == "Windows":
            self.natives_system = "natives-windows"
        elif platform.system() == "Darwin":
            self.natives_system = "natives-osx"

    async def async_download_from_url(self, url, file_name, single_chunk=20 * 1024):
        """
        用于异步分块下载文件
        来自：https://github.com/cxapython/mp4download
        """
        file_path = self.download_temp_folder / file_name
        if not file_path.exists():
            try:
                self.download_temp_folder.mkdir(parents=True)
            except FileExistsError:
                pass
        first_byte = file_path.stat().st_size
        async with connector.TCPConnector(limit=300, force_close=True, enable_cleanup_closed=True) as tcp:
            async with ClientSession(connector=tcp) as session:
                async with session.get(url) as response:
                    file_size = int(response.headers['content-length'])
                    progress_bar = tqdm.tqdm(
                        total=file_size,
                        initial=first_byte,
                        unit='B',
                        unit_scale=True,
                        desc=str(file_path))
                headers = {"Range": f"bytes={first_byte}-{file_size}"}
                async with session.get(url, headers=headers) as response:
                    while first_byte < file_size:
                        # 本地已下载文件的总容量和网络文件的实际大小进行比较，如果小于则表示下载未完成，继续下载。
                        async with aiofiles.open(str(file_path), 'ab') as f:
                            chunk = await response.content.read(single_chunk)
                            if chunk:
                                await f.write(chunk)
                                progress_bar.update(len(chunk))
                            else:
                                break
                    progress_bar.close()

    async def get_version_manifest(self):
        async with ClientSession() as session:
            url = f"https://{self.source['launchermeta.mojang.com']}/mc/game/version_manifest.json"
            async with session.get(url) as r:
                return await r.json()

    async def get_version_json_url(self):
        manifest_json = await self.get_version_manifest()
        for i in manifest_json["versions"]:
            if i["id"] == self.mc_version:
                url = i["url"].replace("launchermeta.mojang.com", self.source['launchermeta.mojang.com'])
                return url
        raise VersionNotFound(self.mc_version)

    async def _get_version_json(self):
        async with ClientSession() as session:
            url = await self.get_version_json_url()
            async with session.get(url) as r:
                return await r.json()

    async def download_version_json(self):
        version_json = await self._get_version_json()
        file_path = self.mc_path / "versions" / self.version / f"{self.mc_version}.json"
        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(version_json))

    def _get_natives_list(self):
        natives_list = []
        for i in self.version_json["libraries"]:
            if "classifiers" in i["downloads"]:
                natives_list.append(i["downloads"]["classifiers"])
        return natives_list

    async def download_natives(self):
        for i in self._get_natives_list():
            if self.natives_system in i:
                url = i[self.natives_system]["url"].replace("launchermeta.minecraft.net", self.source['launchermeta.mojang.com'])
                file_name = Path(i[self.natives_system]["path"]).name
                await self.async_download_from_url(url, file_name)

    async def unzip_natives(self):
        natives_zip_path_list = []
        for i in self._get_natives_list():
            if self.natives_system in i:
                file_name = Path(i[self.natives_system]["path"]).name
                natives_zip_path_list.append(self.download_temp_folder / file_name)
        if not self.natives_path.exists():
            self.natives_path.mkdir(parents=True)
        for j in natives_zip_path_list:
            file = zipfile.ZipFile(str(j), "r")
            file.extractall(self.natives_path)
            logging.info(f"成功解压 {j}")


if __name__ == '__main__':
    t = Downloader(Path(r"C:\Users\Daniel\Documents\MC\HMCL\.minecraft"), version="1.12.2", mc_version="1.12.2",
                   source="mojang")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(t.unzip_natives())
