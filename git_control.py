from NikGapps.Git.Validate import Validate
from NikGapps.Git.GitApi import GitApi
from NikGapps.Git.PullRequest import PullRequest

print("Finding the open pull requests")
try:
    requests = GitApi.get_open_pull_requests(authenticate=True)
except Exception as e:
    print(str(e))
    try:
        requests = GitApi.get_open_pull_requests(authenticate=True)
    except Exception as e:
        print(str(e))
        requests = []

print("Total Open Pull Requests: " + str(len(requests)))

for request in requests:
    print("-------------------------------------------------------------------------------------")
    pr_number = request["number"]
    pr = PullRequest(pr_number, request, authenticate=True)
    pr_url = request["url"]
    print("Validating pull request " + str(pr_url))
    failure_reason = Validate.pull_request(pr)
    print()
    if len(failure_reason) > 0:
        print("Checking if comments already made")
        comments = GitApi.get_comments_from_pull_request(pr_number, authenticate=True)
        comments_len = len(comments)
        print("Total comments already made: " + str(comments_len))
        if comments_len > 0:
            last_commenter = comments[comments_len - 1]["user"]["login"]
            comment_body = comments[comments_len - 1]["body"]
            if str(last_commenter).__eq__("nikgapps") or str(last_commenter).__eq__("nikhilmenghani"):
                print("Comment already made")
                print(comment_body)
                print("Moving on!")
                continue
        GitApi.comment_on_pull_request(pr_number, failure_reason)
    else:
        print("Validation Successful!")
        print("Requesting a merge")
        if GitApi.merge_pull_request(pr_number):
            print("Successfully merged!")
        else:
            print("Failed to merge!")
    print()

print("end of program")
