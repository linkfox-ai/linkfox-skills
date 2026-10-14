---
name: linkfox-tiktok-shop-return-refund
description: TikTok Shop ERP 售后（Return & Refund）业务技能，经 tiktokShop/developerProxy（appType=erp）转发 Return Refund Open API：获取拒退/拒取消原因（Get Reject Reasons）。依赖 linkfox-tiktok-shop-auth 选店（传 openId；token 后台化，勿手动 refresh）。当用户提到 TikTok 拒退原因、拒绝退款原因、拒绝取消原因、Get Reject Reasons、reject_reasons、return_or_cancel_id、售后拒因列表 时触发。**不含授权**；**不含订单查询**（用 shop-order）；同意/拒绝退货等写操作可后续扩展本 skill。
---

## MCP 调用

| 项 | 固定值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `tiktokShop/developerProxy` |
| `arguments` | 直接使用本 reference 的请求对象；不得额外包裹 `body`、`data` 或另一层 `arguments` |
| 响应字段来源 | `skills/linkfox-tiktok-shop-return-refund/SKILL.md`；只按其响应契约核对字段表 |

```json
{
  "toolName": "tiktokShop/developerProxy",
  "arguments": {"appType": "erp", "openId": "<openId>", "path": "return_refund/202309/reject_reasons", "method": "GET"}
}
```

- `toolName` 精确匹配且区分大小写；MCP 缺失时停止，禁止 HTTP fallback。
- WorkBuddy 自动注入 MCP Authorization；不得传 LinkFox `headers`、API Key、`token`、JWT 或手机号。
- 收费失败、空结果或结果不理想时不自动重试；相同 `toolName + arguments` 在同一任务内不重复调用。
- 先处理 MCP/schema/`isError`；text JSON 只解析一次；再检查下游错误字段和业务结果。

# TikTok Shop ERP 售后（Return & Refund）

本 skill 调用 TikTok Shop **卖家 ERP 售后**开放接口。统一经 LinkFox 网关：

```
linkfox-tiktok-shop-auth  →  openId（选店）
        ↓
POST tiktokShop/developerProxy
  appType = erp
  openId  = <ERP openId>
  path / method / queryString
        ↓
401 或 token 失效 → 网关自动 refresh 并重试一次
```

> 📌 **前置依赖**：`linkfox-tiktok-shop-auth`
> 📌 **勿手动刷新 token**
> 📌 官方入口：[Get Reject Reasons](https://partner.tiktokshop.com/docv2/page/get-reject-reasons-202309)
> 📌 完整参考：`linkfox-tiktok-shop-return-refund--apis--<api>.md`

## Prerequisites

> 旧脚本调用已移除；使用本页 `MCP 调用`。
2. 需要有效的 `return_or_cancel_id`（退货单或取消单 ID）。

## Core Concepts

| 概念 | 说明 |
|------|------|
| path 白名单 | `return_refund/`、`authorization/` |
| Get Reject Reasons | Query：`return_or_cancel_id`（必填）+ `shop_cipher`；可选 `locale` |
| 用途 | 拒绝退货/取消前，先拉可选拒因列表 |

## Available Scripts

| 脚本 | 作用 |
|------|------|
| `proxy_call` | 检测 auth skill |
| `proxy_call` | 具名 API |
| `proxy_call` | 通用 path/method |
| `proxy_call` | 取 `shop_cipher` |
| `proxy_call` | 拒因列表 |

## Usage Examples

> 旧 HTTP/脚本示例已移除；使用本页 `MCP 调用` 的完整 `proxy_call` 参数结构。

## Important Limitations

- 当前以 **Get Reject Reasons** 为主；搜索退货/同意拒绝等可后续扩展。
- 不含订单 list/detail（`linkfox-tiktok-shop-order`）。

**Feedback**：`skillName` = `linkfox-tiktok-shop-return-refund`。
