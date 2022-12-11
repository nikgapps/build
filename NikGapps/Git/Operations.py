from NikGapps.Git import GitApi, PullRequest, Validate
from NikGapps.Git.Workflow import Workflow
from NikGapps.Helper import C, Git
from dateutil import parser as dateutil_parser
from datetime import datetime, timedelta
import pytz
from math import floor
import NikGapps.Git.GitConfig as Config


class Operations:

    @staticmethod
    def setup_tracker_repo():
        repo_name = "git@github.com:nikgapps/tracker.git"
        repo_dir = C.pwd + C.dir_sep + "tracker"
        print()
        print("Repo Dir: " + repo_dir)

        tracker_repo = Git(repo_dir)
        result = tracker_repo.clone_repo(repo_name)
        return tracker_repo if result else None

    @staticmethod
    def find_open_pull_request():
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
        return requests

    @staticmethod
    def process_pull_requests():
        Workflow.validate()
        requests = Operations.find_open_pull_request()
        print("Total Open Pull Requests: " + str(len(requests)))
        merged_pr_list = []
        for request in requests:
            print("-------------------------------------------------------------------------------------")
            pr_number = request["number"]
            pr_user = request["user"]["login"]
            user_url = request["user"]["html_url"]
            pr = PullRequest(pr_number, data_json=request, pr_name=pr_user, pr_user_url=user_url, authenticate=True)
            pr_url = request["url"]
            print("Validating pull request " + str(pr_url) + " from " + pr_user)
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
                        updated_at = comments[comments_len - 1]["updated_at"]
                        try:
                            d = dateutil_parser.parse(updated_at)
                            print("Comment already made on: " + str(d))
                            print()
                            print(comment_body)
                            print()
                            datetime_utc = datetime.now(pytz.timezone('UTC'))
                            date_diff = datetime_utc - d
                            seconds = date_diff.seconds + (date_diff.days * 86400)
                            hours = floor(seconds / 3600)
                            sec = timedelta(seconds=seconds)
                            d = datetime(1, 1, 1) + sec
                            print("Last comment was %d:%d:%d:%d ago" % (d.day - 1, d.hour, d.minute, d.second))
                            if hours >= Config.hours_before_close_pr:
                                message = None
                                if not str(comment_body).__contains__(f"Closing as no action was performed in last"):
                                    message = f"Closing as no action was performed in last {Config.hours_before_close_pr} hours"
                                print("Closing the pull request")
                                if GitApi.close_pull_request(pull_number=pr_number, message=message):
                                    print("Successfully Closed!")
                                else:
                                    print("Failed to close the pull request")
                            else:
                                print("Moving on!")
                        except Exception as e:
                            print(f"Exception occurred while parsing updated_at {updated_at} : " + str(e))
                        continue
                GitApi.comment_on_pull_request(pr_number, failure_reason)
            else:
                print("Validation Successful!")
                print("Requesting a merge")
                if GitApi.merge_pull_request(pr, f"Squash Merge pull request #{pr.pull_number} from @{pr.pr_name}"):
                    print("Successfully merged!")
                    merged_pr_list.append(pr)
                else:
                    print("Failed to merge!")
            print()
        return merged_pr_list
