import requests
import time
import pymysql

BASE_URL = "http://127.0.0.1:8000"

def test_create_order_success():
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
        "SELECT stock FROM products WHERE id = %s", 
        (product_id,)
    )
    stock = cur.fetchone()[0]
    assert stock == 4
    cur.close()
    conn.close()

def test_create_order_not_enough_stock():
    response = requests.post(
        f"{BASE_URL}/login",
        params={"username": "test01", "password": "123456"}
    )
    assert response.status_code == 200
    token = response.json()["token"]
    create_response = requests.post(
        f"{BASE_URL}/products",
        headers={"Authorization": f"Bearer {token}"},
        params={"name": f"手机_{int(time.time()*100)}", "price": 3000, "stock": 1}
    )
    assert create_response.status_code == 200
    product_id = create_response.json()["product_id"]
    order_response = requests.post(
        f"{BASE_URL}/orders",
        headers={"Authorization": f"Bearer {token}"},
        params={"product_id": product_id, "quantity": 99}
    )
    assert order_response.status_code == 400
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
        "SELECT stock FROM products WHERE id = %s", 
        (product_id,)
    )
    stock = cur.fetchone()[0]
    assert stock == 1
    cur.close()
    conn.close()

def test_create_order_without_token():
    order_response = requests.post(
        f"{BASE_URL}/orders",
        params={"product_id": 1, "quantity": 1}
    )
    assert order_response.status_code == 401

def test_create_order_product_not_found ():
    response = requests.post(
        f"{BASE_URL}/login",
        params={"username": "test01", "password": "123456"}
    )
    assert response.status_code == 200
    token = response.json()["token"]
    order_response = requests.post(
        f"{BASE_URL}/orders",
        headers={"Authorization": f"Bearer {token}"},
        params={"product_id": 9999, "quantity": 1}
    )
    assert order_response.status_code == 400


