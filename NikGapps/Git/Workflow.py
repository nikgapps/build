from NikGapps.Git import GitApi


class Workflow:

    @staticmethod
    def get_open_workflows():
        print("Checking if there is any existing workflow in progress")
        try:
            workflows = GitApi.get_running_workflows(authenticate=False)
        except Exception as e:
            print(str(e))
            try:
                workflows = GitApi.get_running_workflows(authenticate=True)
            except Exception as e:
                print(str(e))
                workflows = []
        return workflows
