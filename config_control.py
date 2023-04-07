from pathlib import Path
import Config
from NikGapps.Config.ConfigDirectoy import ConfigDirectory
from NikGapps.Config.ConfigOperations import ConfigOperations

from NikGapps.Config.UserBuild.OnDemand import OnDemand
from NikGapps.Git.Operations import Operations
from NikGapps.Helper import Args
from Operation import Operation
from NikGapps.Helper.C import C
from NikGapps.Helper.FileOp import FileOp

actual_start_time = C.start_of_function()
Config.RELEASE_TYPE = "config"
pr_list = Operations.process_pull_requests()
config_dir = ConfigDirectory()
config_repo = config_dir.setup(override_dir=True)
if config_repo is None:
    print("Failed to setup config directory")
    exit(1)
if len(pr_list) > 0:
    ConfigOperations.update_configs_with_pr_details(pr_list=pr_list, config_repo=config_repo)
if Config.BUILD_CONFIG:
    Config.SIGN_ZIP = False
    args = Args()
    android_versions = args.get_android_versions()
    print("---------------------------------------")
    print("Android Versions to build: " + str(android_versions))
    print("---------------------------------------")
    if FileOp.dir_exists(C.config_directory):
        for android_version in android_versions:
            clone_android_version = False
            config_folder = Path(C.config_directory + C.dir_sep + str(android_version))
            if not FileOp.dir_exists(str(config_folder)):
                print(f"{config_folder} doesn't exist!")
                continue
            for config_files in config_folder.rglob("*"):
                if str(config_files).endswith(".config"):
                    clone_android_version = True
                    break
            if clone_android_version:
                repo_dir = C.pwd + C.dir_sep + str(android_version)
                if Operation.clone_apk_repo(android_version=str(android_version), fresh_clone=True) is not None:
                    print(f"{repo_dir} cloned successfully!")
                else:
                    print(f"{repo_dir} could not be cloned!")
                if FileOp.dir_exists(repo_dir):
                    OnDemand.build_all_configs(android_version)
                else:
                    print(f"{repo_dir} doesn't exist!")
            else:
                print(f"There is no config file in {config_folder}, cloning is not required!")
    else:
        print(C.config_directory + " doesn't exist!")

C.end_of_function(actual_start_time, "Total time taken by the program to build custom builds")
