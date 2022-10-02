import json
import os

import Config
from Build import Build
from NikGapps.Config.NikGappsConfig import NikGappsConfig
from NikGapps.Helper import Constants, Logs, Export, FileOp, Upload


class Operations:

    @staticmethod
    def build(config_obj: NikGappsConfig, android_version, config_repo, upload: Upload = None):
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
        if result[1]:
            if Config.UPLOAD_FILES:
                u = upload if upload is not None else Upload()
                print("Uploading " + str(result[0]))
                execution_status = u.upload(result[0])
                print("Done")
            else:
                execution_status = True
            if execution_status:
                Operations.archive_the_config(config_obj.config_path, android_version, config_file_name, config_repo)
            else:
                print("Cannot move to archive as upload failed!")
            return execution_status
        else:
            return False

    @staticmethod
    def archive_the_config(source_config_file, android_version, config_file_name, config_repo):
        try:
            # move the config file to archive
            print("Source: " + str(source_config_file))

            todays_date = str(Logs.get_current_time())
            destination = f"{Constants.config_directory + os.path.sep}archive{os.path.sep}" \
                          f"{android_version + os.path.sep}" \
                          f"{todays_date + os.path.sep}" \
                          f"{config_file_name}_{todays_date}.config"
            print("Destination: " + destination)
            print("Moving the config file to archive")
            FileOp.move_file(source_config_file, destination)
            # commit the changes

            commit_message = f"Moved {android_version + os.path.sep + config_file_name}.config to archive" \
                             f"{os.path.sep + android_version + os.path.sep + todays_date + os.path.sep}" \
                             f"{config_file_name}_{todays_date}.config"
            print(commit_message)
            config_repo.update_config_changes(commit_message)
            return True
        except Exception as e:
            print("Error while moving the config file to archive")
            print(e)
            return False
