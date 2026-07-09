# linkfox-shopee-store-public — 参数与字段参考

Shopee **Public 模块**全部 6 个 API，经 **`POST /shopee/developerProxy`** 转发。

授权见 **`linkfox-shopee-store-auth`**。官方索引：[v2.public.get_shops_by_partner](https://open.shopee.com/documents/v2/v2.public.get_shops_by_partner?module=104&type=1)

## 通用约定

- **path**：须 `api/v2/public/...`
- **Partner 级接口**：`get_shops_by_partner` / `get_merchants_by_partner` 等通常无需 `shopId`
- **OAuth 接口**：`get_access_token` / `refresh_access_token` / `get_token_by_resend_code` 传 POST `body`
- **官方文档 URL 规则**：`https://open.shopee.com/documents/v2/v2.public.{api}?module=104&type=1`

---

## Public 模块总览

| # | API | Method | path | 脚本 | 官方文档 |
|---|-----|--------|------|------|----------|
| 1 | get_access_token | POST | `api/v2/public/get_access_token` | `get_access_token.py` | [doc](https://open.shopee.com/documents/v2/v2.public.get_access_token?module=104&type=1) |
| 2 | get_merchants_by_partner | GET | `api/v2/public/get_merchants_by_partner` | `get_merchants_by_partner.py` | [doc](https://open.shopee.com/documents/v2/v2.public.get_merchants_by_partner?module=104&type=1) |
| 3 | get_shopee_ip_ranges | GET | `api/v2/public/get_shopee_ip_ranges` | `get_shopee_ip_ranges.py` | [doc](https://open.shopee.com/documents/v2/v2.public.get_shopee_ip_ranges?module=104&type=1) |
| 4 | get_shops_by_partner | GET | `api/v2/public/get_shops_by_partner` | `get_shops_by_partner.py` | [doc](https://open.shopee.com/documents/v2/v2.public.get_shops_by_partner?module=104&type=1) |
| 5 | get_token_by_resend_code | POST | `api/v2/public/get_token_by_resend_code` | `get_token_by_resend_code.py` | [doc](https://open.shopee.com/documents/v2/v2.public.get_token_by_resend_code?module=104&type=1) |
| 6 | refresh_access_token | POST | `api/v2/public/refresh_access_token` | `refresh_access_token.py` | [doc](https://open.shopee.com/documents/v2/v2.public.refresh_access_token?module=104&type=1) |
通用入口：`public_api.py`（JSON 含 `"api": "<上表 API 名>"`）。

---

## 常用接口说明

| API | 要点 |
|-----|------|
| `get_shops_by_partner` | 查询 Partner 下已授权店铺列表 |
| `get_merchants_by_partner` | 查询 Partner 下已授权商户列表 |
| `get_access_token` | 用 auth code 换 token |
| `refresh_access_token` | 刷新 access token |
| `get_token_by_resend_code` | 通过 resend code 获取 token |
| `get_shopee_ip_ranges` | Shopee 开放平台 IP 段（白名单配置） |

> 日常授权与已授权店铺查询优先使用 **`linkfox-shopee-store-auth`**（`authorize_url.py` / `authorized_stores.py` / `store_tokens.py`）。

---

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/shopee/developerProxy \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "api/v2/public/get_shops_by_partner",
    "method": "GET",
    "accessToken": "xxx"
  }'
```

---

## Feedback API

```bash
curl -X POST https://skill-api.linkfox.com/api/v1/public/feedback \
  -H "Content-Type: application/json" \
  -d '{"skillName":"linkfox-shopee-store-public","sentiment":"POSITIVE",
       "category":"OTHER","content":"Public API查询正常"}'
```
