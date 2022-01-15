import asyncio
import json
import platform
import subprocess
from pathlib import Path
from typing import Optional

from loguru import logger

from .download.download import Downloader
from .utils.javaFinder import find_java_from_where
from .utils.modloaderFinder import ModloaderFinder
from .utils.static import launcher_version


class Launcher:
    vanilla_json_path: Path
    natives_folder_path: Path
    max_memory: int
    java_path: str
    mc_path: Path
    version: str
    uuid: str
    name: str
    mc_access_token: str
    launcher_version: str
    user_type: str
    width: int = 854
    height: int = 480
    modloader_json_paths: list
    mc_version: str
    forge: bool
    liteloader: bool
    fabric: bool

    def __init__(self,
                 mc_path: Optional[Path, str],
                 version: str,
                 uuid: str,
                 name: str,
                 mc_access_token,
                 java_path: str = find_java_from_where(),
                 max_memory=2048
                 ):
        if type(mc_path) == str:
            self.mc_path = Path(mc_path)
        else:
            self.mc_path = mc_path
        self.version = version
        self.uuid = uuid
        self.name = name
        self.mc_access_token = mc_access_token
        self.java_path = java_path
        self.max_memory = max_memory
        self.modloader_json_paths = self._get_modloader_json_paths()
        self.mc_version = self._get_mc_version()
        self.vanilla_json_path = self._get_vanilla_json_path()
        self.natives_folder_path = self.mc_path / "versions" / self.version / "natives"
        self.asset_index = self._load_vanilla_json()["assetIndex"]["id"]
        self.launcher_version = launcher_version
        ML_finder = ModloaderFinder(self.modloader_json_paths)
        self.liteloader = ML_finder.isLiteloader()
        self.forge = ML_finder.isForge()
        self.fabric = ML_finder.isFabric()

    def _load_vanilla_json(self):
        self._check_and_complete_game()
        with open(self.vanilla_json_path, "r", encoding="utf-8") as f:
            return json.loads(f.read())

    def _get_mc_version(self):
        if self.modloader_json_paths:
            with open(self.modloader_json_paths[0], "r", encoding="utf-8") as f:
                mc_version = json.load(f)["inheritsFrom"]
        else:
            with open(self._get_vanilla_json_path(), "r", encoding="utf-8") as f:
                vanilla_json = json.loads(f.read())
                mc_version = vanilla_json["id"]
        return mc_version

    def _get_vanilla_json_path(self):
        version_dir = self.mc_path / "versions" / self.version  # 文件夹名称
        for i in version_dir.glob("*.json"):  # 遍历所有扩展名为“.json”的文件
            with i.open("r", encoding="utf-8") as f:
                if f.read().find("net.minecraft.client.main.Main") != -1:
                    return i
        return version_dir / self.version / f"{self.mc_version}.json"

    def _get_modloader_json_paths(self):
        version_dir = self.mc_path / "versions" / self.version  # 文件夹名称
        json_list = version_dir.glob("*.json")
        modloader_json_path = []
        for j in json_list:
            with open(j, "r", encoding="utf-8") as f:
                if "inheritsFrom" in json.load(f):
                    modloader_json_path.append(j)
        return modloader_json_path

    def _generate_vanilla_libraries_parameter(self):
        jar_paths = ""
        for i in self._load_vanilla_json()["libraries"]:
            if "classifiers" not in i["downloads"]:
                libraries_parts = i["name"].split(":")
                # "com.mojang:patchy:1.1" => ["com.mojang","patchy","1.1"]
                libraries_parts_0 = libraries_parts[0].replace('.', '\\')
                library_path = self.mc_path/"libraries"/libraries_parts_0/libraries_parts[1]/libraries_parts[2]/f"{libraries_parts[1]}-{libraries_parts[2]}.jar"
                if platform.system() == "Windows":
                    jar_paths += f"{library_path};"
                else:
                    jar_paths += f"{library_path}:"
        return jar_paths

    def _generate_modloader_libraries_parameter(self):
        jar_paths = ""
        for i in self.modloader_json_paths:
            with i.open("r", encoding="utf-8") as f:
                for j in json.loads(f.read())["libraries"]:
                    libraries_parts = j["name"].split(":")
                    libraries_parts_0 = libraries_parts[0].replace('.', '\\')
                    library_path = self.mc_path/"libraries"/libraries_parts_0/libraries_parts[1]/libraries_parts[2]/"{libraries_parts[1]}-{libraries_parts[2]}.jar"
                    if platform.system() == "Windows":
                        jar_paths += f"{library_path};"
                    else:
                        jar_paths += f"{library_path}:"
        return jar_paths

    def _generate_cp_parameter(self):
        cp_parameter = f"-cp \"{self._generate_vanilla_libraries_parameter()}{self._generate_modloader_libraries_parameter()}{self.mc_path}\\versions\\{self.version}\\{self.version}.jar\" "
        return cp_parameter

    def _generate_game_parameter(self):
        if self.liteloader or self.forge:
            main_class = "net.minecraft.launchwrapper.Launch "
        elif self.fabric:
            main_class = "net.fabricmc.loader.launch.knot.KnotClient "
        else:
            main_class = "net.minecraft.client.main.Main "
        if self.liteloader and self.forge:
            tweak_class = "--tweakClass com.mumfrey.liteloader.launch.LiteLoaderTweaker --tweakClass net.minecraftforge.fml.common.launcher.FMLTweaker "
        elif self.forge:
            tweak_class = "--tweakClass net.minecraftforge.fml.common.launcher.FMLTweaker "
        elif self.liteloader:
            tweak_class = "--tweakClass com.mumfrey.liteloader.launch.LiteLoaderTweaker "
        else:
            tweak_class = ""
        game_parameter = \
            f"{main_class}" + \
            f"--username {self.name} --version {self.version} --gameDir \"{self.mc_path}\\versions\\{self.version}\" " + \
            f"{tweak_class}" + \
            f"--assetsDir \"{self.mc_path}\\assets\" --assetIndex {self.asset_index} " + \
            f"--userType mojang --uuid {self.uuid} --accessToken {self.mc_access_token} --versionType TeaLeavesLauncher " + \
            f"--width {self.width} --height {self.height}"
        return game_parameter

    def _generate_launch_parameter(self):
        part_X = f"\"{self.java_path}\" -Xmx{self.max_memory}M -XX:+UseG1GC -XX:-UseAdaptiveSizePolicy -XX:-OmitStackTraceInFastThrow "
        part_D = f"-Dminecraft.launcher.brand=tea-leaves-launcher -Dminecraft.launcher.version={self.launcher_version} -Djava.library.path=\"{self.natives_folder_path}\" "
        part_cp = self._generate_cp_parameter()
        part_game = self._generate_game_parameter()
        return part_X + part_D + part_cp + part_game

    def _check_and_complete_game(self):
        downloader = Downloader(self.mc_path, self.version, self.mc_version, "mcbbs")
        loop = asyncio.get_event_loop()
        if not self._get_vanilla_json_path().exists():
            logger.warning("缺失版本json，开始自动补全")
            loop.run_until_complete(downloader.download_version_json())
            logger.warning("版本json补全完成")
        if not self.natives_folder_path.exists():
            logger.warning("缺失natives，开始自动补全")
            loop.run_until_complete(downloader.download_natives())
            loop.run_until_complete(downloader.unzip_natives())
            logger.warning("natives补全完成")

    def launch_game(self):
        self._check_and_complete_game()
        cmd = self._generate_launch_parameter()
        logger.info("MC已启动")
        logger.debug(cmd)
        subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
