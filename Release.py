import os
from pathlib import Path

import Config
from NikGapps.Config.ConfigOperations import ConfigOperations
from NikGapps.Config.NikGappsConfig import NikGappsConfig
from NikGapps.Helper import Logs, FileOp, Git, Upload
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
    def zip(build_package_list, upload: Upload = None):
        av = str(Config.TARGET_ANDROID_VERSION)
        for pkg_type in build_package_list:
            print("Currently Working on " + pkg_type)
            os.environ['pkg_type'] = str(pkg_type)
            if str(pkg_type).__contains__("addons"):
                for app_set in NikGappsPackages.get_packages(pkg_type):
                    print("Building for " + str(app_set.title))
                    Release.zip_package(Constants.release_directory + Constants.dir_sep + str(
                        "addons") + Constants.dir_sep + "NikGapps-Addon-"
                                        + Constants.android_version_folder + "-" + app_set.title + "-" + str(
                        Logs.get_current_time()) + ".zip", [app_set], upload=upload)
            elif pkg_type == "debloater":
                if Config.CREATE_DEBLOATER_ZIP:
                    file_name = Constants.release_directory + Constants.dir_sep + "Debloater-" + str(
                        Logs.get_current_time()) + ".zip"
                    z = Export(file_name)
                    config_obj = NikGappsConfig()
                    result = z.zip(app_set_list=config_obj.config_package_list,
                                   config_string=config_obj.get_nikgapps_config())
                    if result[1] and Config.UPLOAD_FILES:
                        u = upload if upload is not None else Upload()
                        print("Uploading " + str(result[0]))
                        execution_status = u.upload(result[0])
                        print("Done")
                        return execution_status
                    else:
                        print("Failed to create zip!")
            else:
                if pkg_type in Config.BUILD_PACKAGE_LIST:
                    file_name = Constants.release_directory
                    file_name = file_name + Constants.dir_sep + Logs.get_file_name(pkg_type.lower(),
                                                                                   str(Config.TARGET_ANDROID_VERSION))
                    # Build the packages from the directory
                    print("Building for " + str(pkg_type))
                    Release.zip_package(file_name,
                                        NikGappsPackages.get_packages(pkg_type), upload=upload)
                else:
                    for app_set in NikGappsPackages.get_packages(pkg_type):
                        if app_set is None:
                            print("AppSet/Package Does not Exists: " + str(pkg_type))
                        else:
                            print("Building for " + str(app_set.title))
                            Release.zip_package(Constants.release_directory
                                                + Constants.dir_sep + "addons" + Constants.dir_sep + "NikGapps-Addon-"
                                                + Constants.android_version_folder + "-" + app_set.title + "-"
                                                + str(Logs.get_current_time()) + ".zip", [app_set], upload=upload)
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
    def zip_package(package_name, app_set_list, config_obj: NikGappsConfig = None, upload: Upload = None):
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
            z = Export(file_name)
            result = z.zip(app_set_list=config_obj.config_package_list, config_string=config_obj.get_nikgapps_config())
            if result[1] and Config.UPLOAD_FILES:
                u = upload if upload is not None else Upload()
                print("Uploading " + str(result[0]))
                execution_status = u.upload(result[0])
                print("Done")
                return execution_status
        else:
            print("Package List Empty!")
            return False

    @staticmethod
    def package(fetch_package):
        cmd = Cmd()
        if fetch_package.lower() == "all":
            fetch_package = "full"
        if Config.ADB_ROOT_ENABLED:
            if cmd.established_device_connection_as_root():
                Config.ADB_ROOT_ENABLED = True
            else:
                print("Device not found! or failed to acquire Root permissions")
                return []
        return Release.fetch_packages(fetch_package)

    @staticmethod
    def fetch_packages(fetch_package):
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
            print(message)
            for pkg in app_set.package_list:
                pkg: Package
                pkg.validate()
                failure_summary += pkg.failure_logs
                message = pkg.package_title + " Ready to be fetched"
                print(message)
                if pkg.primary_app_location is not None or pkg.package_name is None \
                        or pkg.predefined_file_list.__len__() > 0:
                    pkg.pull_package_files(app_set.title)
                    failure_summary += pkg.failure_logs
                    message = pkg.package_title + " Successfully Fetched!"
                    print(message)
                updated_pkg_list.append(pkg)
        if not str(failure_summary).__eq__(""):
            print("")
            print("Failure Summary:")
            print(failure_summary)
        return updated_pkg_list
