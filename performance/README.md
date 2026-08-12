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

2. 启动压测（终端2）：

```bash
cd performance
locust
```

3. 浏览器打开 `http://localhost:8089`，设置：
   - Number of users（并发用户数）：`100`
   - Ramp up（启动速度）：`10`
   - Host：`http://127.0.0.1:8000`

4. 点 Start swarming 开始压测。

## 结果查看

网页实时展示：RPS、平均/中位数/P95/P99 响应时间、失败率。

## 结论

详见 [report.md](report.md)。
