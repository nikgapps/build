from NikGapps.Git.Validate import Validate
from NikGapps.Git.GitApi import GitApi
from NikGapps.Git.PullRequest import PullRequest

print("Finding the open pull requests")
try:
    requests = GitApi.get_open_pull_requests()
except Exception as e:
    print(str(e))
    try:
        requests = GitApi.get_open_pull_requests(authenticate=True)
    except Exception as e:
        print(str(e))
        requests = []

for request in requests:
    pr_number = request["number"]
    pr = PullRequest(pr_number, request)
    pr_url = request["url"]
    print("Validating pull request " + str(pr_url))
    failure_reason = Validate.pull_request(pr)
    print()
    if len(failure_reason) > 0:
        print("Validation Failed with reason(s): " + str(failure_reason))
    else:
        print("Validation Successful!")
        print("Requesting a merge")
        GitApi.merge_pull_request(pr_number)
    print()

print("end of program")
