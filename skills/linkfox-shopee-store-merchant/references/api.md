# linkfox-shopee-store-merchant — 参数与字段参考

Shopee **Merchant 模块**全部 6 个 API，经 **`POST /shopee/developerProxy`** 转发。

授权见 **`linkfox-shopee-store-auth`**。官方索引：[v2.merchant.get_merchant_info](https://open.shopee.com/documents/v2/v2.merchant.get_merchant_info?module=93&type=1)

## 通用约定

- **Base URL**：`${LINKFOX_TOOL_GATEWAY}`
- **Method**：POST（网关），上游 Method 见各接口
- **Auth**：Header `Authorization: <api_key>`（从 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取）（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）
- **流程**：`POST /shopee/storeTokens` → `POST /shopee/developerProxy`
- **path**：须 `api/v2/merchant/...`
- **标识**：Merchant 模块为**商户级** API，须传 **`merchantId`**
- **适用对象**：主要为**跨境卖家**（CNSC/CBSC）；本地卖家通常不需要
- **官方文档 URL 规则**：`https://open.shopee.com/documents/v2/v2.merchant.{api}?module=93&type=1`

---

## Merchant 模块总览

| # | API | Method | path | 脚本 | 官方文档 |
|---|-----|--------|------|------|----------|
| 1 | get_merchant_info | GET | `api/v2/merchant/get_merchant_info` | `get_merchant_info.py` | [doc](https://open.shopee.com/documents/v2/v2.merchant.get_merchant_info?module=93&type=1) |
| 2 | get_merchant_prepaid_account_list | GET | `api/v2/merchant/get_merchant_prepaid_account_list` | `get_merchant_prepaid_account_list.py` | [doc](https://open.shopee.com/documents/v2/v2.merchant.get_merchant_prepaid_account_list?module=93&type=1) |
| 3 | get_merchant_warehouse_list | GET | `api/v2/merchant/get_merchant_warehouse_list` | `get_merchant_warehouse_list.py` | [doc](https://open.shopee.com/documents/v2/v2.merchant.get_merchant_warehouse_list?module=93&type=1) |
| 4 | get_merchant_warehouse_location_list | GET | `api/v2/merchant/get_merchant_warehouse_location_list` | `get_merchant_warehouse_location_list.py` | [doc](https://open.shopee.com/documents/v2/v2.merchant.get_merchant_warehouse_location_list?module=93&type=1) |
| 5 | get_shop_list_by_merchant | GET | `api/v2/merchant/get_shop_list_by_merchant` | `get_shop_list_by_merchant.py` | [doc](https://open.shopee.com/documents/v2/v2.merchant.get_shop_list_by_merchant?module=93&type=1) |
| 6 | get_warehouse_eligible_shop_list | GET | `api/v2/merchant/get_warehouse_eligible_shop_list` | `get_warehouse_eligible_shop_list.py` | [doc](https://open.shopee.com/documents/v2/v2.merchant.get_warehouse_eligible_shop_list?module=93&type=1) |
通用入口：`merchant_api.py`（JSON 含 `"api": "<上表 API 名>"`）。

---

## 接口说明

### get_merchant_info

[官方文档](https://open.shopee.com/documents/v2/v2.merchant.get_merchant_info?module=93&type=1)

**Query**：无额外业务参数（公共参数含 merchant_id）

**Response 要点**：`merchant_name`、`merchant_region`、`merchant_currency`、`auth_time`、`expire_time`、`is_cnsc`、`is_upgraded_cbsc`

### get_shop_list_by_merchant

[官方文档](https://open.shopee.com/documents/v2/v2.merchant.get_shop_list_by_merchant?module=93&type=1)

**Query（必填）**：`page_no`（从 1 起）、`page_size`（最大 500）

**Response 要点**：`shop_list[]`（`shop_id`、`sip_affi_shops` 等）、`more`、`is_cnsc`

### get_merchant_warehouse_location_list / get_merchant_warehouse_list

商户仓库位置与仓库列表。

### get_warehouse_eligible_shop_list

可使用仓库的店铺列表。

### get_merchant_prepaid_account_list

商户预付账户列表。

---

## 网关错误码

| errcode | 含义 | 建议 |
|---------|------|------|
| 1002 | 参数/未登录 | 检查 merchantId 与 API Key |
| 1003 | 代理/网络异常 | 重试 |
| 1004 | 无授权记录 | auth skill |
| 1005 | path 未白名单 | 确认 `api/v2/merchant/...` |

---

## curl 示例

```bash
export KEY=$LINKFOXAGENT_API_KEY
BASE=https://tool-gateway.linkfox.com

# 商户信息
curl -X POST $BASE/shopee/developerProxy -H "Authorization: $KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "api/v2/merchant/get_merchant_info",
    "method": "GET",
    "accessToken": "xxx",
    "merchantId": "12345"
  }'

# 商户下店铺列表
curl -X POST $BASE/shopee/developerProxy -H "Authorization: $KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "api/v2/merchant/get_shop_list_by_merchant",
    "method": "GET",
    "accessToken": "xxx",
    "merchantId": "12345",
    "queryString": "page_no=1&page_size=100"
  }'
```

---

## Feedback API

```bash
curl -X POST https://skill-api.linkfox.com/api/v1/public/feedback \
  -H "Content-Type: application/json" \
  -d '{"skillName":"linkfox-shopee-store-merchant","sentiment":"POSITIVE",
       "category":"OTHER","content":"商户信息查询正常"}'
```
