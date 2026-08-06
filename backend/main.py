import pymysql
import secrets
from fastapi import FastAPI, HTTPException, Header
from datetime import datetime, timedelta

app = FastAPI()

@app.get("/hello")
def hello():
    return {"message": "你好，商城后端!"}

@app.get("/user/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id, "name": f"用户{user_id}"}

def get_db():
    return pymysql.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="123456",
        database="mall",
        charset="utf8"
    )

def get_current_user(authorization: str):
    if not authorization:
        raise HTTPException(401, "未提供token")
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "格式错误")
    token = authorization.replace("Bearer ", "")
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT user_id, expires_at FROM tokens WHERE token=%s",
            (token,)
        )
        record = cur.fetchone()
        if not record:
            raise HTTPException(401, "token无效")
        if record[1] < datetime.now():
            raise HTTPException(401, "token已过期")
        return record[0]
    finally:
        cur.close()
        conn.close()

@app.post("/register")
def register(username: str, password: str):
    if not username:
        raise HTTPException(status_code=400, detail="用户名不能为空")
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)", 
            (username, password)
        )
        conn.commit()
        return {"message": "注册成功","user_name": username}
    except pymysql.err.IntegrityError:
        raise HTTPException(status_code=400, detail="用户名已存在")
    finally:
        cur.close()
        conn.close()

@app.post("/login")
def login(username:str,password:str):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id,username,password FROM users WHERE username=%s",
            (username,)
        )
        user = cur.fetchone()
        if not user:
            raise HTTPException(status_code=400,detail="用户名不存在")
        if user[2] != password:
            raise HTTPException(status_code=400,detail="密码错误")
        
        token = secrets.token_hex(32)
        expires_at = datetime.now() + timedelta(hours=24)
        cur.execute(
            "INSERT INTO tokens (user_id, token, expires_at) VALUES (%s, %s, %s)",
            (user[0], token, expires_at)
        )
        conn.commit()
        return {"message": "登录成功", "user_id": user[0], "user_name": user[1],"token": token}
    finally:
        cur.close()
        conn.close()

@app.post("/user/info")
def get_user_info(authorization: str = Header(None)):
    user_id = get_current_user(authorization)
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, username FROM users WHERE id=%s",
            (user_id,)
        )
        user = cur.fetchone()
        return {"user_id": user[0], "username": user[1]}
    finally:
        cur.close()
        conn.close()

@app.post("/products")
def create_product(
    name: str, price: float, stock: int,
    authorization: str = Header(None)   
):
    user_id = get_current_user(authorization)
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO products (name, price, stock, created_by) VALUES (%s, %s, %s, %s)",
            (name, price, stock, user_id)
        )
        conn.commit()
        return {"message": "创建商品成功", "product_name": name, "product_id": cur.lastrowid}
    except Exception as e:
        raise HTTPException(status_code=500, detail="创建商品失败")
    finally:
        cur.close()
        conn.close()    

@app.get("/products")
def get_products():
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id, name, price, stock FROM products"
        )
        rows = cur.fetchall()
        products = []
        for row in rows:
            products.append({
                "id": row[0],
                "name": row[1],
                "price": row[2],
                "stock": row[3]
            })
        return {"products": products}
    finally:
        cur.close()
        conn.close()

@app.post("/cart")
def add_to_cart(
    product_id: int, quantity: int = 1,
    authorization: str = Header(None)
):
    user_id = get_current_user(authorization)
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
                "SELECT id FROM cart WHERE user_id=%s AND product_id=%s",
                (user_id, product_id)
            )
        record = cur.fetchone()
        if record:
            cur.execute(
                "UPDATE cart SET quantity = quantity + %s WHERE user_id = %s AND product_id = %s",
                (quantity, user_id, product_id)
            )
        else:
            cur.execute(
                "INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)",
                (user_id, product_id, quantity)
            )
        conn.commit()
        return {"message": "添加到购物车成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="添加到购物车失败")
    finally:
        cur.close()
        conn.close()    

@app.post("/orders")
def create_order(
    product_id: int, quantity: int , 
    authorization: str = Header(None)
):
    user_id = get_current_user(authorization)
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT PRICE,stock FROM products WHERE id=%s",
            (product_id,)
        )
        product = cur.fetchone()
        if not product:
            raise HTTPException(status_code=400, detail="商品不存在")   
        if product[1] < quantity:
            raise HTTPException(status_code=400, detail="库存不足")
        cur.execute(
            "UPDATE products SET stock = stock - %s WHERE id = %s",
            (quantity, product_id)
        )
        total_price = product[0] * quantity
        cur.execute(
            "INSERT INTO orders (user_id, product_id, quantity, total_price) VALUES (%s, %s, %s, %s)",
            (user_id, product_id, quantity, total_price)
        )
        conn.commit()
        return {"message": "订单创建成功", "total_price": total_price}
    except HTTPException:
        raise              # HTTPException（400等）原样抛出，不改成500
    except Exception as e:
        print(f"下单失败: {e}")
        raise HTTPException(status_code=500, detail="下单失败")

    finally:
        cur.close()
        conn.close()
