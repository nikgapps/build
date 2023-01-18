import json
from NikGapps.Helper import ConfigObj, FileOp, AppSet, Package, C, Logs
from NikGappsPackages import NikGappsPackages


class NikGappsConfig:

    def __init__(self, config_path=None, config_version=None, use_zip_config=None, raw_config=None):
        self.config_version = 23
        if config_version is not None:
            self.config_version = config_version
        self.default_mode = "default"
        self.install_mode = "install"
        self.enabled_mode = 1
        self.disabled_mode = 0
        self.use_zip_config = 0
        if use_zip_config is not None:
            self.use_zip_config = use_zip_config
        self.config_objects = self.build_config_objects()
        self.config_package_list = []
        self.config_dict = None
        if raw_config is not None:
            self.config_dict = self.get_config_dictionary(raw_config)
        if config_path is not None:
            self.config_path = config_path
            self.config_dict = self.get_config_dictionary()
        if self.config_dict is not None:
            for config_obj in self.config_objects:
                if config_obj.key in self.config_dict:
                    config_obj.value = str(self.config_dict[config_obj.key])
            self.config_package_list = self.get_config_packages()

    def build_config_objects(self):
        version = ConfigObj("Version", self.config_version)
        log_directory = ConfigObj("LogDirectory", self.default_mode)
        log_directory.description = """# set this to the directory you want to copy the logs to.
# for e.g. LogDirectory="/system/etc" will install the logs to /system/etc/nikgapps_logs directory
# by default it will install it to /sdcard/NikGapps/nikgapps_logs"""
        install_partition = ConfigObj("InstallPartition", self.default_mode)
        install_partition.description = "# set to /system, /product or" \
                                        " /system_ext if you want to force the installation to aforementioned locations"
        mode = ConfigObj("mode", self.install_mode)
        mode.description = "# set to uninstall if you want to uninstall any google app, " \
                           "also set the value of google app below to -1"
        wipe_dalvik_cache = ConfigObj("WipeDalvikCache", self.enabled_mode)
        wipe_dalvik_cache.description = "# set WipeDalvikCache=0 if you don't want the installer " \
                                        "to wipe dalvik/cache after installing the gapps"
        wipe_runtime_permissions = ConfigObj("WipeRuntimePermissions", self.disabled_mode)
        wipe_runtime_permissions.description = "# set WipeRuntimePermissions=1 if you want to wipe runtime permissions"
        execute_d = ConfigObj("execute.d", self.enabled_mode)
        execute_d.description = "# Addon.d config set it to 0 to skip the " \
                                "automatic backup/restore while flashing the rom"
        use_zip_config = ConfigObj("use_zip_config", self.use_zip_config)
        use_zip_config.description = "# if you want to force the installer to use the config from gapps zip file, " \
                                     "set below to 1"
        gms_optimization = ConfigObj("gms_optimization", self.disabled_mode)
        gms_optimization.description = "# set this to 1 if you want to enable gms optimization, " \
                                       "careful while doing it, you may experience issues like delayed notification " \
                                       "with some Roms"
        config_list = [version, log_directory, install_partition, mode, wipe_dalvik_cache, wipe_runtime_permissions,
                       execute_d, use_zip_config, gms_optimization]
        return config_list

    def get_config_dictionary(self, raw_config=None):
        lines = {}
        for line in FileOp.read_string_file(self.config_path) if raw_config is None else raw_config.splitlines():
            if line.__eq__('') or line.__eq__('\n') or line.startswith('#') \
                    or line.startswith("File Not Found") \
                    or line.startswith("use_zip_config=") \
                    or not line.__contains__("="):
                continue
            lines[line.split('=')[0]] = line.split('=')[1].replace('\n', '')
        return lines

    def get_config_packages(self):
        config_dict = self.config_dict
        print(json.dumps(config_dict, indent=4))
        # pprint.pprint(config_dict)
        app_set_list = []
        pre_defined_addons = []
        for addons in NikGappsPackages.get_packages("addons"):
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

    def get_dictionary_value(self, key):
        if key in self.config_dict:
            return str(self.config_dict[key])
        return str(0)

    def get_nikgapps_config(self):
        nikgapps_config_lines = "# NikGapps configuration file\n\n"
        nikgapps_config_lines += "# If you are not sure about the config, " \
                                 "just skip making changes to it or comment it by adding # before it\n"
        nikgapps_config_lines += "# visit https://nikgapps.com/misc/2020/11/22/" \
                                 "NikGapps-Config.html to read everything about nikgapps\n\n"

        for config_obj in self.config_objects:
            nikgapps_config_lines += config_obj.get_string()

        nikgapps_config_lines += "# Following are the packages with default configuration\n"

        for app_set in NikGappsPackages.get_packages("full"):
            if len(app_set.package_list) > 1:
                nikgapps_config_lines += "\n# Set " + app_set.title + "=0 if you want to skip installing all " \
                                                                      "packages belonging to " \
                                                                      "" + app_set.title + " Package\n"
                if self.config_dict is not None:
                    nikgapps_config_lines += app_set.title + "=" + self.get_dictionary_value(app_set.title) + "\n"
                    for pkg in app_set.package_list:
                        entry = ">>" + pkg.package_title
                        nikgapps_config_lines += entry + "=" + self.get_dictionary_value(entry) + "\n"
                else:
                    nikgapps_config_lines += app_set.title + "=" + str(1) + "\n"
                    for pkg in app_set.package_list:
                        nikgapps_config_lines += ">>" + pkg.package_title + "=" + str(pkg.enabled) + "\n"
                nikgapps_config_lines += "\n"
            else:
                if self.config_dict is not None:
                    for pkg in app_set.package_list:
                        entry = pkg.package_title
                        nikgapps_config_lines += entry + "=" + self.get_dictionary_value(entry) + "\n"
                else:
                    for pkg in app_set.package_list:
                        nikgapps_config_lines += pkg.package_title + "=" + str(pkg.enabled) + "\n"
        for app_set in NikGappsPackages.get_packages("go"):
            if len(app_set.package_list) > 1:
                nikgapps_config_lines += "# Set " + app_set.title + "=0 if you want to skip installing all " \
                                                                    "packages belonging to " \
                                                                    "" + app_set.title + " Package\n"
                if self.config_dict is not None:
                    nikgapps_config_lines += app_set.title + "=" + self.get_dictionary_value(app_set.title) + "\n\n"
                else:
                    nikgapps_config_lines += app_set.title + "=" + str(1) + "\n\n"
                nikgapps_config_lines += "# Setting CoreGo=0 will not skip following packages," \
                                         " set them to 0 if you want to skip them  \n"
            else:
                if self.config_dict is not None:
                    nikgapps_config_lines += app_set.title + "=" + self.get_dictionary_value(app_set.title) + "\n"
                else:
                    nikgapps_config_lines += app_set.title + "=" + str(1) + "\n"
        nikgapps_config_lines += "\n"
        nikgapps_config_lines += "# Following are the Addon packages NikGapps supports\n"
        for app_set in NikGappsPackages.get_packages("addons"):
            if self.config_dict is not None:
                nikgapps_config_lines += app_set.title + "=" + self.get_dictionary_value(app_set.title) + "\n"
            else:
                nikgapps_config_lines += app_set.title + "=" + str(1) + "\n"
        return nikgapps_config_lines

    def validate(self):
        return True
