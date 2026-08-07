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
        cur.execute(
            "UPDATE products SET stock = stock - %s WHERE id = %s AND stock >= %s",
            (quantity, product_id, quantity)
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=400, detail="库存不足")
        total_price = product[0] * quantity
        cur.execute(
            "INSERT INTO orders (user_id, product_id, quantity, total_price) VALUES (%s, %s, %s, %s)",
            (user_id, product_id, quantity, total_price)
        )
        conn.commit()
        return {"message": "订单创建成功", "total_price": total_price, "order_id": cur.lastrowid}
    except HTTPException:
        raise             
    except Exception as e:
        print(f"下单失败: {e}")
        raise HTTPException(status_code=500, detail="下单失败")

    finally:
        cur.close()
        conn.close()

@app.post("/pay")
def pay(order_id: int, authorization: str = Header(None)):
    user_id = get_current_user(authorization)
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT status FROM orders WHERE id=%s AND user_id=%s",
            (order_id, user_id)
        )
        order = cur.fetchone()
        if not order:
            raise HTTPException(status_code=400, detail="订单不存在")
        if order[0] != "pending":
            raise HTTPException(status_code=400, detail="订单状态不正确")
        cur.execute(
            "UPDATE orders SET status='paid' WHERE id=%s",
            (order_id,)
        )
        conn.commit()
        return {"message": "支付成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="支付失败")
    finally:
        cur.close()
        conn.close()

@app.post("/refund")
def refund(order_id: int, authorization: str = Header(None)):
    user_id = get_current_user(authorization)
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT status,quantity,product_id FROM orders WHERE id=%s AND user_id=%s",
            (order_id, user_id)
        )
        order = cur.fetchone()
        if not order:
            raise HTTPException(status_code=400, detail="订单不存在")
        if order[0] != "paid":
            raise HTTPException(status_code=400, detail="订单状态不正确")
        cur.execute(
            "UPDATE orders SET status = 'refunded' WHERE id = %s AND user_id=%s",
            (order_id, user_id)
        )
        cur.execute(
            "UPDATE products SET stock = stock + %s WHERE id = %s",
            (order[1], order[2])
        )
        conn.commit()
        return{"message": "退款成功"}
    except HTTPException:
        raise
    except Exception:
        conn.rollback()
        raise HTTPException(500, "退款失败")
    finally:
        cur.close()
        conn.close()

@app.post("/complete")
def complete(order_id: int, authorization: str = Header(None)):
    user_id = get_current_user(authorization)
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT status,quantity,product_id FROM orders WHERE id=%s AND user_id=%s",
            (order_id, user_id)
        )
        order = cur.fetchone()
        if not order:
            raise HTTPException(status_code=400, detail="订单不存在")
        if order[0] != "paid":
            raise HTTPException(status_code=400, detail="订单状态不正确")
        cur.execute(
            "UPDATE orders SET status = 'complete' WHERE id = %s AND user_id=%s",
            (order_id, user_id)
        )
        conn.commit()
        return{"message": "订单完成"}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(500,"完成失败")
    finally:
        cur.close()
        conn.close()

@app.get("/orders")
def get_orders(authorization: str = Header(None)):
    user_id = get_current_user(authorization)
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id, product_id, quantity, total_price, status FROM orders WHERE user_id=%s",
            (user_id,)
        )
        rows = cur.fetchall()
        orders = []
        for row in rows:
            orders.append({
                "id": row[0],
                "product_id": row[1],
                "quantity": row[2],
                "total_price": row[3],
                "status": row[4]
            })
        return {"orders": orders}
    finally:
        cur.close()
        conn.close()

