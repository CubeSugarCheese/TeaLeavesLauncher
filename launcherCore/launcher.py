import json
import os
import platform
from utils.javaFinder import find_java_from_where


class Launcher:
    version_json_path: str
    natives_folder_path: str
    max_memory: int
    java_path: str
    mc_path: str
    version: str
    uuid: str
    name: str
    mc_access_token: str
    launcher_version: str = "dev"
    user_type: str
    width: int
    height: int

    def __init__(self,
                 mc_path: str,
                 version: str,
                 uuid: str,
                 name: str,
                 mc_access_token=None,
                 java_path: str = find_java_from_where(),
                 max_memory=2048,
                 width=840,
                 height=480
                 ):
        self.mc_path = mc_path
        self.version = version
        self.uuid = uuid
        self.name = name
        self.java_path = java_path
        self.width = width
        self.height = height
        self.max_memory = max_memory
        if mc_access_token:
            self.user_type = "Mojang"
            self.mc_access_token = mc_access_token
        else:
            self.user_type = "Legacy"
        self.version_json_path = f"{self.mc_path}\\versions\\{self.version}\\{self.version}.json"
        self.natives_folder_path = f"{self.mc_path}\\versions\\{self.version}\\natives"
        self.asset_index = self._load_version_json()["assetIndex"]["id"]

    def _load_version_json(self):
        with open(self.version_json_path, "r", encoding="utf-8") as f:
            return json.loads(f.read())

    def _generate_libraries_parameter(self):
        jar_paths = "\""
        for i in self._load_version_json()["libraries"]:
            if "classifiers" not in i["downloads"]:
                libraries_parts = i["name"].split(":")
                # "com.mojang:patchy:1.1" => ["com.mojang","patchy","1.1"]
                libraries_parts_0 = libraries_parts[0].replace('.', '\\')
                library_path = f"{self.mc_path}\\libraries\\{libraries_parts_0}\\{libraries_parts[1]}\\{libraries_parts[2]}\\{libraries_parts[1]}-{libraries_parts[2]}.jar"
                if platform.system() == "Windows":
                    jar_paths += f"{library_path};"
                else:
                    jar_paths += f"{library_path}:"
        jar_paths += "\""
        return jar_paths

    def _generate_launch_parameter(self):
        part_X = f"java -Xmx{self.max_memory}M -XX:+UseG1GC -XX:-UseAdaptiveSizePolicy -XX:-OmitStackTraceInFastThrow "
        part_D = f"-Dminecraft.client.jar=\".minecraft\\versions\\{self.version}\\{self.version}.jar \" -Dminecraft.launcher.brand=tea-leaves-launcher -Dminecraft.launcher.version={self.launcher_version} -Djava.library.path={self.natives_folder_path} "
        part_cp = f"-cp {self._generate_libraries_parameter()} "
        part_jar = f"\"{self.mc_path}\\versions\\{self.version}\\{self.version}.jar\" net.minecraft.client.main.Main "
        if self.user_type == "Legacy":
            part_game = f"--username {self.name} --version {self.version} --gameDir \"{self.mc_path}\\versions\\{self.version}\" " + \
                        f"--assetsDir \"{self.mc_path}\\assets\" --assetIndex {self.asset_index} " + \
                        f"--uuid {self.uuid} --userType {self.user_type} --versionType TeaLeavesLauncher" + \
                        f"--width {self.width} --height {self.height}"
        else:
            part_game = f"--username {self.name} --version {self.version} --gameDir \"{self.mc_path}\\versions\\{self.version}\" " + \
                        f"--assetsDir \"{self.mc_path}\\assets\" --assetIndex {self.asset_index} " + \
                        f"--uuid {self.uuid} --accessToken {self.mc_access_token} --versionType TeaLeavesLauncher " + \
                        f"--width {self.width} --height {self.height}"
        return part_X + part_D + part_cp + part_jar + part_game

    def launch_game(self):
        cmd = self._generate_launch_parameter()
        import subprocess
        subprocess.run(cmd)


if __name__ == "__main__":
    testLauncher = Launcher(
        mc_path=r"C:\Users\2026\Downloads\Programs\bakaxl\.minecraft",
        name="Cubesugarcheese",
        uuid="55eff3377c554216844686450b4b3fef",
        mc_access_token="",
        version="1.16.5"
    )
    print(testLauncher._generate_launch_parameter())
    testLauncher.launch_game()
