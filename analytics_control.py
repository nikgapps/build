import json
import os
from pathlib import Path

import Config
from NikGapps.Helper import C, FileOp, Git, Logs

repo_name = "git@github.com:nikgapps/config.git"
repo_dir = C.pwd + C.dir_sep + "config"
branch = "main"
analytics_dict = {}
count_by_days = {}
count_today = {}
print()
print("Repo Dir: " + repo_dir)
todays_custom_builds_count = 0
config_repo = Git(repo_dir)
config_repo.clone_repo(repo_name)

if FileOp.dir_exists(repo_dir):
    print(f"{repo_dir} exists!")
    archive_dir = repo_dir + C.dir_sep + "archive"
    directory_contents = os.listdir(archive_dir)
    print(directory_contents)
    todays_date = str(Logs.get_current_time())
    for directory in directory_contents:
        custom_build_dict = {}
        android_version_dir = archive_dir + C.dir_sep + str(directory)
        count = 0
        for pkg_files in Path(android_version_dir).rglob("*"):
            if Path(pkg_files).is_file():
                count += 1
            if Path(pkg_files).is_dir():
                dir_name = Path(pkg_files).name
                date_count = 0
                for files in Path(pkg_files).rglob("*"):
                    if Path(files).is_file():
                        date_count += 1
                custom_build_dict[dir_name] = date_count
        analytics_dict[directory] = count
        if directory in Config.ANDROID_VERSIONS:
            key_code = Config.ANDROID_VERSIONS[directory]["code"]
            count_by_days[key_code] = custom_build_dict
            count_today[key_code] = custom_build_dict[todays_date] if todays_date in custom_build_dict else 0
else:
    print(f"{repo_dir} doesn't exist!")

print("Download count from archive directory: " + str(analytics_dict))
# print("Today's Download count so far: " + str(custom_build_dict))

repo_name = "git@github.com:nikgapps/tracker.git"
repo_dir = C.pwd + C.dir_sep + "tracker"
print()
print("Repo Dir: " + repo_dir)

tracker_repo = Git(repo_dir)
tracker_repo.clone_repo(repo_name)

if FileOp.dir_exists(repo_dir):
    print(f"{repo_dir} exists!")
    custom_builds_count_json = repo_dir + C.dir_sep + "count.json"
    decoded_hand = {}
    if FileOp.file_exists(custom_builds_count_json):
        print("File Exists!")
        custom_builds_json_string = ""
        for line in FileOp.read_string_file(custom_builds_count_json):
            custom_builds_json_string += line
        print(custom_builds_json_string)
        print()
        decoded_hand = json.loads(custom_builds_json_string)
        total_count = 0
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
            total_count += int(decoded_hand[key_code])
            print()
        decoded_hand['total'] = str(total_count)
        print(decoded_hand)
    with open(custom_builds_count_json, "w") as file:
        json.dump(decoded_hand, file, indent=2, sort_keys=True)
    custom_builds_by_date_json = repo_dir + C.dir_sep + "count_by_date.json"
    with open(custom_builds_by_date_json, "w") as file:
        json.dump(count_by_days, file, indent=2, sort_keys=True)
    custom_builds_today_json = repo_dir + C.dir_sep + "count_today.json"
    with open(custom_builds_today_json, "w") as file:
        json.dump(count_today, file, indent=2, sort_keys=True)
    try:
        print("Updating the download count in tracker repository")
        message = ""
        for key in count_today:
            todays_custom_builds_count += count_today[key]
            message += f"{key}:{count_today[key]} "
        print("Custom builds so far created today: " + str(todays_custom_builds_count))
        tracker_repo = Git(repo_dir)
        tracker_repo.update_repo_changes(message)
    except Exception as e:
        print(str(e))
else:
    print(f"{repo_dir} doesn't exist!")
