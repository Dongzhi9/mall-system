import requests
import time
import pymysql
import threading          

BASE_URL = "http://127.0.0.1:8000"

def test_oversell():
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
            "stock": 1
        }
    )
    assert create_response.status_code == 200
    product_id = create_response.json()["product_id"]

    results = []
    def worker():
        resp = requests.post(
            f"{BASE_URL}/orders",
            headers={"Authorization": f"Bearer {token}"},
            params={"product_id": product_id, "quantity": 1}
        )
        results.append(resp.status_code)

    threads = []
    for i in range(10):
        threads.append(threading.Thread(target=worker))
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    success = 0
    for code in results:
        if code == 200:
            success = success + 1
    assert success == 1
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
    cur.execute(
        "SELECT COUNT(*) FROM orders WHERE product_id = %s",
        (product_id,)
    )
    count = cur.fetchone()[0]
    assert count == 1
    assert stock == 0
    cur.close()
    conn.close() 