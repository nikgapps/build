import os.path
import shutil
from .Constants import Constants


class FileOp:
    @staticmethod
    def create_file_dir(file_path):
        parent_dir = str(Constants.get_parent_path(file_path))
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

    @staticmethod
    def copy_file(source, destination):
        FileOp.create_file_dir(destination)
        shutil.copy2(source, destination)

    @staticmethod
    def dir_exists(dir_path):
        if os.path.exists(dir_path):
            return True
        return False

    @staticmethod
    def file_exists(file_path):
        if os.path.exists(file_path):
            return True
        return False

    @staticmethod
    def remove_dir(dir_path):
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            return True
        return False

    @staticmethod
    def remove_file(file_path):
        if FileOp.file_exists(file_path):
            os.remove(file_path)
            return True
        return False

    @staticmethod
    def get_dir_list(file_path):
        return_list = []
        dir_list = ""
        file_path = str(file_path.replace("___", "/")).replace("\\", "/")
        for path in str(file_path).split("/"):
            dir_list = str(dir_list) + "/" + path
            if not str(dir_list).__eq__("/") \
                    and not str(dir_list).__contains__(".") \
                    and not str(dir_list).endswith("/system") \
                    and not str(dir_list).endswith("/product") \
                    and not str(dir_list).endswith("/etc") \
                    and not str(dir_list).endswith("/framework") \
                    and not str(dir_list).startswith("/usr/srec/en-US/") \
                    and not str(dir_list).endswith("/priv-app"):
                return_list.append(dir_list[1:])
        return return_list

    @staticmethod
    def read_priv_app_temp_file(file_path, encoding='cp437'):
        return_list = []
        if FileOp.file_exists(file_path):
            file = open(file_path, encoding=encoding)
            text = file.readlines()
            for line in text:
                if line.startswith("uses-permission:"):
                    try:
                        permissions = line.split('\'')
                        if permissions.__len__() > 1:
                            return_list.append(permissions[1])
                    except Exception as e:
                        return_list = ["Exception: " + str(e.message)]
            file.close()
            FileOp.remove_file(file_path)
        else:
            return_list.append("Exception: " + str(Constants.FILE_DOES_NOT_EXIST))
        return return_list

    @staticmethod
    def read_package_name(file_path, encoding='cp437'):
        if FileOp.file_exists(file_path):
            file = open(file_path, encoding=encoding)
            text = file.readline()
            if text.startswith("package:"):
                index1 = text.find("'")
                text = text[index1 + 1: -1]
                index1 = text.find("'")
                text = text[0: index1]
            file.close()
            FileOp.remove_file(file_path)
        else:
            text = "Exception: " + str(Constants.FILE_DOES_NOT_EXIST)
        return text

    @staticmethod
    def read_package_version(file_path, encoding='cp437'):
        if FileOp.file_exists(file_path):
            file = open(file_path, encoding=encoding)
            text = file.readline()
            if text.__contains__("versionName="):
                index1 = text.find("versionName='")
                text = text[index1 + 13: -1]
                index1 = text.find("'")
                text = text[0: index1]
            file.close()
            FileOp.remove_file(file_path)
        else:
            text = "Exception: " + str(Constants.FILE_DOES_NOT_EXIST)
        return text

    @staticmethod
    def write_string_file(str_data, file_path):
        FileOp.create_file_dir(file_path)
        if FileOp.file_exists(file_path):
            os.remove(file_path)
        file = open(file_path, "w")
        file.write(str_data)
        file.close()

    @staticmethod
    def write_string_in_lf_file(str_data, file_path):
        FileOp.create_file_dir(file_path)
        if FileOp.file_exists(file_path):
            os.remove(file_path)
        file = open(file_path, "w", newline='\n')
        file.write(str_data)
        file.close()

    @staticmethod
    def read_string_file(file_path):
        if FileOp.file_exists(file_path):
            file = open(file_path, "r", encoding='cp437')
            lines = file.readlines()
            file.close()
            return lines
        else:
            return ['File Not Found']

    @staticmethod
    def read_binary_file(file_path):
        if FileOp.file_exists(file_path):
            file = open(file_path, "rb")
            lines = file.readlines()
            file.close()
            return lines
        else:
            return ['File Not Found']
