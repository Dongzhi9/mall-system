import requests

BASE_URL = "http://127.0.0.1:8000"

def test_user_info_without_token():
    response = requests.post(f"{BASE_URL}/user/info")
    assert response.status_code == 400
    assert response.json()["detail"] == "未提供token"

def test_user_info_invalid_token():
    response = requests.post(
        f"{BASE_URL}/user/info", 
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "token无效"

def test_user_info_success():
    login_response = requests.post(
        f"{BASE_URL}/login", 
        params={"username": "test01", "password": "123456"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["token"]

    response = requests.post(
        f"{BASE_URL}/user/info", 
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "test01"