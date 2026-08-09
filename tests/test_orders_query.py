import requests
from conftest import BASE_URL

def test_get_orders_success(token, order_id):
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

def test_get_orders_isolation(order_id):
    response_b = requests.post(
            f"{BASE_URL}/login",
            params={"username": "test02", "password": "123456"}
        )
    assert response_b.status_code == 200
    token_b = response_b.json()["token"]
    get_order_response = requests.get(
        f"{BASE_URL}/orders",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert get_order_response.status_code == 200
    a_ids = []
    for o in get_order_response.json()["orders"]:
        a_ids.append(o["id"])
    assert order_id not in a_ids