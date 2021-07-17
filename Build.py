from pathlib import Path
from NikGapps.Helper.Constants import Constants
from NikGapps.Helper.Package import Package
from NikGapps.Helper.FileOp import FileOp
from NikGapps.Helper.Cmd import Cmd
from NikGapps.Helper.AppSet import AppSet


class Build:
    project_name = "NikGapps"

    # Just provide the package list and it will pick them up from the directory and build them for you
    @staticmethod
    def build_from_directory(app_set_build_list):
        dir_path = Constants.source_directory
        cmd = Cmd()
        app_set_list = []
        for app_set in app_set_build_list:
            app_set: AppSet
            name = app_set.title
            app_set_path = Constants.path.join(dir_path, name)
            package_list = []
            for package in app_set.package_list:
                package: Package
                pkg_to_build = package
                package_title = pkg_to_build.package_title
                pkg_path = Constants.path.join(app_set_path, package_title)
                file_dict = dict()
                folder_dict = dict()
                install_list = []
                package_name = None
                app_type = None
                primary_app_location = None
                delete_files_list = []
                # print("Package Name: " + package.title)
                for pkg_files in Path(pkg_path).rglob("*"):
                    if Path(pkg_files).is_dir() or str(pkg_files).__contains__(".git") \
                            or str(pkg_files).endswith(".gitattributes") or str(pkg_files).endswith("README.md"):
                        continue
                    if str(pkg_files).endswith(Constants.DELETE_FILES_NAME):
                        for str_data in FileOp.read_string_file(pkg_files):
                            delete_file = str_data[:-1]
                            if delete_file not in pkg_to_build.delete_files_list:
                                delete_files_list.append(delete_file)
                        continue
                    pkg_files_path = str(pkg_files)
                    pkg_files_path = pkg_files_path[pkg_files_path.find("___") + 3:]
                    if pkg_to_build.package_name is not None and str(pkg_files_path).endswith(".apk") and not str(
                            pkg_files).__contains__("split_") and not str(pkg_files).__contains__("___m___") \
                            and not str(pkg_files).__contains__("___overlay"):
                        primary_app_location = pkg_files.absolute()
                        package_name = cmd.get_package_name(primary_app_location)
                        # print("File: " + package_name)
                        package_version = cmd.get_package_version(primary_app_location)
                        # print("Package Version: " + package_version)
                        if str(primary_app_location).__contains__("___priv-app___"):
                            app_type = Constants.is_priv_app
                        elif str(primary_app_location).__contains__("___app___"):
                            app_type = Constants.is_system_app
                    for folder in FileOp.get_dir_list(pkg_files_path):
                        folder_dict[folder] = folder
                    # We don't need this but for the sake of consistency
                    install_list.append(pkg_files_path.replace("___", "/"))
                    file_dict[pkg_files.absolute()] = str(pkg_files_path.replace("___", "/")).replace("\\", "/")
                if primary_app_location is not None:
                    title = Constants.get_base_name(primary_app_location)[:-4]
                else:
                    title = package_title
                pkg = Package(title, package_name, app_type, package_title)
                pkg.install_list = install_list
                pkg.partition = pkg_to_build.partition
                pkg.clean_flash_only = pkg_to_build.clean_flash_only
                pkg.file_dict = file_dict
                pkg.folder_dict = folder_dict
                pkg.additional_installer_script = pkg_to_build.additional_installer_script
                pkg.primary_app_location = primary_app_location
                # Generate priv-app permissions whitelist
                if pkg.primary_app_location is not None and app_type == Constants.is_priv_app:
                    permissions_list = cmd.get_white_list_permissions(primary_app_location)
                    if permissions_list.__len__() >= 1 and not permissions_list[0].__contains__("Exception"):
                        pkg.generate_priv_app_whitelist(app_set.title, permissions_list, Constants.source_directory)
                pkg.delete_rom_files_list = pkg_to_build.delete_rom_files_list
                # Add the deleted files from the pkg_to_build object
                for delete_file in pkg_to_build.delete_files_list:
                    delete_files_list.append(delete_file)
                pkg.delete_files_list = delete_files_list
                package_list.append(pkg)
            if package_list.__len__() > 0:
                app_set_to_build = AppSet(app_set.title, package_list)
                app_set_list.append(app_set_to_build)
        return app_set_list
