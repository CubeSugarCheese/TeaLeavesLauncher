class ConfigError(Exception):
    pass


class KeyNotFoundError(ConfigError):
    """未在 config.yml 中找到指定 key 对应 value 引发此异常"""

    def __init__(self, key: str):
        self.key = key

    def __str__(self):
        return f"Key {self.key} not found"
