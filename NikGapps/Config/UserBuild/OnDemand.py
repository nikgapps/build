from NikGapps.Config.ConfigDirectoy import ConfigDirectory
from NikGapps.Config.NikGappsConfig import NikGappsConfig
from NikGapps.Config.UserBuild.Operations import Operations
from NikGapps.Helper import Constants, B64


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
            config_dir.setup(override_dir=False)
            path = config_dir.write_user_config(config_string=config_string, android_version=android_version,
                                                config_name=config_name)
            return OnDemand.build_from_config_file(config_path=path, android_version=android_version)
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def build_from_config_file(config_path, android_version):
        config_obj = NikGappsConfig(config_path=config_path, use_zip_config=1)
        result = False
        if config_obj.validate():
            # create a config based build
            Constants.update_android_version_dependencies()
            result = Operations.build(config_obj, android_version)
        return result
