import requests
import time
import pymysql

BASE_URL = "http://127.0.0.1:8000"

def test_get_orders_success():
    response = requests.post(
        f"{BASE_URL}/login",
        params={"username": "test01", "password": "123456"}
    )
    assert response.status_code == 200
    token = response.json()["token"]
    create_response = requests.post(
        f"{BASE_URL}/products",
        headers={"Authorization": f"Bearer {token}"},
        params={"name": f"电脑_{int(time.time()*100)}", "price": 5000, "stock": 5}
    )
    assert create_response.status_code == 200
    product_id = create_response.json()["product_id"]
    order_response = requests.post(
        f"{BASE_URL}/orders",
        headers={"Authorization": f"Bearer {token}"},
        params={"product_id": product_id, "quantity": 1}
    )
    assert order_response.status_code == 200
    order_id = order_response.json()["order_id"]
    get_order_response = requests.get(
        f"{BASE_URL}/orders",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_order_response.status_code == 200
    a_ids = []
    for o in get_order_response.json()["orders"]:
        a_ids.append(o["id"])
    assert order_id in a_ids

def test_get_orders_without_token():
    response = requests.get(
        f"{BASE_URL}/orders",
        headers={"Authorization": f"Bearer "}
    )
    assert response.status_code == 401

def test_get_orders_isolation():
    response = requests.post(
        f"{BASE_URL}/login",
        params={"username": "test01", "password": "123456"}
    )
    assert response.status_code == 200
    token = response.json()["token"]
    create_response = requests.post(
        f"{BASE_URL}/products",
        headers={"Authorization": f"Bearer {token}"},
        params={"name": f"电脑_{int(time.time()*100)}", "price": 5000, "stock": 5}
    )
    assert create_response.status_code == 200
    product_id = create_response.json()["product_id"]
    order_response = requests.post(
        f"{BASE_URL}/orders",
        headers={"Authorization": f"Bearer {token}"},
        params={"product_id": product_id, "quantity": 1}
    )
    assert order_response.status_code == 200
    order_id = order_response.json()["order_id"]
    response_B = requests.post(
            f"{BASE_URL}/login",
            params={"username": "test02", "password": "123456"}
        )
    assert response_B.status_code == 200
    token = response_B.json()["token"]
    get_order_response = requests.get(
        f"{BASE_URL}/orders",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_order_response.status_code == 200
    a_ids = []
    for o in get_order_response.json()["orders"]:
        a_ids.append(o["id"])
    assert order_id not in a_ids