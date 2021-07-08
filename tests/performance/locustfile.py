from locust import HttpLocust, TaskSet, task


class UserTasks(TaskSet):
    @task
    def get_threads_with_limit_with_survey(self):
        self.client.get(
            "/threads?survey=02b9c366-7397-42f7-942a-76dc5876d86d&page=1&limit=10",
            headers={"Authorization": "<insert jwt here>"},
        )

    @task
    def get_threads_with_limit_with_survey_page_2(self):
        self.client.get(
            "/threads?survey=02b9c366-7397-42f7-942a-76dc5876d86d&page=2&limit=10",
            headers={"Authorization": "<insert jwt here>"},
        )

    @task
    def get_threads_with_limit_with_50_results(self):
        self.client.get(
            "/threads?survey=02b9c366-7397-42f7-942a-76dc5876d86d&page=1&limit=50",
            headers={"Authorization": "<insert jwt here>"},
        )


class WebsiteUser(HttpLocust):
    """
    Locust user class that does requests to the locust web server running on localhost
    """

    host = "http://localhost:5050"
    min_wait = 5
    max_wait = 10
    task_set = UserTasks
