from locust import HttpUser, task

class LoginUser(HttpUser):
    host = "http://127.0.0.1:8000"

    @task
    def login(self):
        self.client.post("/login", params={"username": "test01", "password": "123456"})
