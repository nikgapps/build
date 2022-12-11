import json
import os

import Config
from NikGapps.Config.NikGappsConfig import NikGappsConfig
from NikGapps.Git import PullRequest
from NikGapps.Helper import C, Git, FileOp, Upload


class ConfigOperations:
    @staticmethod
    def upload_nikgapps_config(config_obj: NikGappsConfig):
        repo_name = "git@github.com:nikgapps/tracker.git"
        repo_dir = C.pwd + C.dir_sep + "tracker"
        print()
        print("Repo Dir: " + repo_dir)
        analytics_dict = {}
        android_version_dict = Config.ANDROID_VERSIONS[str(Config.TARGET_ANDROID_VERSION)]
        key = "config_version_" + str(android_version_dict["code"])
        analytics_dict[key] = str(config_obj.config_version)
        tracker_repo = Git(repo_dir)
        tracker_repo.clone_repo(repo_name)

        if FileOp.dir_exists(repo_dir):
            print(f"{repo_dir} exists!")
            config_version_json = repo_dir + C.dir_sep + "config_version.json"
            if FileOp.file_exists(config_version_json):
                print("File Exists!")
                custom_builds_json_string = ""
                for line in FileOp.read_string_file(config_version_json):
                    custom_builds_json_string += line
                print(custom_builds_json_string)
                print()
                decoded_hand = json.loads(custom_builds_json_string)
                if decoded_hand.get(key) is not None:
                    version_on_server = decoded_hand[key]
                    print("version on server is: " + version_on_server)
                    if int(version_on_server) < int(config_obj.config_version):
                        print("server needs updating")
                        if ConfigOperations.create_nikgapps_config_and_upload(config_obj):
                            decoded_hand[key] = str(config_obj.config_version)
                            with open(config_version_json, "w") as file:
                                json.dump(decoded_hand, file, indent=2)
                        else:
                            print("Cannot update the tracker since config file failed to upload")
                    elif int(version_on_server) == int(config_obj.config_version):
                        print("server is in sync")
                    else:
                        print("server is on higher version")
                else:
                    print(f"{key} key doesn't exist! creating the file with the key")
                    if ConfigOperations.create_nikgapps_config_and_upload(config_obj):
                        decoded_hand[key] = str(config_obj.config_version)
                        with open(config_version_json, 'w') as f:
                            json.dump(decoded_hand, f, indent=2)
                            print(f"{config_version_json} file is created")
                    else:
                        print("Cannot update the tracker since config file failed to upload")

            else:
                print(config_version_json + " doesn't exist! creating the file")
                if ConfigOperations.create_nikgapps_config_and_upload(config_obj):
                    with open(config_version_json, 'w') as f:
                        json.dump(analytics_dict, f, indent=2)
                        print(f"{config_version_json} file is created")
                else:
                    print("Cannot update the tracker since config file failed to upload")
            if tracker_repo.due_changes():
                print("Updating the config version to v" + str(config_obj.config_version))
                tracker_repo.git_push("Updating config version to v" + str(config_obj.config_version),
                                      push_untracked_files=True)
            else:
                print("There is no change in config version to update!")
        else:
            print(f"{repo_dir} doesn't exist!")

    @staticmethod
    def create_nikgapps_config_and_upload(config_obj: NikGappsConfig):
        execution_status = False
        # create nikgapps.config file and upload to sourceforge
        FileOp.write_string_in_lf_file(config_obj.get_nikgapps_config(), C.temp_nikgapps_config_location)
        if FileOp.file_exists(C.temp_nikgapps_config_location):
            C.sourceforge_release_directory = "/home/frs/project/nikgapps/Releases/Config"
            u = Upload()
            if u.successful_connection:
                file_type = "config"
                # check if directory exists, if it does, we're good to upload the file
                cd = u.get_cd_with_date(Config.TARGET_ANDROID_VERSION, file_type)
                dir_exists = u.cd(cd)
                if not dir_exists:
                    print(str(cd) + " doesn't exist!")
                    # make the folder with current date if the directory doesn't exist
                    u.make_folder(Config.TARGET_ANDROID_VERSION, file_type,
                                  folder_name=f"v{config_obj.config_version}")
                    # try to cd again
                    dir_exists = u.cd(u.get_cd_with_date(Config.TARGET_ANDROID_VERSION, file_type,
                                                         input_date=f"v{config_obj.config_version}"))
                # if the directory exists, we can upload the file
                if dir_exists:
                    print("uploading " + C.temp_nikgapps_config_location + " ...")
                    u.upload_file(C.temp_nikgapps_config_location)
                    print("uploading file finished...")
                    execution_status = True
                else:
                    print("The directory doesn't exist!")
            else:
                print("The Connection Failed!")
                # make sure we close the connection
            u.close()
        return execution_status

    @staticmethod
    def get_android_version_from_path(config_obj: NikGappsConfig):
        for android_version in Config.ANDROID_VERSIONS:
            if str(config_obj.config_path).__contains__(os.path.sep + android_version + os.path.sep):
                return android_version
        return 0

    @staticmethod
    def update_configs_with_pr_details(pr_list, config_repo: Git):
        for pr in pr_list:
            pr: PullRequest
            for file in pr.file_names:
                filepath = config_repo.working_tree_dir + os.path.sep + file
                if FileOp.file_exists(filepath):
                    print("Updating " + filepath)
                    file_contents = FileOp.read_string_file(filepath)
                    file_contents.insert(0, f"# PR_NUMBER={pr.pull_number}")
                    file_contents.insert(1, f"# PR_NAME={pr.pr_name}")
                    FileOp.write_string_in_lf_file(file_contents, filepath)
                else:
                    print("File doesn't exist: " + filepath)
        if config_repo.due_changes():
            config_repo.git_push("Updated config files with PR details", push_untracked_files=True)
