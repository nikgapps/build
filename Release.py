import Config
from NikGapps.Helper import Logs
from Build import Build
from NikGappsPackages import NikGappsPackages
from NikGapps.Helper.Cmd import Cmd
from NikGapps.Helper.Assets import Assets
from NikGapps.Helper.Export import Export
from NikGapps.Helper.Constants import Constants
from NikGapps.Helper.AddonSet import AddonSet


class Release:
    @staticmethod
    def zip(build_package_list, sent_message=None):
        for pkg_type in build_package_list:
            print("Currently Working on " + pkg_type)
            if str(pkg_type).__contains__("addons"):
                for app_set in NikGappsPackages.get_packages(pkg_type):
                    print("Building for " + str(app_set.title))
                    if sent_message is not None:
                        sent_message.edit_text("Building for " + str(app_set.title))
                    Release.zip_package(sent_message,
                                        Constants.release_directory + Constants.dir_sep + str(
                                            "addons") + Constants.dir_sep + "NikGapps-Addon-"
                                        + Constants.android_version_folder + "-" + app_set.title + ".zip", [app_set])
            elif pkg_type == "config":
                file_name = Constants.release_directory + Constants.dir_sep + Logs.get_file_name(pkg_type.lower(), str(
                    Config.TARGET_ANDROID_VERSION))
                if sent_message is not None:
                    sent_message.edit_text("Building from config")
                Release.zip_package(sent_message, file_name,
                                    Release.get_config_packages(Constants.nikgapps_config))
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
                                                + Constants.android_version_folder + "-" + app_set.title + ".zip",
                                                [app_set])

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
    def zip_package(sent_message, package_name, app_set_list):
        if app_set_list is not None and app_set_list.__len__() > 0:
            file_name = package_name
            app_set_build_list = Build.build_from_directory(app_set_list)
            print("Exporting " + str(file_name))
            if sent_message is not None:
                sent_message.edit_text("Exporting " + str(file_name))
            z = Export(file_name)
            z.zip(app_set_build_list, sent_message)
        else:
            print("Package List Empty!")


