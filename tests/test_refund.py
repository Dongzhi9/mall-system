import requests
import time
import pymysql

BASE_URL = "http://127.0.0.1:8000"

def test_refund_success(token, paid_order_id):
    refund_response = requests.post(
        f"{BASE_URL}/refund",
        headers={"Authorization": f"Bearer {token}"},
        params={"order_id": paid_order_id}
    )
    assert refund_response.status_code == 200
    conn = pymysql.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="123456",
        database="mall",
        charset="utf8"
    )
    cur = conn.cursor()
    cur.execute(
        "SELECT product_id FROM orders WHERE id = %s", 
        (paid_order_id,)
    )
    product_id = cur.fetchone()[0]
    cur.execute(
        "SELECT stock FROM products WHERE id = %s", 
        (product_id,)
    )
    stock = cur.fetchone()[0]
    cur.execute(
        "SELECT status FROM orders WHERE id = %s", 
        (paid_order_id,)
    )
    status = cur.fetchone()[0]
    assert stock == 2
    assert status == "refunded"
    cur.close()
    conn.close()

def test_refund_cross_user(paid_order_id):
    response_b = requests.post(
        f"{BASE_URL}/login",
        params={"username": "test02", "password": "123456"}
    )
    token_b = response_b.json()["token"]
    assert response_b.status_code == 200
    refund_response = requests.post(
        f"{BASE_URL}/refund",
        headers={"Authorization": f"Bearer {token_b}"},
        params={"order_id": paid_order_id}   
    )
    assert refund_response.status_code == 400

def test_refund_already_refunded(token, paid_order_id):
    refund_response = requests.post(
        f"{BASE_URL}/refund",
        headers={"Authorization": f"Bearer {token}"},
        params={"order_id": paid_order_id}
    )
    assert refund_response.status_code == 200
    refund_response_2 = requests.post(
        f"{BASE_URL}/refund",
        headers={"Authorization": f"Bearer {token}"},
        params={"order_id": paid_order_id}
    )
    assert refund_response_2.status_code == 400

def test_refund_order_not_found(token):
    refund_response = requests.post(
        f"{BASE_URL}/refund",
        headers={"Authorization": f"Bearer {token}"},
        params={"order_id": 9999}
    )
    assert refund_response.status_code == 400

def test_refund_not_paid(token, order_id):
    refund_response = requests.post(
        f"{BASE_URL}/refund",
        headers={"Authorization": f"Bearer {token}"},
        params={"order_id": order_id}
    )
    assert refund_response.status_code == 400

def test_refund_without_token():
    refund_response = requests.post(
        f"{BASE_URL}/refund",
        headers={"Authorization": f"Bearer "},
        params={"order_id": 1}
    )
    assert refund_response.status_code == 401