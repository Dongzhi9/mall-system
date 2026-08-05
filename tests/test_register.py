import requests

BASE_URL = "http://127.0.0.1:8000"

def test_register_success():
    """注册新用户，应该成功"""
    resp = requests.post(f"{BASE_URL}/register", params={"username": "pytest_02", "password": "123"})
    assert resp.status_code == 200
    assert resp.json()["message"] == "注册成功"

def test_register_duplicate():
    """重复注册同一用户名，应该被拦截返回400"""
    resp = requests.post(f"{BASE_URL}/register", params={"username": "pytest_01", "password": "123"})
    assert resp.status_code == 400

def test_register_empty_username():
    """用户名空，应该返回422（参数校验失败）"""
    resp = requests.post(f"{BASE_URL}/register", params={"username": "", "password": "123"})
    assert resp.status_code == 400
