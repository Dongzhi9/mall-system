import pytest
import requests
import time

BASE_URL = "http://127.0.0.1:8000"

@pytest.fixture
def token():
    response = requests.post(
        f"{BASE_URL}/login",
        params={"username": "test01", "password": "123456"}
    )
    assert response.status_code == 200
    return response.json()["token"]

@pytest.fixture
def product_id(token):
    create_response = requests.post(
        f"{BASE_URL}/products",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "name": f"test_{int(time.time()*100)}", 
            "price": 50, 
            "stock": 2
        }
    )
    assert create_response.status_code == 200
    return create_response.json()["product_id"]

@pytest.fixture
def order_id(token, product_id):
    order_response = requests.post(
        f"{BASE_URL}/orders",
        headers={"Authorization": f"Bearer {token}"},
        params={"product_id": product_id, "quantity": 2}
    )
    assert order_response.status_code == 200
    return order_response.json()["order_id"]

@pytest.fixture
def paid_order_id(token, order_id):
    pay_response = requests.post(
        f"{BASE_URL}/pay",
        headers={"Authorization": f"Bearer {token}"},
        params={"order_id": order_id}
    )
    assert pay_response.status_code == 200
    return order_id