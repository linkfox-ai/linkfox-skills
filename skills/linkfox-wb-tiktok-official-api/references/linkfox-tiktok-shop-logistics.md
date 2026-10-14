---
name: linkfox-tiktok-shop-logistics
description: TikTok Shop ERP 物流/仓库（Logistics）业务技能，经 tiktokShop/developerProxy（appType=erp）转发 Logistics Open API：获取仓库列表（Get Warehouse List）。依赖 linkfox-tiktok-shop-auth 选店（传 openId；token 后台化，勿手动 refresh）。当用户提到 TikTok 小店仓库、仓库列表、Get Warehouse List、warehouse_id、销售仓/退货仓、多仓、logistics/warehouses、查店铺仓库 时触发。**不含授权**（用 linkfox-tiktok-shop-auth）；**不含订单/履约发货**（用 shop-order / shop-fulfillment）；运费模板/配送选项等可后续扩展本 skill。
---

## MCP 调用

| 项 | 固定值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `tiktokShop/developerProxy` |
| `arguments` | 直接使用本 reference 的请求对象；不得额外包裹 `body`、`data` 或另一层 `arguments` |
| 响应字段来源 | `skills/linkfox-tiktok-shop-logistics/SKILL.md`；只按其响应契约核对字段表 |

```json
{
  "toolName": "tiktokShop/developerProxy",
  "arguments": {"appType": "erp", "openId": "<openId>", "path": "logistics/202309/warehouses", "method": "GET"}
}
```

- `toolName` 精确匹配且区分大小写；MCP 缺失时停止，禁止 HTTP fallback。
- WorkBuddy 自动注入 MCP Authorization；不得传 LinkFox `headers`、API Key、`token`、JWT 或手机号。
- 收费失败、空结果或结果不理想时不自动重试；相同 `toolName + arguments` 在同一任务内不重复调用。
- 先处理 MCP/schema/`isError`；text JSON 只解析一次；再检查下游错误字段和业务结果。

# TikTok Shop ERP 物流/仓库（Logistics）

本 skill 调用 TikTok Shop **卖家 ERP 物流仓库**开放接口。统一经 LinkFox 网关：

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
> 📌 **转发说明 + 索引**：`linkfox-tiktok-shop-logistics--api.md`
> 📌 **完整官方参数/响应**：`linkfox-tiktok-shop-logistics--apis--<api>.md`
> 📌 官方入口：[Get Warehouse List](https://partner.tiktokshop.com/docv2/page/get-warehouse-list-202309)

## Prerequisites

> 旧脚本调用已移除；使用本页 `MCP 调用`。
2. 本 skill **不实现**授权；也**不必**在调用前手动 `/refreshToken`。

## Core Concepts

| 概念 | 说明 |
|------|------|
| 转发入口 | 仅 `POST tiktokShop/developerProxy`，**固定 `appType=erp`** |
| path | 相对路径，如 `logistics/202309/warehouses`；白名单 `logistics/`、`authorization/` |
| shop_cipher | 来自 `get_authorized_shops`；单店也须显式传入 |
| Get Warehouse List | 仅需 `shop_cipher`（Query）；返回仓库 id/name/type/address 等 |
| warehouse_id | 创建商品库存、改库存、多仓场景常用 |

## Available Scripts

| 脚本 | 作用 |
|------|------|
| `proxy_call` | 检测 `linkfox-tiktok-shop-auth` |
| `proxy_call` | 具名 API |
| `proxy_call` | 通用 path/method |
| `proxy_call` | 取 `shop_cipher` |
| `proxy_call` | 仓库列表（[202309](https://partner.tiktokshop.com/docv2/page/get-warehouse-list-202309)） |

共享模块：`proxy_call`、`proxy_call`、`proxy_call`。

## 标准流程

1. **`linkfox-tiktok-shop-auth`** 选 ERP 店 → `openId`
2. `get_authorized_shops` → `shop_cipher`（多店必传）
3. `get_warehouse_list` 拿到 `warehouse_id`（以及 type / effect_status / is_default 等）
4. 下游刊登/改库存使用对应 `warehouse_id`（见 `linkfox-tiktok-shop-product`）

## Usage Examples

> 旧 HTTP/脚本示例已移除；使用本页 `MCP 调用` 的完整 `proxy_call` 参数结构。

## Display Rules

1. 勿输出完整 accessToken。
2. 列表优先展示：`id`、`name`、`type`、`sub_type`、`effect_status`、`is_default`、地址摘要。
3. 网关 `errcode=1005` → 需放行 `logistics/`、`authorization/`。

## Important Limitations

- **仅 ERP 物流仓库域**（当前以仓库列表为主；配送选项/运费模板可后续扩展）。
- **不含**订单 list/detail（`linkfox-tiktok-shop-order`）。
- **不含**履约拆单/发货（`linkfox-tiktok-shop-fulfillment`）。
- **不含授权**。

## 积分消耗规则

不消耗积分（以网关实际为准）。

**Feedback**：`skillName` = `linkfox-tiktok-shop-logistics`。

---
*More skills: [LinkFox Skills](https://skill.linkfox.com/)*
