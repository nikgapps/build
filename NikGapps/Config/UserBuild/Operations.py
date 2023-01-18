import json
import os

import Config
from Build import Build
from NikGapps.Config.NikGappsConfig import NikGappsConfig
from NikGapps.Helper import C, Logs, Export, FileOp, Upload


class Operations:

    @staticmethod
    def build(config_obj: NikGappsConfig, android_version, config_repo, upload: Upload = None):
        # Generate a file name for the zip
        file_name = C.release_directory
        config_file_name = os.path.splitext(os.path.basename(config_obj.config_path))[0].replace(" ", "")
        config_file_name = os.path.splitext(os.path.basename(config_file_name))[0].replace("'", "")
        file_name = file_name + C.dir_sep + Logs.get_file_name(config_file_name, android_version)
        # Build the packages from the directory
        print("Building for " + str(config_obj.config_path))
        # Create a zip out of filtered packages
        config_obj.config_package_list = Build.build_from_directory(config_obj.config_package_list)
        print("Exporting " + str(file_name))
        initial_message = "Android Version: " + str(android_version) + "\n"
        initial_message += "Building Config: " + str(os.path.basename(config_obj.config_path)) + "\n"
        initial_message += "File Name: " + str(os.path.basename(file_name)) + "\n"
        C.telegram.message(initial_message)
        if "TelegramUsername" in config_obj.config_dict:
            tg_name = config_obj.config_dict["TelegramUsername"]
            C.telegram.message(
                "Telegram User: " + ("@" + str(tg_name) if not str(tg_name).startswith('@') else str(tg_name)) + "\n")
        if "PR_NUMBER" in config_obj.config_dict:
            pr_number = config_obj.config_dict["PR_NUMBER"]
            if "PR_NAME" in config_obj.config_dict:
                pr_name = config_obj.config_dict["PR_NAME"]
                C.telegram.message(
                    f"Pull Request: #{str(pr_number)}", escape_text=False,
                    ur_link={f"#{str(pr_number)}": f"https://github.com/nikgapps/config/pull/{pr_number}"})
                C.telegram.message(f"Pull Request by: #{pr_name}\n", escape_text=False,
                                   ur_link={f"{pr_name}'s profile": f"https://github.com/{pr_name}"})
        initial_message = "__Running Status:__"
        C.telegram.message(initial_message, escape_text=False)
        z = Export(file_name)
        file_name, zip_execution_status = z.zip(app_set_list=config_obj.config_package_list,
                                                config_string=config_obj.get_nikgapps_config())
        if Config.SIGN_ZIP and (not zip_execution_status) and (not str(file_name).endswith("-signed.zip")):
            # this probably happened because the zip failed to sign, we still want to upload the unsigned zip
            zip_execution_status = True
        if zip_execution_status:
            if Config.UPLOAD_FILES:
                u = upload if upload is not None else Upload()
                print("Uploading " + str(file_name))
                execution_status = u.upload(file_name)
                print("Done")
            else:
                execution_status = True
            if execution_status:
                Operations.archive_the_config(config_obj.config_path, android_version, config_file_name, config_repo)
            else:
                C.telegram.message("- Upload failed!")
                print("Cannot move to archive as upload failed!")
            C.telegram.reset_message()
            return execution_status
        else:
            C.telegram.reset_message()
            return False

    @staticmethod
    def archive_the_config(source_config_file, android_version, config_file_name, config_repo):
        try:
            # move the config file to archive
            print("Source: " + str(source_config_file))

            todays_date = str(Logs.get_current_time())
            destination = f"{C.config_directory + os.path.sep}archive{os.path.sep}" \
                          f"{str(android_version) + os.path.sep}" \
                          f"{todays_date + os.path.sep}" \
                          f"{config_file_name}_{todays_date}.config"
            print("Destination: " + destination)
            print("Moving the config file to archive")
            FileOp.move_file(source_config_file, destination)
            # commit the changes

            commit_message = f"Moved {str(android_version) + os.path.sep + config_file_name}.config to archive" \
                             f"{os.path.sep + str(android_version) + os.path.sep + todays_date + os.path.sep}" \
                             f"{config_file_name}_{todays_date}.config"
            print(commit_message)
            config_repo.update_config_changes(commit_message)
            return True
        except Exception as e:
            print("Error while moving the config file to archive")
            print(e)
            return False
