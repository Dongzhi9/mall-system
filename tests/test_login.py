import time
import requests

BASE_URL = "http://127.0.0.1:8000"

def test_login_success():
    username = f"test{int(time.time()*100)}"
    requests.post(
        f"{BASE_URL}/register",
        params={"username":username,
                "password":"123"})
    response = requests.post(
        f"{BASE_URL}/login",
        params={"username":username,
                "password":"123"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "登录成功"

def test_login_wrong_password():
    response = requests.post(
        f"{BASE_URL}/login",
        params={"username":"test01",
                "password":"wrong_password"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "密码错误"

def test_login_user_not_found():
    response = requests.post(
        f"{BASE_URL}/login",
        params={"username":"nonexistent_user",
                "password":"123"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "用户名不存在"