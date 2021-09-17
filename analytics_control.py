import json
import os
from pathlib import Path

import git
from git import Repo

from NikGapps.Helper import Constants, FileOp, Git

repo_name = "git@github.com:nikgapps/config.git"
repo_dir = Constants.pwd + Constants.dir_sep + "config"
branch = "main"
analytics_dict = {}
print()
print("Repo Dir: " + repo_dir)
start_time = Constants.start_of_function()
try:
    if FileOp.dir_exists(repo_dir):
        print(f"{repo_dir} already exists, deleting for a fresh clone!")
        FileOp.remove_dir(repo_dir)
    print(f"git clone -b --depth=1 {branch} {repo_name}")
    repo = git.Repo.clone_from(repo_name, repo_dir, branch=branch, depth=1)
    assert repo.__class__ is Repo  # clone an existing repository
    assert Repo.init(repo_dir).__class__ is Repo
except Exception as e:
    print("Exception caught while cloning the repo: " + str(e))
    Constants.end_of_function(start_time, f"Time taken to clone -b {branch} {repo_name}")
if FileOp.dir_exists(repo_dir):
    print(f"{repo_dir} exists!")
    archive_dir = repo_dir + Constants.dir_sep + "archive"
    directory_contents = os.listdir(archive_dir)
    print(directory_contents)
    for directory in directory_contents:
        android_version_dir = archive_dir + Constants.dir_sep + str(directory)
        count = 0
        for pkg_files in Path(android_version_dir).rglob("*"):
            if Path(pkg_files).is_file():
                count += 1
        analytics_dict[directory] = count
else:
    print(f"{repo_dir} doesn't exist!")

print("Download count from archive directory: " + str(analytics_dict))

repo_name = "git@github.com:nikgapps/tracker.git"
repo_dir = Constants.pwd + Constants.dir_sep + "tracker"
print()
print("Repo Dir: " + repo_dir)
start_time = Constants.start_of_function()
try:
    if FileOp.dir_exists(repo_dir):
        print(f"{repo_dir} already exists, deleting for a fresh clone!")
        FileOp.remove_dir(repo_dir)
    print(f"git clone -b --depth=1 {branch} {repo_name}")
    repo = git.Repo.clone_from(repo_name, repo_dir, branch=branch, depth=1)
    assert repo.__class__ is Repo  # clone an existing repository
    assert Repo.init(repo_dir).__class__ is Repo
except Exception as e:
    print("Exception caught while cloning the repo: " + str(e))
    Constants.end_of_function(start_time, f"Time taken to clone -b {branch} {repo_name}")
if FileOp.dir_exists(repo_dir):
    print(f"{repo_dir} exists!")
    custom_builds_count_json = repo_dir + Constants.dir_sep + "count.json"
    if FileOp.file_exists(custom_builds_count_json):
        print("File Exists!")
        custom_builds_json_string = ""
        for line in FileOp.read_string_file(custom_builds_count_json):
            custom_builds_json_string += line
        print(custom_builds_json_string)
        print()
        decoded_hand = json.loads(custom_builds_json_string)

        for key in analytics_dict:
            print(f"Update download count for {key}")
            if decoded_hand.get(key) is not None:
                # get the download count of the key
                download_count_before = decoded_hand[key]
                decoded_hand[key] = str(analytics_dict[key])
                print(f"Download count for {key} updated from {download_count_before} to {str(analytics_dict[key])}")
            else:
                print(f"key doesn't exist.. so creating {str(analytics_dict[key])}")
                decoded_hand[key] = str(analytics_dict[key])
            print()

        print(decoded_hand)

        with open(custom_builds_count_json, "w") as file:
            json.dump(decoded_hand, file)
        try:
            print("Updating the download count in tracker repository")
            tracker_repo = Git(repo_dir)
            tracker_repo.update_repo_changes("Update custom builds download count")
        except Exception as e:
            print(str(e))
else:
    print(f"{repo_dir} doesn't exist!")




