from pathlib import Path

from loguru import logger
from ruamel.yaml import YAML

from ..utils.static import default_config
from ..utils.singleton import Singleton
from .exceptions import KeyNotFoundError

yaml = YAML()


class Config(Singleton):
    config_path: Path

    def __init__(self):
        self.path = Path()
        self.config_path = Path().cwd().joinpath("config.yml")
        if not Path.exists(self.config_path):
            logger.warning("未发现配置文件，已自动创建")
            self._output_default_config_yml()

    def _output_default_config_yml(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            f.write(default_config)

    # 编写 __getitem__ 方法实现用 config[key] 形式加载配置的语法
    def __getitem__(self, key: str):
        return self.load(key)

    # 编写 __setitem__ 方法实现用 config[key] = value 形式修改配置的语法
    def __setitem__(self, key: str, value):
        self.set(key, value)

    def set(self, key: str, value):
        with open(self.config_path, "r", encoding="utf-8") as f:
            conf = yaml.load(f)
            if key not in conf:
                raise KeyNotFoundError(key)
            else:
                conf[key] = value
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(conf, f)
            logger.info(f"已将配置文件 {key} 值设定为 {value}")

    def load(self, key: str):
        with open(self.config_path, "r", encoding="utf-8") as f:
            conf = yaml.load(f)
            if key not in conf:
                raise KeyNotFoundError(key)
            else:
                value = conf[key]
                logger.debug(f"已从配置文件读取 {key} 值 {value}")
            return value
