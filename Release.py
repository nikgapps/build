import os
from pathlib import Path

import Config
from NikGapps.Helper import Logs, NikGappsConfig, FileOp, Git
from Build import Build
from NikGappsPackages import NikGappsPackages
from NikGapps.Helper.Assets import Assets
from NikGapps.Helper.Export import Export
from NikGapps.Helper.Constants import Constants
from NikGapps.Helper.Cmd import Cmd
from NikGapps.Helper.AppSet import AppSet
from NikGapps.Helper.Package import Package


class Release:
    @staticmethod
    def zip(build_package_list, sent_message=None):
        for pkg_type in build_package_list:
            print("Currently Working on " + pkg_type)
            os.environ['pkg_type'] = str(pkg_type)
            if str(pkg_type).__contains__("addons"):
                for app_set in NikGappsPackages.get_packages(pkg_type):
                    print("Building for " + str(app_set.title))
                    if sent_message is not None:
                        sent_message.edit_text("Building for " + str(app_set.title))
                    Release.zip_package(sent_message,
                                        Constants.release_directory + Constants.dir_sep + str(
                                            "addons") + Constants.dir_sep + "NikGapps-Addon-"
                                        + Constants.android_version_folder + "-" + app_set.title + "-" + str(
                                            Logs.get_current_time()) + ".zip", [app_set])
            elif pkg_type == "config":
                config_repo = Git(Constants.config_directory)
                for config_files in Path(Constants.config_directory).rglob("*.config"):
                    if Path(config_files).is_dir() or str(config_files).__contains__(
                            os.path.sep + "archive" + os.path.sep):
                        continue
                    # Create config obj to handle config operations
                    config_obj = NikGappsConfig(config_files, use_zip_config=1)
                    # Get Target Android Version so the packages can be created
                    android_version = config_obj.get_android_version()
                    if str(android_version) != str(Config.TARGET_ANDROID_VERSION):
                        continue
                    Constants.update_android_version_dependencies()
                    # Generate a file name for the zip
                    file_name = Constants.release_directory
                    config_file_name = os.path.splitext(os.path.basename(config_files))[0].replace(" ", "")
                    config_file_name = os.path.splitext(os.path.basename(config_file_name))[0].replace("'", "")
                    file_name = file_name + Constants.dir_sep + Logs.get_file_name(config_file_name,
                                                                                   str(Config.TARGET_ANDROID_VERSION))
                    # Build the packages from the directory
                    print("Building for " + str(config_files))
                    if sent_message is not None:
                        sent_message.edit_text("Building for " + str(pkg_type))
                    # Create a zip out of filtered packages
                    zip_status = Release.zip_package(sent_message, file_name, app_set_list=None, config_obj=config_obj)
                    # move the config file to archive
                    if zip_status:
                        print("Source: " + str(config_files))
                        destination = Constants.config_directory + os.path.sep + str("archive") + os.path.sep + str(
                            Config.TARGET_ANDROID_VERSION) + os.path.sep + config_file_name + "_" + str(
                            Logs.get_current_time()) + ".config"
                        print("Destination: " + destination)
                        print("Moving the config file to archive")
                        FileOp.move_file(config_files, destination)
                        # commit the changes
                        config_repo.update_config_changes("Moved " + str(
                            Config.TARGET_ANDROID_VERSION) + os.path.sep + config_file_name + ".config to archive" + os.path.sep + str(
                            Config.TARGET_ANDROID_VERSION) + os.path.sep + config_file_name + "_" + str(
                            Logs.get_current_time()) + ".config")
                    elif zip_status is None:
                        print("Delete the config file")
                        FileOp.remove_file(config_files)
                        # commit the changes
                        config_repo.update_config_changes("Deleting " + str(
                            Config.TARGET_ANDROID_VERSION) + os.path.sep + config_file_name
                                                          + ".config since it doesn't follow defined protocols")
                    else:
                        print("Failed to create zip!")
            elif pkg_type == "debloater":
                if Config.CREATE_DEBLOATER_ZIP:
                    file_name = Constants.release_directory + Constants.dir_sep + "Debloater-" + str(
                        Logs.get_current_time()) + ".zip"
                    z = Export(file_name)
                    config_obj = NikGappsConfig()
                    z.zip(config_obj, sent_message)
            else:
                if pkg_type in Config.BUILD_PACKAGE_LIST:
                    file_name = Constants.release_directory
                    file_name = file_name + Constants.dir_sep + Logs.get_file_name(pkg_type.lower(),
                                                                                   str(Config.TARGET_ANDROID_VERSION))
                    # Build the packages from the directory
                    print("Building for " + str(pkg_type))
                    if sent_message is not None:
                        sent_message.edit_text("Building for " + str(pkg_type))
                    Release.zip_package(sent_message, file_name,
                                        NikGappsPackages.get_packages(pkg_type))
                else:
                    for app_set in NikGappsPackages.get_packages(pkg_type):
                        if app_set is None:
                            print("AppSet/Package Does not Exists: " + str(pkg_type))
                            if sent_message is not None:
                                sent_message.edit_text("AppSet/Package Does not Exists: " + str(pkg_type))
                        else:
                            print("Building for " + str(app_set.title))
                            if sent_message is not None:
                                sent_message.edit_text("Building for " + str(app_set.title))
                            Release.zip_package(sent_message, Constants.release_directory
                                                + Constants.dir_sep + "addons" + Constants.dir_sep + "NikGapps-Addon-"
                                                + Constants.android_version_folder + "-" + app_set.title + "-"
                                                + str(Logs.get_current_time()) + ".zip", [app_set])
            os.environ['pkg_type'] = ''

    @staticmethod
    def get_config_packages(file_path):
        package_list = []
        pkg_list = []
        config_lines = Assets.get_string_resource(file_path)
        for line in config_lines:
            if not str(line).startswith("#") and str(line).__contains__("=1"):
                pkg_list.append(line.split("=")[0])
        for pkg in NikGappsPackages.get_packages(NikGappsPackages.all_packages):
            if pkg.title in pkg_list:
                package_list.append(pkg)
        return package_list

    @staticmethod
    def zip_package(sent_message, package_name, app_set_list, config_obj: NikGappsConfig = None):
        if config_obj is not None:
            config_obj: NikGappsConfig
            if config_obj.config_package_list.__len__() > 0:
                app_set_list = config_obj.config_package_list
        else:
            config_obj = NikGappsConfig()

        if app_set_list is not None and app_set_list.__len__() > 0:
            file_name = package_name
            config_obj.config_package_list = Build.build_from_directory(app_set_list)
            print("Exporting " + str(file_name))
            if sent_message is not None:
                sent_message.edit_text("Exporting " + str(file_name))
            z = Export(file_name)
            return z.zip(config_obj, sent_message)
        else:
            print("Package List Empty!")

    @staticmethod
    def package(fetch_package, sent_message=None):
        cmd = Cmd()
        if fetch_package.lower() == "all":
            fetch_package = "full"
        if Config.ADB_ROOT_ENABLED:
            if cmd.established_device_connection_as_root():
                Config.ADB_ROOT_ENABLED = True
            else:
                print("Device not found! or failed to acquire Root permissions")
                return []
        return Release.fetch_packages(sent_message, fetch_package)

    @staticmethod
    def fetch_packages(sent_message, fetch_package):
        # Get the list of packages that we want to pull from connected device
        app_set_list = NikGappsPackages.get_packages(fetch_package)
        # Fetch all the packages from the device
        # We will check for errors here (need to make sure we pulled all the files we were looking for
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        if app_set_list is None or app_set_list[0] is None:
            return []
        updated_pkg_list = []
        failure_summary = ""
        for app_set in app_set_list:
            app_set: AppSet
            message = "--> Working on " + app_set.title
            if sent_message is not None:
                sent_message.edit_text(message)
            print(message)
            for pkg in app_set.package_list:
                pkg: Package
                pkg.validate()
                failure_summary += pkg.failure_logs
                message = pkg.package_title + " Ready to be fetched"
                if sent_message is not None:
                    sent_message.edit_text(message)
                print(message)
                if pkg.primary_app_location is not None or pkg.package_name is None \
                        or pkg.predefined_file_list.__len__() > 0:
                    pkg.pull_package_files(app_set.title)
                    failure_summary += pkg.failure_logs
                    message = pkg.package_title + " Successfully Fetched!"
                    if sent_message is not None:
                        sent_message.edit_text(message)
                    print(message)
                updated_pkg_list.append(pkg)
        if not str(failure_summary).__eq__(""):
            print("")
            print("Failure Summary:")
            print(failure_summary)
        return updated_pkg_list
