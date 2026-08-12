from locust import HttpUser, task

class OrderUser(HttpUser):
    host = "http://127.0.0.1:8000"

    def on_start(self):
        resp = self.client.post("/login", params={"username": "test01", "password": "123456"})
        self.token = resp.json()["token"]

    @task
    def create_order(self):
        self.client.post(
            "/orders",
            headers={"Authorization": f"Bearer {self.token}"},
            params={"product_id": 256, "quantity": 1},
        )