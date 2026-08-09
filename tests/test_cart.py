import requests
from conftest import BASE_URL, get_db

def test_add_to_cart_success(token):
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

def test_add_to_cart_merge_quantity(token, product_id):
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
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT quantity FROM cart WHERE product_id=%s",
        (product_id,)
    )
    record = cur.fetchone()
    assert record[0] == 5
    cur.close()
    conn.close()    