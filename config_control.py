import sys
from pathlib import Path
import Config
import git
from git import Repo

from NikGapps.Git.GitApi import GitApi
from Release import Release
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
    arg_len = len(sys.argv)
    android_versions = [Config.TARGET_ANDROID_VERSION]
    if arg_len > 1:
        android_versions = sys.argv[1].split(',')
    print("---------------------------------------")
    print("Android Versions to build: " + str(android_versions))
    print("---------------------------------------")
    if FileOp.dir_exists(Constants.config_directory):
        branch = "master"
        if Config.RELEASE_TYPE.__eq__("canary"):
            branch = "canary"
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
                print("Repo Dir: " + repo_dir)
                start_time = Constants.start_of_function()
                try:
                    if FileOp.dir_exists(repo_dir):
                        print(f"{repo_dir} already exists, deleting for a fresh clone!")
                        FileOp.remove_dir(repo_dir)
                    print(f"git clone -b --depth=1 {branch} https://gitlab.com/nikgapps/{android_version}.git")
                    repo = git.Repo.clone_from(f"https://gitlab.com/nikgapps/{android_version}.git",
                                               repo_dir,
                                               branch=branch, depth=1)
                    assert repo.__class__ is Repo  # clone an existing repository
                    assert Repo.init(repo_dir).__class__ is Repo
                except Exception as e:
                    print("Exception caught while cloning the repo: " + str(e))
                    continue
                Constants.end_of_function(start_time,
                                          f"Time taken to clone -b {branch} gitlab.com/nikgapps/{android_version}.git")
                Config.TARGET_ANDROID_VERSION = int(android_version)
                if FileOp.dir_exists(repo_dir):
                    Constants.update_sourceforge_release_directory("config")
                    zip_status = Release.zip(['config'])
                else:
                    print(f"{repo_dir} doesn't exist!")
            else:
                print(f"There is no config file in {config_folder}, cloning is not required!")
    else:
        print(Constants.config_directory + " doesn't exist!")

Constants.end_of_function(actual_start_time, "Total time taken by the program to build custom builds")
