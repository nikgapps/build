import math
import os.path
import time
from datetime import datetime
from pathlib import Path

import pytz

import Config


class Constants:
    tz_london = pytz.timezone('Europe/London')
    datetime_london = datetime.now(tz_london)
    current_time = datetime_london.strftime("%Y%m%d")
    local_datetime = datetime.now()
    # current_local_time = local_datetime.strftime("%Y-%m-%d %H:%M:%S")
    cwd = os.getcwd()
    meta_inf_dir = "META-INF/com/google/android/"
    dir_sep = os.path.sep
    is_system_app = 1
    is_priv_app = 2
    # The directory where all the packages will be pulled from device and exported
    export_directory = str(Path(cwd).parent) + os.path.sep + "Export" + os.path.sep + str(
        Config.TARGET_ANDROID_VERSION) + os.path.sep + current_time
    # The directory where all the stable package specific files will reside
    android_version_folder = "Q"
    if str(Config.TARGET_ANDROID_VERSION).__eq__("9"):
        android_version_folder = "P"
    elif str(Config.TARGET_ANDROID_VERSION).__eq__("10"):
        android_version_folder = "Q"
    elif str(Config.TARGET_ANDROID_VERSION).__eq__("11"):
        android_version_folder = "R"

    if str(Config.ENVIRONMENT_TYPE).__eq__("production"):
        android_version_folder = str(Config.TARGET_ANDROID_VERSION)
    source_directory = str(Path(cwd).parent) + os.path.sep + str(android_version_folder)
    website_directory = str(Path(cwd).parent) + os.path.sep + "nikgapps.github.io"
    release_history_directory = str(Path(cwd).parent) + os.path.sep + "release"
    if Config.RELEASE_TYPE.__eq__("canary"):
        release_history_directory = str(Path(cwd).parent) + os.path.sep + "canary-release"

    apk_source_directly = str(Path(cwd).parent) + os.path.sep
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

    @staticmethod
    def get_file_bytes(file_name):
        file_stats = os.stat(file_name)
        # 1000 instead of 1024 because it's better to require more size than what gapps exactly takes
        return math.ceil(file_stats.st_size / 1000)

    @staticmethod
    def start_of_function():
        return time.time()

    @staticmethod
    def end_of_function(start_time, message=None):
        if message is not None:
            print()
            print("--- " + message + " ---")
        else:
            print()
        sec = round(time.time() - start_time, 0)
        seconds = int(math.fmod(sec, 60))
        minutes = int(sec // 60)
        print("--- %s seconds --- " % (time.time() - start_time))
        print("--- %s minutes %s seconds --- " % (minutes, seconds))
        print()

    @staticmethod
    def update_sourceforge_release_directory(release_type):
        if release_type == "config":
            Constants.sourceforge_release_directory = "/home/frs/project/nikgapps/Config-Releases"
        elif release_type == "canary":
            Constants.sourceforge_release_directory = "/home/frs/project/nikgapps/Canary-Releases"
        else:
            Constants.sourceforge_release_directory = "/home/frs/project/nikgapps/Releases"

    @staticmethod
    def update_android_version_dependencies():
        if str(Config.TARGET_ANDROID_VERSION).__eq__("9"):
            Constants.android_version_folder = "P"
        elif str(Config.TARGET_ANDROID_VERSION).__eq__("10"):
            Constants.android_version_folder = "Q"
        elif str(Config.TARGET_ANDROID_VERSION).__eq__("11"):
            Constants.android_version_folder = "R"
        if str(Config.ENVIRONMENT_TYPE.lower()) == "production":
            Constants.android_version_folder = str(Config.TARGET_ANDROID_VERSION)
        Constants.export_directory = str(Path(Constants.cwd).parent) + os.path.sep + "Export" + os.path.sep + str(
            Config.TARGET_ANDROID_VERSION) + os.path.sep + Constants.current_time
        Constants.source_directory = str(Path(Constants.cwd).parent) + os.path.sep + str(
            Constants.android_version_folder)
        print("Source: " + Constants.source_directory)
        Constants.release_directory = str(Path(Constants.cwd).parent) + os.path.sep + "Releases" + os.path.sep + str(
            Config.TARGET_ANDROID_VERSION)
        Constants.temp_packages_directory = str(
            Path(Constants.cwd).parent) + os.path.sep + "TempPackages" + os.path.sep + str(
            Constants.android_version_folder)

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
                    print_progress += Constants.progress_complete
                else:
                    print_progress += Constants.progress_remaining
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
        base_name = Constants.get_base_name(install_path)
        dir_name = Constants.get_parent_path(install_path)
        dir_name = str(dir_name).replace("\\system", "").replace("\\product", "")
        if export_directory is not None:
            output = export_directory + Constants.dir_sep
        else:
            output = Constants.export_directory + Constants.dir_sep
        if app_set is not None:
            output += app_set + Constants.dir_sep
        output += str(pkg) + Constants.dir_sep + str(
            dir_name).replace("\\", "___") + Constants.dir_sep + base_name
        if not os.path.exists(Path(output).parent):
            os.makedirs(Path(output).parent)
        return Path(output)
