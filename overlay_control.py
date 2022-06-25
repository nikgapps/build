from pathlib import Path

from NikGapps.Helper import Constants, Git, FileOp, Cmd

repo_name = "git@github.com:nikhilmenghani/NikGapps-overlays.git"
repo_dir = Constants.pwd + Constants.dir_sep + "NikGapps-overlays"
branch = "master"
config_repo = Git(repo_dir)
if not FileOp.dir_exists(repo_dir):
    config_repo.clone_repo(repo_name, branch=branch)

if FileOp.dir_exists(repo_dir):
    print(f"{repo_dir} exists!")
    for folder in Path(repo_dir).iterdir():
        if str(folder).endswith(".git"):
            continue
        cmd = Cmd()
        overlay_path = cmd.build_overlay(folder_name=str(folder))
        if not overlay_path.__eq__(""):
            print(f"{overlay_path} successfully built..")
        else:
            print("Failed to build overlay")
else:
    print(f"{repo_dir} doesn't exist!")
