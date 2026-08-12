# 性能测试（Locust）

对商城后端接口做并发压测，验证响应时间、吞吐量（RPS）与稳定性。

## 环境依赖

```
pip install locust DBUtils
```

## 启动步骤

1. 启动后端（终端1）：

```bash
cd backend
uvicorn main:app --port 8000
```

2. 启动压测（终端2），按需选择压测文件：

```bash
cd performance
locust                        # 默认压 GET /products（locustfile.py）
locust -f locustfile_login.py # 压 POST /login
locust -f locustfile_orders.py# 压 POST /orders（需先建压测商品，见下方说明）
```

3. 浏览器打开 `http://localhost:8089`，设置：
   - Number of users（并发用户数）：`100`
   - Ramp up（启动速度）：`10`
   - Host：`http://127.0.0.1:8000`

4. 点 Start swarming 开始压测。

## 压 /orders 前置

/orders 需要 token 鉴权和真实商品。`locustfile_orders.py` 使用 `on_start` 钩子让每个虚拟用户启动时登录一次拿 token，再反复下单。压测前需在库里准备带库存的商品，`locustfile_orders.py` 里的 `product_id` 要改成对应商品。

## 结果查看

网页实时展示：RPS、平均/中位数/P95/P99 响应时间、失败率。

## 结论

详见 [report.md](report.md)。
