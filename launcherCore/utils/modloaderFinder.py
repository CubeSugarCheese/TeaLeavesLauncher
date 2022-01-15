class ModloaderFinder:
    modloader_json_path: list

    def __init__(self, modloader_json_path: list):
        self.modloader_json_path = modloader_json_path

    def isForge(self):
        for i in self.modloader_json_path:
            with open(i, "r", encoding="utf8") as f:
                modloader_json = f.read()
            if modloader_json.find("net.minecraftforge.fml.common.launcher.FMLTweaker") != -1:
                return True
            else:
                return False

    def isLiteloader(self):
        for i in self.modloader_json_path:
            with open(i, "r", encoding="utf8") as f:
                modloader_json = f.read()
            if modloader_json.find("com.mumfrey.liteloader.launch.LiteLoaderTweaker") != -1:
                return True
            else:
                return False

    def isFabric(self):
        for i in self.modloader_json_path:
            with open(i, "r", encoding="utf8") as f:
                modloader_json = f.read()
            if modloader_json.find("net.fabricmc.loader.launch.knot.KnotClient") != -1:
                return True
            else:
                return False
