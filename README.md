# Mall System 商城系统接口自动化测试项目

基于 **FastAPI + PyMySQL + Pytest + Allure + GitHub Actions** 实现的商城业务系统与接口自动化测试项目。

一个可运行的商品商城后端（注册/登录/商品/购物车/下单/支付/退款/订单完成），配以完整的接口自动化测试覆盖，并通过 CI 流水线实现测试自动化与可视化报告。

## 技术栈

| 技术 | 用途 |
|------|------|
| FastAPI | 后端接口框架 |
| PyMySQL | 数据库访问 |
| Pytest | 测试框架 |
| Allure | 可视化测试报告 |
| GitHub Actions | CI 持续集成 |
| Threading | 并发测试 |

## 项目结构

```
mall-system/
├── backend/
│   ├── main.py            # FastAPI 后端（全部接口）
│   └── schema.sql         # 数据库建表脚本
├── tests/
│   ├── conftest.py        # 测试夹具（token/product_id/order_id/paid_order_id + 数据清理）
│   ├── test_login.py      # 登录测试
│   ├── test_products.py   # 商品测试
│   ├── test_cart.py       # 购物车测试
│   ├── test_orders.py     # 下单测试
│   ├── test_pay.py        # 支付测试
│   ├── test_refund.py     # 退款测试
│   ├── test_complete.py   # 订单完成测试
│   ├── test_orders_query.py  # 订单查询测试
│   ├── test_oversell.py   # 库存超卖并发测试
│   ├── test_register.py   # 注册测试
│   └── test_user_info.py  # 用户信息测试
├── .github/workflows/
│   └── ci.yml             # CI 流水线
├── pytest.ini             # pytest 配置（自动生成 Allure 结果）
├── requirements.txt       # 依赖清单
└── README.md
```

## 快速开始

### 1. 初始化数据库

```bash
mysql -uroot -p123456 < backend/schema.sql
```

脚本会创建 `mall` 库、5 张表（users/tokens/products/cart/orders），并写入测试用户 test01/test02。

### 2. 启动后端

```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 3. 运行测试

```bash
pytest
```

### 4. 生成测试报告

```bash
allure generate reports/result -o reports/html --clean
allure open reports/html
```

## 测试覆盖

| 模块 | 接口 | 覆盖场景 |
|------|------|----------|
| 注册 | POST /register | 成功 / 重名拦截 / 空用户名 |
| 登录 | POST /login | 成功 / 密码错误 / 用户不存在 |
| 商品 | POST/GET /products | 创建成功 / 未授权 |
| 购物车 | POST /cart | 添加 / 合并数量 / 未授权 |
| 下单 | POST /orders | 扣库存 / 库存不足 / 商品不存在 |
| 支付 | POST /pay | 成功 / 重复支付 / 订单不存在 |
| 退款 | POST /refund | 成功 / 越权拦截 / 重复退款 / 状态校验 |
| 完成 | POST /complete | 成功 / 状态校验 / 重复完成 |

共 **37 条测试用例**，全部通过。

## 测试亮点

- **库存超卖并发测试**：用 10 线程并发下单复现 check-then-act 竞态（实测 8 单超卖），再用原子 UPDATE 修复，验证并发安全
- **越权防护测试**：跨用户操作（test02 操作 test01 的订单）被拦截
- **测试数据治理**：autouse 清理 fixture，每个测试结束后清空测试数据，保证可重复执行
- **Fixture 分层抽象**：token → product_id → order_id → paid_order_id 四级夹具链，消除测试重复代码
- **CI 自动化**：push 到 master 自动触发流水线（建库 → 起后端 → 跑测试 → 生成 Allure 报告 → 上传产物）

## CI

流水线配置见 `.github/workflows/ci.yml`：

1. 触发：push / pull_request 到 master
2. 环境：Ubuntu + Python 3.10 + MySQL 8.0
3. 流程：初始化数据库 → 安装依赖 → 启动后端 → 运行 pytest → 生成 Allure 报告 → 上传 artifact
