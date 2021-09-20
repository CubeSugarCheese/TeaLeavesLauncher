import asyncio
import aiofiles
from aiohttp import ClientSession

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

    def __init__(self, mc_path, version, mc_version, src="mojang"):
        self.mc_path = mc_path
        self.version = version
        self.mc_version = mc_version
        self.src = src

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

    async def download_version_json(self):
        async with ClientSession() as session:
            url = await self.get_version_json_url()
            async with session.get(url) as r:
                file_path = f"{self.mc_path}/versions/{self.version}/{self.mc_version}.json"
                async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                    content = await r.text()
                    await f.write(content)

    async def download_natives(self):
        pass


if __name__ == '__main__':
    t = Downloader(mc_path=r"C:\Users\Daniel\Documents\MC\HMCL\.minecraft", version="1.12.2", mc_version="1.12.2")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(t.download_version_json())