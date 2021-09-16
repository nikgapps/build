import git.exc
from git import Repo, Commit
from shutil import copyfile
from NikGapps.Helper.Assets import Assets
from NikGapps.Helper.Constants import Constants
import os
import time
import datetime
from datetime import datetime
import pytz


class Git:

    def __init__(self, working_tree_dir):
        self.working_tree_dir = working_tree_dir
        self.repo = Repo(working_tree_dir)

    # this will return commits 21-30 from the commit list as traversed backwards master
    # ten_commits_past_twenty = list(repo.iter_commits('master', max_count=10, skip=20))
    # assert len(ten_commits_past_twenty) == 10
    # assert fifty_first_commits[20:30] == ten_commits_past_twenty
    # repo = git.Repo.clone_from(repo_url, working_tree_dir, branch='master')
    def get_latest_commit_date(self, repo=None, filter_key=None):
        tz_london = pytz.timezone('Europe/London')
        try:
            if repo is not None:
                commits = list(self.repo.iter_commits(repo, max_count=50))
            else:
                commits = list(self.repo.iter_commits('master', max_count=50))
        except git.exc.GitCommandError:
            commits = list(self.repo.iter_commits('master', max_count=50))

        for commit in commits:
            commit: Commit
            # if filter_key = 10, it will look for commits that starts with 10
            # failing will continue looking for latest available commit that starts with 10
            if filter_key is not None and not str(commit.message).startswith(filter_key):
                continue
            time_in_string = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(commit.committed_date)))
            time_in_object = datetime.strptime(time_in_string, '%Y-%m-%d %H:%M:%S')
            london_time_in_object = time_in_object.astimezone(tz_london)
            london_time_in_string = london_time_in_object.strftime('%Y-%m-%d %H:%M:%S')
            commit_datetime = datetime.strptime(london_time_in_string, '%Y-%m-%d %H:%M:%S')
            return commit_datetime
        return None

    def due_changes(self):
        files = self.repo.git.diff(None, name_only=True)
        if files != "":
            for f in files.split('\n'):
                return True
        return False

    def git_push(self, commit_message, push_untracked_files=None):
        self.repo.git.add(update=True)
        if push_untracked_files is not None:
            for file in self.repo.untracked_files:
                self.repo.index.add([file])
        self.repo.index.commit(commit_message)
        origin = self.repo.remote(name='origin')
        origin.push()
        print("Pushed to origin: " + str(commit_message))

    def update_changelog(self):
        source_file = Assets.changelog
        dest_file = Constants.website_directory + os.path.sep + "_data" + os.path.sep + "changelogs.yaml"
        i = copyfile(source_file, dest_file)
        if self.due_changes():
            print("Updating the changelog to the website")
            self.git_push("Update Changelog")
        else:
            print("There is no changelog to update!")

    def update_config_changes(self, message):
        if self.due_changes():
            print(message)
            self.git_push(message, push_untracked_files=True)
        else:
            print("There is nothing to update!")

    def update_repo_changes(self, message):
        if self.due_changes():
            print(message)
            self.git_push(message, push_untracked_files=True)
        else:
            print("There is nothing to update!")

    def get_status(self, path):
        changed = [item.a_path for item in self.repo.index.diff(None)]
        if path in self.repo.untracked_files:
            return 'untracked'
        elif path in changed:
            return 'modified'
        else:
            return 'don''t care'
