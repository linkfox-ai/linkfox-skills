# linkfox-shopee-store-shop — 参数与字段参考

Shopee **Shop 模块**全部 9 个 API，经 **`POST /shopee/developerProxy`** 转发。

授权见 **`linkfox-shopee-store-auth`**。官方索引：[v2.shop.get_shop_info](https://open.shopee.com/documents/v2/v2.shop.get_shop_info?module=92&type=1)

## 通用约定

- **Base URL**：`https://tool-gateway.linkfox.com`
- **Method**：POST（网关），上游 Method 见各接口
- **Auth**：Header `Authorization: <api_key>`（`LINKFOXAGENT_API_KEY`）（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）
- **流程**：`POST /shopee/storeTokens` → `POST /shopee/developerProxy`
- **path**：须 `api/v2/shop/...`
- **官方文档 URL 规则**：`https://open.shopee.com/documents/v2/v2.shop.{api}?module=92&type=1`

---

## Shop 模块总览

| # | API | Method | path | 脚本 | 官方文档 |
|---|-----|--------|------|------|----------|
| 1 | get_shop_info | GET | `api/v2/shop/get_shop_info` | `get_shop_info.py` | [doc](https://open.shopee.com/documents/v2/v2.shop.get_shop_info?module=92&type=1) |
| 2 | get_profile | GET | `api/v2/shop/get_profile` | `get_profile.py` | [doc](https://open.shopee.com/documents/v2/v2.shop.get_profile?module=92&type=1) |
| 3 | update_profile | POST | `api/v2/shop/update_profile` | `update_profile.py` | [doc](https://open.shopee.com/documents/v2/v2.shop.update_profile?module=92&type=1) |
| 4 | get_warehouse_detail | GET | `api/v2/shop/get_warehouse_detail` | `get_warehouse_detail.py` | [doc](https://open.shopee.com/documents/v2/v2.shop.get_warehouse_detail?module=92&type=1) |
| 5 | get_shop_notification | GET | `api/v2/shop/get_shop_notification` | `get_shop_notification.py` | [doc](https://open.shopee.com/documents/v2/v2.shop.get_shop_notification?module=92&type=1) |
| 6 | get_authorised_reseller_brand | GET | `api/v2/shop/get_authorised_reseller_brand` | `get_authorised_reseller_brand.py` | [doc](https://open.shopee.com/documents/v2/v2.shop.get_authorised_reseller_brand?module=92&type=1) |
| 7 | get_br_shop_onboarding_info | GET | `api/v2/shop/get_br_shop_onboarding_info` | `get_br_shop_onboarding_info.py` | [doc](https://open.shopee.com/documents/v2/v2.shop.get_br_shop_onboarding_info?module=92&type=1) |
| 8 | get_shop_holiday_mode | GET | `api/v2/shop/get_shop_holiday_mode` | `get_shop_holiday_mode.py` | [doc](https://open.shopee.com/documents/v2/v2.shop.get_shop_holiday_mode?module=92&type=1) |
| 9 | set_shop_holiday_mode | POST | `api/v2/shop/set_shop_holiday_mode` | `set_shop_holiday_mode.py` | [doc](https://open.shopee.com/documents/v2/v2.shop.set_shop_holiday_mode?module=92&type=1) |

通用入口：`shop_api.py`（JSON 含 `"api": "<上表 API 名>"`）。

---

## 1. get_shop_info

[官方文档](https://open.shopee.com/documents/v2/v2.shop.get_shop_info?module=92&type=1)

**Query**：无额外业务参数（仅店铺公共 query）

**Response 要点**：`shop_name`、`region`、`status`（NORMAL/BANNED/FROZEN）、`is_cb`、`auth_time`、`expire_time`、`merchant_id`、`shop_fulfillment_flag`、SIP/跨境直发相关字段等

---

## 2. get_profile

[官方文档](https://open.shopee.com/documents/v2/v2.shop.get_profile?module=92&type=1)

**Query**：无额外业务参数

**Response 要点**：`shop_name`、`shop_logo`、`description`；巴西 CNPJ 卖家可能含 `invoice_issuer`

---

## 3. update_profile

[官方文档](https://open.shopee.com/documents/v2/v2.shop.update_profile?module=92&type=1)

**Body（至少一项）**：
| 字段 | 说明 |
|------|------|
| `shop_name` | 新店名（30 天内仅可改一次） |
| `shop_logo` | Shopee 图片 URL |
| `description` | 描述（≤500 字符） |

---

## 4. get_warehouse_detail

[官方文档](https://open.shopee.com/documents/v2/v2.shop.get_warehouse_detail?module=92&type=1)

**Query（可选）**：`warehouse_type` — `1` 揽收仓（默认）、`2` 退货仓

**Response 要点**：`warehouse_id`、`warehouse_name`、`location_id`、`address_id`、地址字段、`holiday_mode_state`

---

## 5. get_shop_notification

[官方文档](https://open.shopee.com/documents/v2/v2.shop.get_shop_notification?module=92&type=1)

**Query（可选）**：`cursor`（上一页 notification_id）、`page_size`（默认 10，最大 50）

**Response 要点**：`cursor`、`data.title`、`data.content`、`data.create_time`、`data.url`

---

## 6. get_authorised_reseller_brand

[官方文档](https://open.shopee.com/documents/v2/v2.shop.get_authorised_reseller_brand?module=92&type=1)

**Query（必填）**：`page_no`（从 1 起）、`page_size`（1–30）

**Response 要点**：`is_authorised_reseller`、`total_count`、`more`、`authorised_brand_list[]`

---

## 7. get_br_shop_onboarding_info

[官方文档](https://open.shopee.com/documents/v2/v2.shop.get_br_shop_onboarding_info?module=92&type=1)

**Query**：无额外业务参数

**区域**：仅巴西站。返回 KYC / 税号（CPF/CNPJ）、`onboarding_status`、`billing_address` 等

---

## 8. get_shop_holiday_mode

[官方文档](https://open.shopee.com/documents/v2/v2.shop.get_shop_holiday_mode?module=92&type=1)

**Query**：无额外业务参数

**Response 要点**：`holiday_mode_on`、`holiday_mode_mtime`

---

## 9. set_shop_holiday_mode

[官方文档](https://open.shopee.com/documents/v2/v2.shop.set_shop_holiday_mode?module=92&type=1)

**Body（必填）**：`holiday_mode_on`（boolean）— `true` 开启假期模式（买家无法下单）

---

## 网关错误码

| errcode | 含义 | 建议 |
|---------|------|------|
| 1002 | 参数/未登录 | 检查 shopId 与 API Key |
| 1003 | 代理/网络异常 | 重试 |
| 1004 | 无授权记录 | auth skill |
| 1005 | path 未白名单 | 确认 `api/v2/shop/...` |
| HTTP 402 | 积分不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |

---

## curl 示例

```bash
export KEY=${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}
BASE=${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}

# 店铺信息
curl -X POST $BASE/shopee/developerProxy -H "Authorization: $KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "api/v2/shop/get_shop_info",
    "method": "GET",
    "accessToken": "xxx",
    "shopId": "67890"
  }'

# 更新资料
curl -X POST $BASE/shopee/developerProxy -H "Authorization: $KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "api/v2/shop/update_profile",
    "method": "POST",
    "accessToken": "xxx",
    "shopId": "67890",
    "body": "{\"description\":\"Welcome to our shop!\"}"
  }'
```

---

## Feedback API

```bash
curl -X POST https://skill-api.linkfox.com/api/v1/public/feedback \
  -H "Content-Type: application/json" \
  -d '{"skillName":"linkfox-shopee-store-shop","sentiment":"POSITIVE",
       "category":"OTHER","content":"店铺信息查询正常"}'
```
