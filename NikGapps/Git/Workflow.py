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

    @staticmethod
    def validate():
        workflows = Workflow.get_open_workflows()
        workflow_count = len(workflows)
        print("Total Open Workflows: " + str(workflow_count))
        if workflow_count > 1:
            print("Total Open Workflows: " + str(workflow_count) + f", most recent being {workflows[0]['run_number']}")

        if workflow_count > 1:
            print(f"Open workflows detected, Let's wait for open workflows to finish")
            for workflow in workflows:
                print(workflow["run_number"])
            exit(0)
        return True
