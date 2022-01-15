class DownloadError(Exception):
    pass


class VersionNotFound(DownloadError):
    """未在 version_manifest.json 中找到指定版本引发此异常"""

    def __init__(self, version):
        self.version = version

    def __str__(self):
        return f"Version {self.version} not found"
