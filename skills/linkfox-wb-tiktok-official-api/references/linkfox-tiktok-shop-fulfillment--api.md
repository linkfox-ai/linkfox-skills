# TikTok Shop ERP Fulfillment API Reference

## MCP 调用

| 项 | 固定值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `tiktokShop/developerProxy` |
| `arguments` | 直接使用本 reference 的请求对象；不得额外包裹 `body`、`data` 或另一层 `arguments` |
| 响应字段来源 | `skills/linkfox-tiktok-shop-fulfillment/references/api.md`；只按其响应契约核对字段表 |

```json
{
  "toolName": "tiktokShop/developerProxy",
  "arguments": {"appType": "erp", "openId": "<openId>", "path": "fulfillment/202309/orders/split_attributes", "method": "GET"}
}
```

- `toolName` 精确匹配且区分大小写；MCP 缺失时停止，禁止 HTTP fallback。
- WorkBuddy 自动注入 MCP Authorization；不得传 LinkFox `headers`、API Key、`token`、JWT 或手机号。
- 收费失败、空结果或结果不理想时不自动重试；相同 `toolName + arguments` 在同一任务内不重复调用。
- 先处理 MCP/schema/`isError`；text JSON 只解析一次；再检查下游错误字段和业务结果。

本文档是 **`linkfox-tiktok-shop-fulfillment`** 的接口总览与转发说明。
**每个接口的完整官方参数/响应/错误码**见 `linkfox-tiktok-shop-fulfillment--apis--<api>.md`。

> ⚠️ 依赖 **`linkfox-tiktok-shop-auth`**（`appType=erp`）。
> 官方入口：[Get Order Split Attributes](https://partner.tiktokshop.com/docv2/page/get-order-split-attributes-202309)。

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
| queryString | 视接口 | 不含 `?`；履约 API 须含 `shop_cipher` |
| body | 视接口 | JSON 字符串 |
| ttsAccessToken | 否 | **已废弃**，忽略 |

### path 白名单

- `authorization/`
- `fulfillment/`

> 订单 list/detail 请用 **`linkfox-tiktok-shop-order`**（`order/`）。取消售后（`return_refund/`）另开 skill。

### shop_cipher

1. `get_authorized_shops` → `data.shops[].cipher`
2. Query：`shop_cipher=<cipher>`
3. 多店须显式传；单店也须显式传入

---

## 2. 接口索引

| api | Method | path | shop_cipher | 完整参考 | 官方 |
|-----|--------|------|-------------|----------|------|
| `get_authorized_shops` | GET | `authorization/202309/shops` | 否 | [Get Authorized Shops](linkfox-tiktok-shop-fulfillment--apis--get_authorized_shops.md) | [doc](https://partner.tiktokshop.com/docv2/page/get-authorized-shops-202309) |
| `get_order_split_attributes` | GET | `fulfillment/202309/orders/split_attributes` | 是 | [Get Order Split Attributes](linkfox-tiktok-shop-fulfillment--apis--get_order_split_attributes.md) | [doc](https://partner.tiktokshop.com/docv2/page/get-order-split-attributes-202309) |

### 推荐链路

```
linkfox-tiktok-shop-order（拿 order id）
  → get_authorized_shops → shop_cipher
  → get_order_split_attributes（order_ids=...）
```

### 通用调用

> 旧 HTTP/脚本示例已移除；使用本页 `MCP 调用` 的完整 `proxy_call` 参数结构。

---

## 3. Feedback

- POST `https://skill-api.linkfox.com/api/v1/public/feedback`
- `skillName`: `linkfox-tiktok-shop-fulfillment`

## 4. Notes

1. Get Order Split Attributes 的 `order_ids` 为 Query，可传数组（脚本会拼成逗号分隔）。
2. 上游 path 属于 **`fulfillment/`**（不是 `order/`）。
3. 后续可在本 skill 扩展 Split Orders / Ship Package 等履约接口。
4. 勿输出完整 ERP token。
