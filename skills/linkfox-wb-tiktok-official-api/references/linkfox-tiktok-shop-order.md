---
name: linkfox-tiktok-shop-order
description: TikTok Shop ERP 订单（Order）业务技能，经 tiktokShop/developerProxy（appType=erp）转发 Order Open API：获取订单列表（Get Order List）、订单详情（Get Order Detail）。依赖 linkfox-tiktok-shop-auth 选店（传 openId；token 后台化，勿手动 refresh）。当用户提到 TikTok 小店订单、ERP 订单、订单列表、订单详情、Get Order List、Get Order Detail、查待发货订单、按状态筛订单、TikTok Shop order API、order/202309/orders/search 时触发。**不含授权**（用 linkfox-tiktok-shop-auth）；**不含履约发货/取消售后**（后续 fulfillment/returns skill）；**不含达人侧订单**。
---

## MCP 调用

| 项 | 固定值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `tiktokShop/developerProxy` |
| `arguments` | 直接使用本 reference 的请求对象；不得额外包裹 `body`、`data` 或另一层 `arguments` |
| 响应字段来源 | `skills/linkfox-tiktok-shop-order/SKILL.md`；只按其响应契约核对字段表 |

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

# TikTok Shop ERP 订单（Order）

本 skill 调用 TikTok Shop **卖家 ERP 订单**开放接口。统一经 LinkFox 网关：

```
linkfox-tiktok-shop-auth  →  openId（选店）
        ↓
POST tiktokShop/developerProxy
  appType = erp
  openId  = <ERP openId>     # 网关从库取 token；ttsAccessToken 已废弃
  path / method / queryString / body
        ↓
401 或 token 失效 → 网关自动 refresh 并重试一次
        ↓
TikTok Open API → 网关透传 httpStatus + body
```

> 📌 **前置依赖**：`linkfox-tiktok-shop-auth`（固定 ERP）。
> 📌 **勿手动刷新 token**：业务调用只需 `openId`；网关遇 401/过期会自动续签。
> 📌 **转发说明 + 索引**：`linkfox-tiktok-shop-order--api.md`
> 📌 **完整官方参数/响应**：`linkfox-tiktok-shop-order--apis--<api>.md`
> 📌 官方入口：[Get Order List](https://partner.tiktokshop.com/docv2/page/get-order-list-202309)

## Prerequisites

> 旧脚本调用已移除；使用本页 `MCP 调用`。
2. 本 skill **不实现**授权；也**不必**在调用前手动 `/refreshToken`。

## Core Concepts

| 概念 | 说明 |
|------|------|
| 转发入口 | 仅 `POST tiktokShop/developerProxy`，**固定 `appType=erp`** |
| path | 相对路径，如 `order/202309/orders/search`；白名单 `order/`、`authorization/` |
| shop_cipher | 来自 `get_authorized_shops`；单店也须显式传入 |
| Get Order List | 筛选条件在 **body**；分页在 **query**（`page_size`/`page_token`） |
| Get Order Detail | Query `ids`（可数组，脚本拼逗号） |

## Available Scripts

| 脚本 | 作用 |
|------|------|
| `proxy_call` | 检测 `linkfox-tiktok-shop-auth` |
| `proxy_call` | 具名 API |
| `proxy_call` | 通用 path/method |
| `proxy_call` | 取 `shop_cipher` |
| `proxy_call` | 订单列表（[202309](https://partner.tiktokshop.com/docv2/page/get-order-list-202309)） |
| `proxy_call` | 订单详情（202507，推荐） |
| `proxy_call` | 订单详情（202309） |

共享模块：`proxy_call`、`proxy_call`、`proxy_call`。

## 标准流程

1. **`linkfox-tiktok-shop-auth`** 选 ERP 店 → `openId`
2. `get_authorized_shops` → `shop_cipher`（多店必传）
3. `get_order_list` 按状态/时间筛选
4. `get_order_detail` 用返回的 order id 查详情

## Usage Examples

> 旧 HTTP/脚本示例已移除；使用本页 `MCP 调用` 的完整 `proxy_call` 参数结构。

## Display Rules

1. 勿输出完整 accessToken。
2. 列表展示订单号、状态、金额、创建/更新时间等关键字段；细节从 detail 再取。
3. 网关 `errcode=1005` → 需放行 `order/`、`authorization/`。

## Important Limitations

- **仅 ERP 订单查询**（list/detail）。
- **不含**履约拆单/发货（`fulfillment/`）→ 用 **`linkfox-tiktok-shop-fulfillment`**。
- **不含**取消/退款（`return_refund/`）— 另开 skill。
- **不含授权**。

## 积分消耗规则

不消耗积分（以网关实际为准）。

**Feedback**：`skillName` = `linkfox-tiktok-shop-order`。

---
*More skills: [LinkFox Skills](https://skill.linkfox.com/)*
