import requests
import time
import pymysql

BASE_URL = "http://127.0.0.1:8000"

def test_add_to_cart_success():
    response = requests.post(
        f"{BASE_URL}/login",
        params={"username": "test01", "password": "123456"}
    )
    assert response.status_code == 200
    token = response.json()["token"]
    add_response = requests.post(
        f"{BASE_URL}/cart",
        headers={"Authorization": f"Bearer {token}"},
        params={"product_id": 1, "quantity": 2}
    )
    assert add_response.status_code == 200

def test_add_to_cart_without_token():
    add_response = requests.post(
        f"{BASE_URL}/cart",
        params={"product_id": 1, "quantity": 2}
    )
    assert add_response.status_code == 401
    assert add_response.json()["detail"] == "未提供token"

def test_add_to_cart_merge_quantity():
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
            "stock": 10
        }
    )
    assert create_response.status_code == 200
    product_id = create_response.json()["product_id"]
    add_response1 = requests.post(
        f"{BASE_URL}/cart",
        headers={"Authorization": f"Bearer {token}"},
        params={"product_id": product_id, "quantity": 2}
    )
    assert add_response1.status_code == 200 
    add_response2 = requests.post(
        f"{BASE_URL}/cart", 
        headers={"Authorization": f"Bearer {token}"},
        params={"product_id": product_id, "quantity": 3}
    )
    assert add_response2.status_code == 200
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
        "SELECT quantity FROM cart WHERE product_id=%s",
        (product_id)
    )
    record = cur.fetchone()
    assert record[0] == 5
    cur.close()
    conn.close()    