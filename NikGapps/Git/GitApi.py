import NikGapps.Git.Config as Config
import json
import requests


class GitApi:
    @staticmethod
    def read_from_url(url, params=None, authenticate=False):
        if params is None:
            params = {"": ""}
        if authenticate:
            headers = {'Authorization': f'token {Config.git_token_admin}'}
        else:
            headers = {'Accept': 'application/vnd.github.v3+json'}
        return requests.get(url, data=json.dumps(params), headers=headers)

    @staticmethod
    def post_to_url(url, params=None, authenticate=False):
        if params is None:
            params = {"": ""}
        if authenticate:
            headers = {'Authorization': f'token {Config.git_token_admin}'}
        else:
            headers = {'Accept': 'application/vnd.github.v3+json'}
        return requests.get(url, data=json.dumps(params), headers=headers)

    @staticmethod
    def get_open_pull_requests(authenticate=False):
        query_url = f"https://api.github.com/repos/{Config.owner}/{Config.repo}/pulls"
        pull_requests = []
        data_json = GitApi.read_from_url(query_url, authenticate).json()
        for i in range(0, len(data_json)):
            pull_requests.append(data_json[i])
        return pull_requests

    @staticmethod
    def merge_pull_request(pull_number):
        query_url = f"https://api.github.com/repos/{Config.owner}/{Config.repo}/pulls/{pull_number}/merge"
        params = {
            "commit_title": f"Squash Merge pull request #{pull_number}",
            "commit_message": "Merging automatically",
            "merge_method": "squash"
        }
        execution_status = False
        try:
            r = GitApi.post_to_url(query_url, params, authenticate=True)
            print(json.dumps(r.json(), indent=4, sort_keys=True))
            if r.status_code.__eq__("200"):
                execution_status = True
        except Exception as e:
            print(str(e))
        return execution_status
