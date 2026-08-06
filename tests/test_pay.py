import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def test_pay_success():
    response = requests.post(
        f"{BASE_URL}/login",
        params={"username": "test01", "password": "123456"}
    )
    assert response.status_code == 200
    token = response.json()["token"]
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
    product_id = create_response.json()["product_id"]
    order_response = requests.post(
        f"{BASE_URL}/orders",
        headers={"Authorization": f"Bearer {token}"},
        params={"product_id": product_id, "quantity": 2}
    )
    assert order_response.status_code == 200
    order_id = order_response.json()["order_id"]
    pay_response = requests.post(
        f"{BASE_URL}/pay",
        headers={"Authorization": f"Bearer {token}"},
        params={"order_id": order_id}
    )
    assert pay_response.status_code == 200

def test_pay_already_paid():
    response = requests.post(
        f"{BASE_URL}/login",
        params={"username": "test01", "password": "123456"}
    )
    assert response.status_code == 200
    token = response.json()["token"]
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
    product_id = create_response.json()["product_id"]
    order_response = requests.post(
        f"{BASE_URL}/orders",
        headers={"Authorization": f"Bearer {token}"},
        params={"product_id": product_id, "quantity": 2}
    )
    assert order_response.status_code == 200
    order_id = order_response.json()["order_id"]
    pay_response = requests.post(
        f"{BASE_URL}/pay",
        headers={"Authorization": f"Bearer {token}"},
        params={"order_id": order_id}
    )
    assert pay_response.status_code == 200
    pay_response_again = requests.post(
        f"{BASE_URL}/pay",
        headers={"Authorization": f"Bearer {token}"},
        params={"order_id": order_id}
    )
    assert pay_response_again.status_code == 400

def test_pay_order_not_found():
    response = requests.post(
        f"{BASE_URL}/login",
        params={"username": "test01", "password": "123456"}
    )   
    assert response.status_code == 200
    token = response.json()["token"]
    pay_response = requests.post(
        f"{BASE_URL}/pay",
        headers={"Authorization": f"Bearer {token}"},
        params={"order_id": 9999}
    )
    assert pay_response.status_code == 400

def test_pay_without_token():
    pay_response = requests.post(
        f"{BASE_URL}/pay",
        headers={"Authorization": f"Bearer "},
        params={"order_id": 1}
    )
    assert pay_response.status_code == 401