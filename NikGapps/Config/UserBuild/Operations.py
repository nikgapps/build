import json
import os

import Config
from Build import Build
from NikGapps.Config.NikGappsConfig import NikGappsConfig
from NikGapps.Helper import Constants, Logs, Export, FileOp, Upload, Git


class Operations:

    @staticmethod
    def build(config_obj: NikGappsConfig, android_version, upload: Upload = None):
        # Generate a file name for the zip
        file_name = Constants.release_directory
        config_file_name = os.path.splitext(os.path.basename(config_obj.config_path))[0].replace(" ", "")
        config_file_name = os.path.splitext(os.path.basename(config_file_name))[0].replace("'", "")
        file_name = file_name + Constants.dir_sep + Logs.get_file_name(config_file_name, android_version)
        # Build the packages from the directory
        print("Building for " + str(config_obj.config_path))
        # Create a zip out of filtered packages
        config_obj.config_package_list = Build.build_from_directory(config_obj.config_package_list)
        print("Exporting " + str(file_name))
        z = Export(file_name)
        result = z.zip(app_set_list=config_obj.config_package_list, config_string=config_obj.get_nikgapps_config())
        if result[1] and Config.UPLOAD_FILES:
            u = upload if upload is not None else Upload()
            print("Uploading " + str(result[0]))
            u.upload(result[0])
            print("Done")
            return True
        else:
            return False
