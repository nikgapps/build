import sys
from pathlib import Path
import Config

from NikGapps.Config.UserBuild.OnDemand import OnDemand
from NikGapps.Git.GitApi import GitApi
from NikGapps.Helper import Git, Args
from Operation import Operation
from NikGapps.Helper.Constants import Constants
from NikGapps.Helper.FileOp import FileOp

actual_start_time = Constants.start_of_function()
print("Checking if there is any existing workflow in progress")

try:
    workflows = GitApi.get_running_workflows(authenticate=False)
except Exception as e:
    print(str(e))
    try:
        workflows = GitApi.get_running_workflows(authenticate=True)
    except Exception as e:
        print(str(e))
        workflows = []

print("Total Open Workflows: " + str(len(workflows)))

if len(workflows) > 1:
    print("Open workflows detected, Let's wait for open workflows to finish")
    exit(0)
if Config.BUILD_CONFIG:
    args = Args()
    android_versions = args.get_android_versions()
    print("---------------------------------------")
    print("Android Versions to build: " + str(android_versions))
    print("---------------------------------------")
    if FileOp.dir_exists(Constants.config_directory):
        for android_version in android_versions:
            clone_android_version = False
            config_folder = Path(Constants.config_directory + Constants.dir_sep + str(android_version))
            if not FileOp.dir_exists(str(config_folder)):
                print(f"{config_folder} doesn't exist!")
                continue
            for config_files in config_folder.rglob("*"):
                if str(config_files).endswith(".config"):
                    clone_android_version = True
                    break
            if clone_android_version:
                repo_dir = Constants.pwd + Constants.dir_sep + str(android_version)
                if Operation.clone_apk_repo(android_version=str(android_version), fresh_clone=True) is not None:
                    print(f"{repo_dir} cloned successfully!")
                else:
                    print(f"{repo_dir} could not be cloned!")
                Config.TARGET_ANDROID_VERSION = android_version
                if FileOp.dir_exists(repo_dir):
                    config_repo = Git(Constants.config_directory)
                    for config_file in config_folder.rglob("*.config"):
                        if not OnDemand.build_from_config_file(config_file, android_version, config_repo):
                            print("Failed to build from config file: " + str(config_file))
                            continue
                        else:
                            print("Successfully built from config file: " + str(config_file))
                else:
                    print(f"{repo_dir} doesn't exist!")
            else:
                print(f"There is no config file in {config_folder}, cloning is not required!")
    else:
        print(Constants.config_directory + " doesn't exist!")

Constants.end_of_function(actual_start_time, "Total time taken by the program to build custom builds")
