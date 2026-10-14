# TikTok Shop ERP Order API Reference

## MCP 调用

| 项 | 固定值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `tiktokShop/developerProxy` |
| `arguments` | 直接使用本 reference 的请求对象；不得额外包裹 `body`、`data` 或另一层 `arguments` |
| 响应字段来源 | `skills/linkfox-tiktok-shop-order/references/api.md`；只按其响应契约核对字段表 |

```json
{
  "toolName": "tiktokShop/developerProxy",
  "arguments": {"appType": "erp", "openId": "<openId>", "path": "order/202309/orders/search", "method": "POST"}
}
```

- `toolName` 精确匹配且区分大小写；MCP 缺失时停止，禁止 HTTP fallback。
- WorkBuddy 自动注入 MCP Authorization；不得传 LinkFox `headers`、API Key、`token`、JWT 或手机号。
- 收费失败、空结果或结果不理想时不自动重试；相同 `toolName + arguments` 在同一任务内不重复调用。
- 先处理 MCP/schema/`isError`；text JSON 只解析一次；再检查下游错误字段和业务结果。

本文档是 **`linkfox-tiktok-shop-order`** 的接口总览与转发说明。
**每个接口的完整官方参数/响应/错误码**见 `linkfox-tiktok-shop-order--apis--<api>.md`。

> ⚠️ 依赖 **`linkfox-tiktok-shop-auth`**（`appType=erp`）。
> 官方入口：[Get Order List](https://partner.tiktokshop.com/docv2/page/get-order-list-202309)。

---

## 1. 转发约定（Agent 必读）

### 调用链

```
linkfox-tiktok-shop-auth  →  openId（选店）
        ↓
POST tiktokShop/developerProxy
  appType = erp
  openId  = <ERP openId>          # 网关按 openId+appType 从库取 token
  path / method / queryString / body
        ↓
若上游 401 或 token expired/invalid → 网关自动 refresh 并重试一次，回写库
        ↓
紫鸟注入 app_key / timestamp / sign → TikTok Open API
```

> ⚠️ **ACCESS_TOKEN 已后台化**：勿传 `ttsAccessToken`（即使传入也会被忽略）。业务调用**不要**先调 `/storeTokens` 或 `/refreshToken`。

### developerProxy 入参

| 参数 | 必填 | 说明 |
|------|------|------|
| path | 是 | 相对路径，不含主机名 |
| method | 是 | `GET` / `POST` |
| openId | 是 | 卖家 open_id；网关据此取库中 token |
| appType | 是 | **固定 `erp`** |
| region | 否 | 默认 `global`，美国站 `us` |
| queryString | 视接口 | 不含 `?`；订单 API 须含 `shop_cipher` |
| body | 视接口 | JSON 字符串（Get Order List 的筛选条件） |
| ttsAccessToken | 否 | **已废弃**，忽略 |

### path 白名单

- `authorization/`
- `order/`

> 履约拆单/发货（`fulfillment/`）请用 **`linkfox-tiktok-shop-fulfillment`**。取消售后（`return_refund/`）另开 skill。

### shop_cipher

1. `get_authorized_shops` → `data.shops[].cipher`
2. Query：`shop_cipher=<cipher>`
3. 多店须显式传；单店也须显式传入

---

## 2. 接口索引

| api | Method | path | shop_cipher | 完整参考 | 官方 |
|-----|--------|------|-------------|----------|------|
| `get_authorized_shops` | GET | `authorization/202309/shops` | 否 | [Get Authorized Shops](linkfox-tiktok-shop-order--apis--get_authorized_shops.md) | [doc](https://partner.tiktokshop.com/docv2/page/get-authorized-shops-202309) |
| `get_order_list` | POST | `order/202309/orders/search` | 是 | [Get Order List](linkfox-tiktok-shop-order--apis--get_order_list.md) | [doc](https://partner.tiktokshop.com/docv2/page/get-order-list-202309) |
| `get_order_detail` | GET | `order/202507/orders` | 是 | [Get Order Detail](linkfox-tiktok-shop-order--apis--get_order_detail.md) | [doc](https://partner.tiktokshop.com/docv2/page/get-order-detail-202507) |
| `get_order_detail_202309` | GET | `order/202309/orders` | 是 | [Get Order Detail](linkfox-tiktok-shop-order--apis--get_order_detail_202309.md) | [doc](https://partner.tiktokshop.com/docv2/page/get-order-detail-202309) |

### 推荐链路

```
get_authorized_shops → shop_cipher
  → get_order_list（按时间/状态筛选）
  → get_order_detail（ids=订单号列表）
```

### 通用调用

> 旧 HTTP/脚本示例已移除；使用本页 `MCP 调用` 的完整 `proxy_call` 参数结构。

---

## 3. Feedback

- POST `https://skill-api.linkfox.com/api/v1/public/feedback`
- `skillName`: `linkfox-tiktok-shop-order`

## 4. Notes

1. Get Order List 的时间窗与状态过滤写在 **body**；`page_size`/`page_token` 在 **query**。
2. Get Order Detail 的 `ids` 为 Query，可传数组（脚本会拼成逗号分隔）。
3. 默认详情接口为 **202507**；需要旧版时用 `get_order_detail_202309`。
4. 勿输出完整 ERP token。
