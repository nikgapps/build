import os.path
from pathlib import Path

import Config
from NikGapps.Helper import C, Git, FileOp, Cmd, Args

# parse command line arguments
args = Args()
if args.android_version != str(-1):
    Config.TARGET_ANDROID_VERSION = args.android_version
    C.update_android_version_dependencies()
android_version_code = Config.ANDROID_VERSIONS[str(Config.TARGET_ANDROID_VERSION)]['code']
repo_name = f"git@github.com:nikgapps/overlays_{android_version_code}_source.git"
repo_dir = C.pwd + C.dir_sep + f"overlays_{android_version_code}_source"
branch = "master"
config_repo = Git(repo_dir)
config_repo.clone_repo(repo_name, branch=branch)

if FileOp.dir_exists(repo_dir):
    overlay_android_version = f"overlays_{android_version_code}"
    overlays_repo_name = f"git@github.com:nikgapps/{overlay_android_version}.git"
    overlays_repo_dir = C.pwd + C.dir_sep + overlay_android_version
    overlay_config_repo = Git(overlays_repo_dir)
    overlay_config_repo.clone_repo(overlays_repo_name, branch="master")
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
            folder_to_remove = os.path.join(str(folder), "dist")
            FileOp.remove_dir(folder_to_remove)
            folder_to_remove = os.path.join(str(folder), "build")
            FileOp.remove_dir(folder_to_remove)
        else:
            print("Failed to build overlay")
    if overlay_config_repo.due_changes():
        print("Pushing due changes!")
        overlay_config_repo.git_push(commit_message="Updated Overlays!", push_untracked_files=True)
    else:
        print(f"{overlays_repo_dir} doesn't exist!")
else:
    print(f"{repo_dir} doesn't exist!")
