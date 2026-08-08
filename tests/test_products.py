import requests

BASE_URL = "http://127.0.0.1:8000"

def test_create_product_success(token):
    create_response = requests.post(
        f"{BASE_URL}/products",
        headers={"Authorization": f"Bearer {token}"},
        params={"name": "桌子", "price": 100, "stock": 5}
    )
    assert create_response.status_code == 200
    assert create_response.json()["message"] == "创建商品成功"

def test_create_product_without_token():
    response = requests.post(
        f"{BASE_URL}/products",
        params={"name": "鼠标", "price": 50, "stock": 10}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "未提供token"

def test_get_products_success():
    response = requests.get(
        f"{BASE_URL}/products"
    )
    assert response.status_code == 200
    assert response.json()["products"] is not None