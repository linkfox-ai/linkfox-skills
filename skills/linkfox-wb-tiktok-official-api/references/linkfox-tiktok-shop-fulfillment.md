---
name: linkfox-tiktok-shop-fulfillment
description: TikTok Shop ERP 履约（Fulfillment）业务技能，经 tiktokShop/developerProxy（appType=erp）转发 Fulfillment Open API：查询订单拆单属性（Get Order Split Attributes）。依赖 linkfox-tiktok-shop-auth 选店（传 openId；token 后台化，勿手动 refresh）。当用户提到 TikTok 小店拆单、订单能否拆分、拆单属性、must_split、can_split、Get Order Split Attributes、split_attributes、订单拆包裹、TikTok Shop fulfillment split 时触发。**不含授权**（用 linkfox-tiktok-shop-auth）；**不含订单列表/详情**（用 linkfox-tiktok-shop-order）；发货/包裹后续可继续扩展本 skill。
---

## MCP 调用

| 项 | 固定值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `tiktokShop/developerProxy` |
| `arguments` | 直接使用本 reference 的请求对象；不得额外包裹 `body`、`data` 或另一层 `arguments` |
| 响应字段来源 | `skills/linkfox-tiktok-shop-fulfillment/SKILL.md`；只按其响应契约核对字段表 |

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

# TikTok Shop ERP 履约（Fulfillment）

本 skill 调用 TikTok Shop **卖家 ERP 履约**开放接口。统一经 LinkFox 网关：

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
> 📌 **转发说明 + 索引**：`linkfox-tiktok-shop-fulfillment--api.md`
> 📌 **完整官方参数/响应**：`linkfox-tiktok-shop-fulfillment--apis--<api>.md`
> 📌 官方入口：[Get Order Split Attributes](https://partner.tiktokshop.com/docv2/page/get-order-split-attributes-202309)

## Prerequisites

> 旧脚本调用已移除；使用本页 `MCP 调用`。
2. 本 skill **不实现**授权；也**不必**在调用前手动 `/refreshToken`。
3. 查订单号请用 **`linkfox-tiktok-shop-order`**，再对本 skill 传 `order_ids`。

## Core Concepts

| 概念 | 说明 |
|------|------|
| 转发入口 | 仅 `POST tiktokShop/developerProxy`，**固定 `appType=erp`** |
| path | 相对路径，如 `fulfillment/202309/orders/split_attributes`；白名单 `fulfillment/`、`authorization/` |
| shop_cipher | 来自 `get_authorized_shops`；单店也须显式传入 |
| Get Order Split Attributes | Query `order_ids`（可数组，脚本拼逗号）+ `shop_cipher` |
| 与订单 skill 分工 | list/detail → `shop-order`；拆单属性/履约 → 本 skill |

## Available Scripts

| 脚本 | 作用 |
|------|------|
| `proxy_call` | 检测 `linkfox-tiktok-shop-auth` |
| `proxy_call` | 具名 API |
| `proxy_call` | 通用 path/method |
| `proxy_call` | 取 `shop_cipher` |
| `proxy_call` | 拆单属性（[202309](https://partner.tiktokshop.com/docv2/page/get-order-split-attributes-202309)） |

共享模块：`proxy_call`、`proxy_call`、`proxy_call`。

## 标准流程

1. **`linkfox-tiktok-shop-auth`** 选 ERP 店 → `openId`
2. （可选）**`linkfox-tiktok-shop-order`** 查到目标订单号
3. `get_authorized_shops` → `shop_cipher`（多店必传）
4. `get_order_split_attributes` 传入 `order_ids`，查看 `can_split` / `must_split` 等

## Usage Examples

> 旧 HTTP/脚本示例已移除；使用本页 `MCP 调用` 的完整 `proxy_call` 参数结构。

## Display Rules

1. 勿输出完整 accessToken。
2. 优先展示每个 `order_id` 的 `can_split` / `must_split` / `reason` / `must_split_reasons`。
3. 网关 `errcode=1005` → 需放行 `fulfillment/`、`authorization/`。

## Important Limitations

- **仅 ERP 履约域**（当前以拆单属性为主；发货/包裹后续扩展）。
- **不含**订单 list/detail（用 `linkfox-tiktok-shop-order`）。
- **不含**取消/退款（`return_refund/`）。
- **不含授权**。

## 积分消耗规则

不消耗积分（以网关实际为准）。

**Feedback**：`skillName` = `linkfox-tiktok-shop-fulfillment`。

---
*More skills: [LinkFox Skills](https://skill.linkfox.com/)*
