import os.path
from pathlib import Path
import git
from git import Repo

from NikGapps.Helper import Git
from NikGapps.Helper.Constants import Constants
from NikGapps.Helper.FileOp import FileOp

actual_start_time = Constants.start_of_function()
repo_name = "git@github.com:nikgapps/config.git"
repo_dir = Constants.pwd + Constants.dir_sep + "config"
branch = "main"
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
    count = 0
    for path in Path(archive_dir).rglob("*"):
        if Path(path).is_file():
            filename = str(Path(path).name)
            parent = str(Path(path).parent)
            if filename.__contains__("_"):
                date_of_file = filename[filename.rindex("_") + 1:filename.rindex(".config")]
                if not parent.endswith(date_of_file):
                    source = str(Path(path))
                    destination = f"{parent + os.path.sep + date_of_file + os.path.sep + filename}"
                    FileOp.move_file(source, destination)
    # commit the changes
    commit_message = f"Organized the archive folder structure"
    config_repo = Git(repo_dir)
    config_repo.update_config_changes(commit_message)
else:
    print(Constants.config_directory + " doesn't exist!")

Constants.end_of_function(actual_start_time, "Total time taken by the program")
