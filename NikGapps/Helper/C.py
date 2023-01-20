import math
import os.path
import time
from datetime import datetime
from pathlib import Path

import pytz
from colorama import Fore

import Config
from NikGapps.Telegram.TelegramApi import TelegramApi


class C:
    tz_london = pytz.timezone('Europe/London')
    datetime_london = datetime.now(tz_london)
    current_time = datetime_london.strftime("%Y%m%d")
    local_datetime = datetime.now()
    # current_local_time = local_datetime.strftime("%Y-%m-%d %H:%M:%S")
    cwd = os.getcwd()
    pwd = str(Path(cwd).parent)
    meta_inf_dir = "META-INF/com/google/android/"
    dir_sep = os.path.sep
    is_system_app = 1
    is_priv_app = 2
    # The directory where all the packages will be pulled from device and exported
    export_directory = str(Path(cwd).parent) + os.path.sep + "Export" + os.path.sep + str(
        Config.TARGET_ANDROID_VERSION) + os.path.sep + current_time
    android_version_code = Config.ANDROID_VERSIONS[str(Config.TARGET_ANDROID_VERSION)]['code']
    overlay_android_version = f"overlays_{android_version_code}"
    overlay_directory = str(Path(cwd).parent) + os.path.sep + overlay_android_version
    # The directory where all the stable package specific files will reside
    android_version_folder = str(Config.TARGET_ANDROID_VERSION)
    source_directory = str(Path(cwd).parent) + os.path.sep + str(android_version_folder)
    website_repo = "git@github.com:nikgapps/nikgapps.github.io.git"
    website_directory = str(Path(cwd).parent) + os.path.sep + "nikgapps.github.io"
    release_history_directory = str(Path(cwd).parent) + os.path.sep + "release"
    if Config.RELEASE_TYPE.__eq__("canary"):
        release_history_directory = str(Path(cwd).parent) + os.path.sep + "canary-release"
    apk_source_repo = f"https://gitlab.com/nikgapps/"
    apk_source_directory = str(Path(cwd).parent) + os.path.sep
    config_directory = str(Path(cwd).parent) + os.path.sep + "config"
    sourceforge_release_directory = "/home/frs/project/nikgapps/Releases"

    # source_directory = export_directory
    # The directory where all the final nikgapps packages will be exported
    # release_directory = str(Path(cwd).parent) + os.path.sep + "Releases" + os.path.sep + str(
    #     Config.TARGET_ANDROID_VERSION) + os.path.sep + current_time
    release_directory = str(Path(cwd).parent) + os.path.sep + "Releases" + os.path.sep + str(
        Config.TARGET_ANDROID_VERSION)
    temp_packages_directory = str(Path(cwd).parent) + os.path.sep + "TempPackages" + os.path.sep + str(
        android_version_folder)
    # temp_packages_directory = str(Path(cwd).parent) + os.path.sep + "TempPackages" + os.path.sep + str(
    #     TARGET_ANDROID_VERSION) + os.path.sep + current_time + os.path.sep + "Packages"
    path = os.path
    nikgapps_config = "nikgapps.config"
    temp_nikgapps_config_location = temp_packages_directory + os.path.sep + nikgapps_config
    DELETE_FILES_NAME = "DeleteFilesData"

    if Config.TARGET_ANDROID_VERSION >= 10:
        system_root_dir = "/system/product"
    else:
        system_root_dir = "/system"

    FILE_DOES_NOT_EXIST = 1001
    progress_complete = "▰"
    # progress_complete = "/"
    progress_remaining = "▱"
    # progress_remaining = "\\"
    telegram = TelegramApi()

    @staticmethod
    def get_file_bytes(file_name):
        file_stats = os.stat(file_name)
        # 1000 instead of 1024 because it's better to require more size than what gapps exactly takes
        return math.ceil(file_stats.st_size / 1000)

    @staticmethod
    def get_download_link(file_name, sf_path):
        sf_prefix = "https://sourceforge.net/projects/nikgapps/files/"
        download_link = sf_prefix + sf_path[len("/home/frs/project/nikgapps/"):] + "/" + C.get_base_name(
            file_name) + "/download"
        return download_link

    @staticmethod
    def start_of_function():
        return time.time()

    @staticmethod
    def end_of_function(start_time, message=None):
        print(Fore.YELLOW)
        print("---------------------------------------")
        if message is not None:
            print("--- " + message + " ---")
        sec = round(time.time() - start_time, 0)
        seconds = int(math.fmod(sec, 60))
        minutes = int(sec // 60)
        time_diff = (time.time() - start_time)
        print(Fore.YELLOW + f"--- {time_diff} seconds --- " + Fore.RESET)
        print(Fore.YELLOW + f"--- %s minutes %s seconds --- " % (minutes, seconds) + Fore.RESET)
        print("---------------------------------------")
        print(Fore.RESET)
        return time_diff

    @staticmethod
    def update_sourceforge_release_directory(release_type):
        if release_type == "config":
            C.sourceforge_release_directory = "/home/frs/project/nikgapps/Config-Releases"
        elif release_type == "canary":
            C.sourceforge_release_directory = "/home/frs/project/nikgapps/Canary-Releases"
        else:
            C.sourceforge_release_directory = "/home/frs/project/nikgapps/Releases"

    @staticmethod
    def update_android_version_dependencies():
        C.android_version_folder = str(Config.TARGET_ANDROID_VERSION)
        C.export_directory = str(Path(C.cwd).parent) + os.path.sep + "Export" + os.path.sep + str(
            Config.TARGET_ANDROID_VERSION) + os.path.sep + C.current_time
        C.source_directory = str(Path(C.cwd).parent) + os.path.sep + str(
            C.android_version_folder)
        print("Source: " + C.source_directory)
        C.release_directory = str(Path(C.cwd).parent) + os.path.sep + "Releases" + os.path.sep + str(
            Config.TARGET_ANDROID_VERSION)
        C.temp_packages_directory = str(
            Path(C.cwd).parent) + os.path.sep + "TempPackages" + os.path.sep + str(
            C.android_version_folder)
        android_version_code = Config.ANDROID_VERSIONS[str(Config.TARGET_ANDROID_VERSION)]['code']
        overlay_android_version = f"overlays_{android_version_code}"
        C.overlay_directory = str(Path(C.cwd).parent) + os.path.sep + overlay_android_version

    @staticmethod
    def get_mtime(pkg_zip_path):
        return datetime.fromtimestamp(os.path.getmtime(pkg_zip_path))

    @staticmethod
    def get_progress(package_progress):
        progress_count = 0
        print_progress = "["
        progress_length = 10
        while True:
            if progress_count == progress_length:
                break
            else:
                progress_count += 1
                progress = int((package_progress * progress_length) / 100)
                if progress >= progress_count:
                    print_progress += C.progress_complete
                else:
                    print_progress += C.progress_remaining
        print_progress += "]"
        return print_progress

    @staticmethod
    def get_base_name(directory):
        return os.path.basename(directory)

    @staticmethod
    def get_parent_path(file_path):
        return Path(file_path).parent

    @staticmethod
    def get_import_path(app_set, pkg, install_path, export_directory=None):
        base_name = C.get_base_name(install_path)
        dir_name = C.get_parent_path(install_path)
        dir_name = str(dir_name).replace("\\system_ext", "").replace("/system_ext", "") \
            .replace("\\system", "").replace("/system", "") \
            .replace("\\product", "").replace("/product", "")
        if export_directory is not None:
            output = export_directory + C.dir_sep
        else:
            output = C.export_directory + C.dir_sep
        if app_set is not None:
            output += app_set + C.dir_sep
        output += str(pkg) + C.dir_sep + str(dir_name).replace("\\", "___").replace(
            C.dir_sep, "___") + C.dir_sep + base_name
        if not os.path.exists(Path(output).parent):
            os.makedirs(Path(output).parent)
        return Path(output)

    @staticmethod
    def print_yellow(message):
        print(Fore.YELLOW + str(message) + Fore.RESET)

    @staticmethod
    def print_red(message):
        print(Fore.RED + str(message) + Fore.RESET)

    @staticmethod
    def print_green(message):
        print(Fore.GREEN + str(message) + Fore.RESET)

    @staticmethod
    def print_blue(message):
        print(Fore.BLUE + message + Fore.RESET)

    @staticmethod
    def print_magenta(message):
        print(Fore.MAGENTA + str(message) + Fore.RESET)
