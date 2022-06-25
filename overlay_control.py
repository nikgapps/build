import os.path
from pathlib import Path

import Config
from NikGapps.Helper import Constants, Git, FileOp, Cmd

repo_name = "git@github.com:nikhilmenghani/NikGapps-overlays.git"
repo_dir = Constants.pwd + Constants.dir_sep + "NikGapps-overlays"
branch = "master"
config_repo = Git(repo_dir)
if FileOp.dir_exists(repo_dir):
    FileOp.remove_dir(repo_dir)
config_repo.clone_repo(repo_name, branch=branch)

if FileOp.dir_exists(repo_dir):
    overlay_android_version = f"overlays_{Config.ANDROID_VERSIONS[str(Config.TARGET_ANDROID_VERSION)]['code']}"
    overlays_repo_name = f"git@github.com:nikhilmenghani/{overlay_android_version}.git"
    overlays_repo_dir = Constants.pwd + Constants.dir_sep + overlay_android_version
    if FileOp.dir_exists(overlays_repo_dir):
        FileOp.remove_dir(overlays_repo_dir)
    overlay_config_repo = Git(overlays_repo_dir)
    overlay_config_repo.clone_repo(overlays_repo_name, branch="main")
    for folder in Path(repo_dir).iterdir():
        if str(folder).endswith(".git"):
            continue
        cmd = Cmd()
        overlay_path = cmd.build_overlay(folder_name=str(folder))
        if not overlay_path.__eq__(""):
            print(f"{overlay_path} successfully built..")
            print(f"Copying to {os.path.join(overlays_repo_dir, str(Path(folder).name), f'{Path(folder).name}.apk')}")
            FileOp.copy_file(overlay_path, os.path.join(overlays_repo_dir,
                                                        str(Path(folder).name), f"{Path(folder).name}.apk"))
        else:
            print("Failed to build overlay")
    if overlay_config_repo.due_changes():
        print("Pushing due changes!")
        overlay_config_repo.git_push(commit_message="Updated Overlays!")
    else:
        print(f"{overlays_repo_dir} doesn't exist!")
else:
    print(f"{repo_dir} doesn't exist!")
