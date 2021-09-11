import zipfile


class ZipManager:

    def __init__(self, zip_path: str):
        self.zip = zipfile.ZipFile(zip_path, "r")

    def check_file_is_in_zip(self, filename: str):
        """
        该方法只会检查最外层文件
        """
        if filename in self.zip.namelist():
            result = True
        else:
            result = False
        return result

    def read_single_file(self, filename: str):
        """
        该方法只读取最外层文件
        """
        return self.zip.read(filename)
