import requests
from conftest import BASE_URL

def test_pay_success(token, order_id):
    pay_response = requests.post(
        f"{BASE_URL}/pay",
        headers={"Authorization": f"Bearer {token}"},
        params={"order_id": order_id}
    )
    assert pay_response.status_code == 200

def test_pay_already_paid(token, order_id):
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

def test_pay_order_not_found(token):
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