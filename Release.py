import os

import Config
from NikGapps.Config.NikGappsConfig import NikGappsConfig
from NikGapps.Helper import Logs, Upload
from Build import Build
from NikGappsPackages import NikGappsPackages
from NikGapps.Helper.Export import Export
from NikGapps.Helper.C import C
from NikGapps.Helper.Cmd import Cmd
from NikGapps.Helper.AppSet import AppSet
from NikGapps.Helper.Package import Package


class Release:
    @staticmethod
    def zip(build_package_list, upload: Upload = None):
        for pkg_type in build_package_list:
            print("Currently Working on " + pkg_type)
            os.environ['pkg_type'] = str(pkg_type)
            if str(pkg_type).__contains__("addons"):
                for app_set in NikGappsPackages.get_packages(pkg_type):
                    print("Building for " + str(app_set.title))
                    Release.zip_package(C.release_directory + C.dir_sep + str(
                        "addons") + C.dir_sep + "NikGapps-Addon-"
                                        + C.android_version_folder + "-" + app_set.title + "-" + str(
                        Logs.get_current_time()) + ".zip", [app_set], upload=upload)
            elif str(pkg_type).lower() == "debloater":
                if Config.CREATE_DEBLOATER_ZIP:
                    file_name = C.release_directory + C.dir_sep + "Debloater-" + str(
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
                    file_name = C.release_directory
                    file_name = file_name + C.dir_sep + Logs.get_file_name(pkg_type.lower(),
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
                            Release.zip_package(C.release_directory
                                                + C.dir_sep + "addons" + C.dir_sep + "NikGapps-Addon-"
                                                + C.android_version_folder + "-" + app_set.title + "-"
                                                + str(Logs.get_current_time()) + ".zip", [app_set], upload=upload)
            os.environ['pkg_type'] = ''

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
