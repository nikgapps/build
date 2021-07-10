import NikGapps.Git.GitConfig as Config
from NikGapps.Git.GitApi import GitApi


class PullRequest:

    def __init__(self, number, data_json=None):
        self.pull_number = number
        if data_json is None:
            query_url = f"https://api.github.com/repos/{Config.owner}/{Config.repo}/pulls/{self.pull_number}"
            self.request = GitApi.read_from_url(query_url).json()
        else:
            self.request = data_json

    def get_files_changed(self):
        query_url = f"https://api.github.com/repos/{Config.owner}/{Config.repo}/pulls/{self.pull_number}/files"
        files_changed = []
        data_json = GitApi.read_from_url(query_url).json()
        for i in range(0, len(data_json)):
            files_changed.append(data_json[i])
        return files_changed
