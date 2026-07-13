# linkfox-shopee-store-payment — 参数与字段参考

Shopee **Payment 模块**全部 18 个 API，经 **`POST /shopee/developerProxy`** 转发。

授权见 **`linkfox-shopee-store-auth`**。官方索引：[v2.payment.get_escrow_detail](https://open.shopee.com/documents/v2/v2.payment.get_escrow_detail?module=97&type=1)

## 通用约定

- **Base URL**：`${LINKFOX_TOOL_GATEWAY}`
- **Method**：POST（网关），上游 Method 见各接口
- **Auth**：Header `Authorization: <api_key>`（从 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取）（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）
- **流程**：`POST /shopee/storeTokens` → `POST /shopee/developerProxy`
- **path**：须 `api/v2/payment/...`
- **标识**：店铺级 API，通常传 **`shopId`**
- **官方文档 URL 规则**：`https://open.shopee.com/documents/v2/v2.payment.{api}?module=97&type=1`

---

## Payment 模块总览

| # | API | Method | path | 脚本 | 官方文档 |
|---|-----|--------|------|------|----------|
| 1 | generate_income_report | POST | `api/v2/payment/generate_income_report` | `generate_income_report.py` | [doc](https://open.shopee.com/documents/v2/v2.payment.generate_income_report?module=97&type=1) |
| 2 | generate_income_statement | POST | `api/v2/payment/generate_income_statement` | `generate_income_statement.py` | [doc](https://open.shopee.com/documents/v2/v2.payment.generate_income_statement?module=97&type=1) |
| 3 | get_billing_transaction_info | GET | `api/v2/payment/get_billing_transaction_info` | `get_billing_transaction_info.py` | [doc](https://open.shopee.com/documents/v2/v2.payment.get_billing_transaction_info?module=97&type=1) |
| 4 | get_escrow_detail | GET | `api/v2/payment/get_escrow_detail` | `get_escrow_detail.py` | [doc](https://open.shopee.com/documents/v2/v2.payment.get_escrow_detail?module=97&type=1) |
| 5 | get_escrow_detail_batch | POST | `api/v2/payment/get_escrow_detail_batch` | `get_escrow_detail_batch.py` | [doc](https://open.shopee.com/documents/v2/v2.payment.get_escrow_detail_batch?module=97&type=1) |
| 6 | get_escrow_list | GET | `api/v2/payment/get_escrow_list` | `get_escrow_list.py` | [doc](https://open.shopee.com/documents/v2/v2.payment.get_escrow_list?module=97&type=1) |
| 7 | get_income_detail | GET | `api/v2/payment/get_income_detail` | `get_income_detail.py` | [doc](https://open.shopee.com/documents/v2/v2.payment.get_income_detail?module=97&type=1) |
| 8 | get_income_overview | GET | `api/v2/payment/get_income_overview` | `get_income_overview.py` | [doc](https://open.shopee.com/documents/v2/v2.payment.get_income_overview?module=97&type=1) |
| 9 | get_income_report | GET | `api/v2/payment/get_income_report` | `get_income_report.py` | [doc](https://open.shopee.com/documents/v2/v2.payment.get_income_report?module=97&type=1) |
| 10 | get_income_statement | GET | `api/v2/payment/get_income_statement` | `get_income_statement.py` | [doc](https://open.shopee.com/documents/v2/v2.payment.get_income_statement?module=97&type=1) |
| 11 | get_item_installment_status | GET | `api/v2/payment/get_item_installment_status` | `get_item_installment_status.py` | [doc](https://open.shopee.com/documents/v2/v2.payment.get_item_installment_status?module=97&type=1) |
| 12 | get_payment_method_list | GET | `api/v2/payment/get_payment_method_list` | `get_payment_method_list.py` | [doc](https://open.shopee.com/documents/v2/v2.payment.get_payment_method_list?module=97&type=1) |
| 13 | get_payout_detail | GET | `api/v2/payment/get_payout_detail` | `get_payout_detail.py` | [doc](https://open.shopee.com/documents/v2/v2.payment.get_payout_detail?module=97&type=1) |
| 14 | get_payout_info | GET | `api/v2/payment/get_payout_info` | `get_payout_info.py` | [doc](https://open.shopee.com/documents/v2/v2.payment.get_payout_info?module=97&type=1) |
| 15 | get_shop_installment_status | GET | `api/v2/payment/get_shop_installment_status` | `get_shop_installment_status.py` | [doc](https://open.shopee.com/documents/v2/v2.payment.get_shop_installment_status?module=97&type=1) |
| 16 | get_wallet_transaction_list | GET | `api/v2/payment/get_wallet_transaction_list` | `get_wallet_transaction_list.py` | [doc](https://open.shopee.com/documents/v2/v2.payment.get_wallet_transaction_list?module=97&type=1) |
| 17 | set_item_installment_status | POST | `api/v2/payment/set_item_installment_status` | `set_item_installment_status.py` | [doc](https://open.shopee.com/documents/v2/v2.payment.set_item_installment_status?module=97&type=1) |
| 18 | set_shop_installment_status | POST | `api/v2/payment/set_shop_installment_status` | `set_shop_installment_status.py` | [doc](https://open.shopee.com/documents/v2/v2.payment.set_shop_installment_status?module=97&type=1) |
通用入口：`payment_api.py`（JSON 含 `"api": "<上表 API 名>"`）。

---

## 常用接口说明

### 托管/结算

| API | 要点 |
|-----|------|
| `get_escrow_detail` | 必填 `order_sn`；订单托管/结算明细 |
| `get_escrow_list` | 托管列表；时间范围筛选 |
| `get_escrow_detail_batch` | POST 批量查 escrow |

### 打款/钱包

| API | 要点 |
|-----|------|
| `get_payout_detail` | 打款明细 |
| `get_payout_info` | 打款汇总 |
| `get_wallet_transaction_list` | 钱包流水 |
| `get_billing_transaction_info` | 账单交易信息 |

### 分期

| API | 要点 |
|-----|------|
| `get_shop_installment_status` / `set_shop_installment_status` | 店铺分期开关 |
| `get_item_installment_status` / `set_item_installment_status` | 商品分期 |

### 收入报表

| API | 要点 |
|-----|------|
| `generate_income_statement` / `get_income_statement` | 异步生成/获取 income statement |
| `generate_income_report` / `get_income_report` | 异步生成/获取 income report |
| `get_income_overview` / `get_income_detail` | 收入概览与明细 |

### 其他

| API | 要点 |
|-----|------|
| `get_payment_method_list` | 可用支付方式 |

---

## 网关错误码

| errcode | 含义 | 建议 |
|---------|------|------|
| 1002 | 参数/未登录 | 检查 shopId 与 API Key |
| 1003 | 代理/网络异常 | 重试 |
| 1004 | 无授权记录 | auth skill |
| 1005 | path 未白名单 | 确认 `api/v2/payment/...` |

---

## curl 示例

```bash
export KEY=$LINKFOXAGENT_API_KEY
BASE=https://tool-gateway.linkfox.com

curl -X POST $BASE/shopee/developerProxy -H "Authorization: $KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "api/v2/payment/get_escrow_detail",
    "method": "GET",
    "accessToken": "xxx",
    "shopId": "67890",
    "queryString": "order_sn=240101ABC"
  }'
```

---

## Feedback API

```bash
curl -X POST https://skill-api.linkfox.com/api/v1/public/feedback \
  -H "Content-Type: application/json" \
  -d '{"skillName":"linkfox-shopee-store-payment","sentiment":"POSITIVE",
       "category":"OTHER","content":"托管明细查询正常"}'
```
