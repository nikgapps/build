import os
from pathlib import Path

import Config
from NikGapps.Config.ConfigDirectoy import ConfigDirectory
from NikGapps.Config.NikGappsConfig import NikGappsConfig
from NikGapps.Config.UserBuild.Operations import Operations
from NikGapps.Helper import C, B64, FileOp, Git, Logs


class OnDemand:

    @staticmethod
    def build_from_config_byte(config_name, config_in_byte, android_version):
        try:
            config_string = B64.b64d(config_in_byte)
            return OnDemand.build_from_config_string(config_name, config_string, android_version)
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def build_from_config_string(config_name, config_string, android_version):
        try:
            config_dir = ConfigDirectory()
            config_repo = config_dir.setup(override_dir=False)
            if config_repo is not None:
                path = config_dir.write_user_config(config_string=config_string, android_version=android_version,
                                                    config_name=config_name)
                return OnDemand.build_from_config_file(config_path=path, android_version=android_version,
                                                       config_repo=config_repo)
        except Exception as e:
            print(e)
            return False
        return False

    @staticmethod
    def build_from_config_file(config_path, android_version, config_repo, exclusive=False):
        config_obj = NikGappsConfig(config_path=config_path, use_zip_config=1)
        result = False
        if config_obj.validate():
            # create a config based build
            C.update_android_version_dependencies()
            if not exclusive:
                C.update_sourceforge_release_directory()
                result = Operations.build(config_obj, android_version, config_repo)
            else:
                config_obj.exclusive = True
                file_name = f"{Config.EXCLUSIVE_FOLDER}-Releases/{Logs.get_path(config_obj.get_user_name_from_config(), C.get_android_code(android_version))}"
                C.update_sourceforge_release_directory(file_name)
                result = Operations.build(config_obj, android_version, config_repo,
                                          release_directory=C.sourceforge_release_directory)
        else:
            print("Delete the config file")
            FileOp.remove_file(config_path)
            # commit the changes
            config_repo.update_config_changes("Deleting " + str(
                Config.TARGET_ANDROID_VERSION) + os.path.sep + os.path.basename(
                config_path) + ".config since it doesn't follow defined protocols")
        return result

    @staticmethod
    def build_all_configs(android_version, exclusive=False):
        Config.TARGET_ANDROID_VERSION = str(android_version)
        config_repo = Git(C.config_directory)
        config_folder = Path(C.config_directory + C.dir_sep + str(android_version)) if not exclusive else Path(
            C.config_directory + C.dir_sep + f"{Config.EXCLUSIVE_FOLDER.lower()}" + C.dir_sep + str(android_version))
        for config_file in config_folder.rglob("*.config"):
            if not OnDemand.build_from_config_file(config_file, android_version, config_repo, exclusive):
                print("Failed to build from config file: " + str(config_file))
            else:
                print("Successfully built from config file: " + str(config_file))
