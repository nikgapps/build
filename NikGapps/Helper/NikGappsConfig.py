import os

from . import Package, AppSet, AddonSet
from .FileOp import FileOp
from NikGappsPackages import NikGappsPackages


class NikGappsConfig:

    def __init__(self, config_path):
        self.config_path = config_path

    def get_android_version(self):
        if str(self.config_path).__contains__(os.path.sep + "9" + os.path.sep):
            return 9
        elif str(self.config_path).__contains__(os.path.sep + "10" + os.path.sep):
            return 10
        elif str(self.config_path).__contains__(os.path.sep + "11" + os.path.sep):
            return 11
        elif str(self.config_path).__contains__(os.path.sep + "12" + os.path.sep):
            return 12
        else:
            return 0

    def get_config_dictionary(self):
        lines = {}
        for line in FileOp.read_string_file(self.config_path):
            if line.__eq__('') or line.__eq__('\n') or line.startswith('#') \
                    or line.startswith("mode=") \
                    or line.startswith("LogDirectory=") \
                    or line.startswith("Version=") \
                    or line.__contains__(".d=") \
                    or line.startswith("File Not Found") \
                    or line.startswith("WipeRuntimePermissions=") \
                    or not line.__contains__("=") \
                    or line.startswith("WipeDalvikCache="):
                continue
            lines[line.split('=')[0]] = line.split('=')[1].replace('\n', '')
        return lines

    def get_config_packages(self):
        config_dict = self.get_config_dictionary()
        print(config_dict)
        app_set_list = []
        pre_defined_addons = []
        for addons in AddonSet.get_addon_packages():
            pre_defined_addons.append(addons.title)
        for app_set in NikGappsPackages.get_packages("all"):
            app_set: AppSet
            if app_set.title not in config_dict:
                continue
            pkg_len = len(app_set.package_list)
            new_app_set = None
            if pkg_len > 1 and str(config_dict[app_set.title]) == "1":
                new_app_set = AppSet(app_set.title)
                for pkg in app_set.package_list:
                    pkg: Package
                    if str(">>" + pkg.package_title) not in config_dict:
                        if app_set.title in pre_defined_addons:
                            # these will be the addons who can be directly added
                            new_app_set.add_package(pkg)
                        continue
                    if config_dict[str(">>" + pkg.package_title)] == "1":
                        new_app_set.add_package(pkg)
                    else:
                        print("Package disabled " + pkg.package_title)
            elif pkg_len == 1 and str(config_dict[app_set.title]) == "1":
                new_app_set = app_set
            if new_app_set is not None:
                app_set_list.append(new_app_set)
        return app_set_list
