import requests
from conftest import BASE_URL, get_db

def test_complete_success(token, paid_order_id):
    complete_response = requests.post(
        f"{BASE_URL}/complete",
        headers={"Authorization": f"Bearer {token}"},
        params={"order_id": paid_order_id}
    )
    assert complete_response.status_code == 200
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT status FROM orders WHERE id = %s", 
        (paid_order_id,)
    )
    status = cur.fetchone()[0]
    assert status == "complete"
    cur.close()
    conn.close()

def test_complete_not_paid(token, order_id):
    complete_response = requests.post(
        f"{BASE_URL}/complete",
        headers={"Authorization": f"Bearer {token}"},
        params={"order_id": order_id}
    )
    assert complete_response.status_code == 400

def test_complete_already_completed(token, paid_order_id):
    complete_response = requests.post(
        f"{BASE_URL}/complete",
        headers={"Authorization": f"Bearer {token}"},
        params={"order_id": paid_order_id}
    )
    assert complete_response.status_code == 200
    complete_response2 = requests.post(
        f"{BASE_URL}/complete",
        headers={"Authorization": f"Bearer {token}"},
        params={"order_id": paid_order_id}
    )
    assert complete_response2.status_code == 400

def test_complete_without_token():
    refund_response = requests.post(
        f"{BASE_URL}/complete",
        headers={"Authorization": f"Bearer "},
        params={"order_id": 1}
    )
    assert refund_response.status_code == 401