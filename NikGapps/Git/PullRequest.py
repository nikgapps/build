import NikGapps.Git.GitConfig as Config
from NikGapps.Git.GitApi import GitApi


class PullRequest:

    def __init__(self, number, pr_name, pr_user_url, data_json=None, authenticate=False):
        self.pull_number = number
        self.pr_name = pr_name
        self.pr_name_url = pr_user_url
        if data_json is None:
            query_url = f"https://api.github.com/repos/{Config.owner}/{Config.repo}/pulls/{self.pull_number}"
            self.request = GitApi.read_from_url(query_url, authenticate=authenticate).json()
        else:
            self.request = data_json
        self.files_changed = self.get_files_changed(authenticate=authenticate)
        self.file_names = self.get_file_names_list()

    def get_files_changed(self, authenticate=False):
        query_url = f"https://api.github.com/repos/{Config.owner}/{Config.repo}/pulls/{self.pull_number}/files"
        files_changed = []
        data_json = GitApi.read_from_url(query_url, authenticate=authenticate).json()
        for i in range(0, len(data_json)):
            files_changed.append(data_json[i])
        return files_changed

    def get_file_names_list(self):
        file_names = []
        for file in self.files_changed:
            file_names.append(file["filename"])
        return file_names
