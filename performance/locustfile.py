from locust import HttpUser, task, between

class MallUser(HttpUser):
    host = "http://127.0.0.1:8000"

    @task
    def get_products(self):
        self.client.get("/products")