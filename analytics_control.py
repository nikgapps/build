import json
import os
from pathlib import Path

import git
from git import Repo

import Config
from NikGapps.Helper import Constants, FileOp, Git, Logs

repo_name = "git@github.com:nikgapps/config.git"
repo_dir = Constants.pwd + Constants.dir_sep + "config"
branch = "main"
analytics_dict = {}
custom_build_dict = {}
print()
print("Repo Dir: " + repo_dir)
todays_custom_builds_count = 0
config_repo = Git(repo_dir)
config_repo.clone_repo(repo_name)

if FileOp.dir_exists(repo_dir):
    print(f"{repo_dir} exists!")
    archive_dir = repo_dir + Constants.dir_sep + "archive"
    directory_contents = os.listdir(archive_dir)
    print(directory_contents)
    todays_date = str(Logs.get_current_time())
    for directory in directory_contents:
        android_version_dir = archive_dir + Constants.dir_sep + str(directory)
        count = 0
        for pkg_files in Path(android_version_dir).rglob("*"):
            if Path(pkg_files).is_file():
                count += 1
        analytics_dict[directory] = count
        android_version_dir_today = android_version_dir + Constants.dir_sep + todays_date
        for pkg_files in Path(android_version_dir_today).rglob("*"):
            if Path(pkg_files).is_file():
                todays_custom_builds_count += 1
        custom_build_dict[todays_date] = todays_custom_builds_count
else:
    print(f"{repo_dir} doesn't exist!")

print("Download count from archive directory: " + str(analytics_dict))
print("Today's Download count so far: " + str(custom_build_dict))

repo_name = "git@github.com:nikgapps/tracker.git"
repo_dir = Constants.pwd + Constants.dir_sep + "tracker"
print()
print("Repo Dir: " + repo_dir)

tracker_repo = Git(repo_dir)
tracker_repo.clone_repo(repo_name)

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
            key_code = Config.ANDROID_VERSIONS[key]["code"]
            print(f"Update download count for {key}({key_code})")
            if decoded_hand.get(key_code) is not None:
                # get the download count of the key
                download_count_before = decoded_hand[key_code]
                decoded_hand[key_code] = str(analytics_dict[key])
                print(f"Download count for {key} updated from {download_count_before} to {str(analytics_dict[key])}")
            else:
                print(f"key doesn't exist.. so creating {str(analytics_dict[key])}")
                decoded_hand[key_code] = str(analytics_dict[key])
            print()

        print(decoded_hand)

        with open(custom_builds_count_json, "w") as file:
            json.dump(decoded_hand, file)
        try:
            print("Updating the download count in tracker repository")
            print("Custom builds so far created today: " + str(todays_custom_builds_count))
            tracker_repo = Git(repo_dir)
            tracker_repo.update_repo_changes("Custom builds so far created today: " + str(todays_custom_builds_count))
        except Exception as e:
            print(str(e))
else:
    print(f"{repo_dir} doesn't exist!")
