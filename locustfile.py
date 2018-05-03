from locust import HttpLocust, TaskSet, task

class UserTasks(TaskSet):

    def setup(self):
        print("performing setup")
        # Doesn't work yet
        for x in range(0, 50):
            subject = str(x) + " subject"
            body = str(x) + " body"
            message = {
              "msg_to": ["ef7737df-2097-4a73-a530-e98dba7bf28f"],
              "msg_from": "d45e99c-8edf-489a-9c72-6cabe6c387fc",
              "subject": subject,
              "body": body,
              "thread_id": "a1a5e99c-8edf-489a-9c72-6cabe6c387fc",
              "ru_id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
              "collection_case": "ACollectionCase",
              "survey": "2346e99c-8edf-489a-9c72-6cabe6c387fc"
            }
            self.client.post("/message/send", headers={'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXJ0eV9pZCI6ImE1YzZhODNkLTU4M2YtNGNjYi05ZTg0LTEzZGIxNGFhN2IzZiIsInJvbGUiOiJpbnRlcm5hbCJ9.SuEpUCZwY7b6gRMOF6FTOB09O82EXRrI-7nhRogNnaw', 'Content-Type': 'application/json',
                                           'Accept': 'application/json'}, data=message)

    # # but it might be convenient to use the @task decorator
    # @task
    # def get_threads(self):
    #     self.client.get("/threads", headers={'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXJ0eV9pZCI6ImE1YzZhODNkLTU4M2YtNGNjYi05ZTg0LTEzZGIxNGFhN2IzZiIsInJvbGUiOiJpbnRlcm5hbCJ9.SuEpUCZwY7b6gRMOF6FTOB09O82EXRrI-7nhRogNnaw'})

    # but it might be convenient to use the @task decorator
    @task
    def get_threads_with_limit(self):
        self.client.get("/threads?page=2&limit=15", headers={'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXJ0eV9pZCI6ImE1YzZhODNkLTU4M2YtNGNjYi05ZTg0LTEzZGIxNGFhN2IzZiIsInJvbGUiOiJpbnRlcm5hbCJ9.SuEpUCZwY7b6gRMOF6FTOB09O82EXRrI-7nhRogNnaw'})

class WebsiteUser(HttpLocust):
    """
    Locust user class that does requests to the locust web server running on localhost
    """
    host = "http://localhost:5050"
    min_wait = 1500
    max_wait = 2500
    task_set = UserTasks
