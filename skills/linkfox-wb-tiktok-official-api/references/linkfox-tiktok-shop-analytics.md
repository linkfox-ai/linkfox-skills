---
name: linkfox-tiktok-shop-analytics
description: TikTok Shop ERP 数据分析（Analytics）业务技能，经 tiktokShop/developerProxy（appType=erp）转发 Analytics Open API：获取店铺视频表现（Get Video Performances）。依赖 linkfox-tiktok-shop-auth 选店（传 openId；token 后台化，勿手动 refresh）。当用户提到 TikTok 视频表现、店铺视频数据、视频 GMV、Get Video Performances、shop_videos/performance、视频销量/浏览量分析、analytics video 时触发。**不含授权**；**不含达人侧视频发布**（用 linkfox-tiktok-video）；商品/店铺绩效等可后续扩展本 skill。
---

## MCP 调用

| 项 | 固定值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `tiktokShop/developerProxy` |
| `arguments` | 直接使用本 reference 的请求对象；不得额外包裹 `body`、`data` 或另一层 `arguments` |
| 响应字段来源 | `skills/linkfox-tiktok-shop-analytics/SKILL.md`；只按其响应契约核对字段表 |

```json
{
  "toolName": "tiktokShop/developerProxy",
  "arguments": {"appType": "erp", "openId": "<openId>", "path": "analytics/202403/shop_videos/performance", "method": "GET"}
}
```

- `toolName` 精确匹配且区分大小写；MCP 缺失时停止，禁止 HTTP fallback。
- WorkBuddy 自动注入 MCP Authorization；不得传 LinkFox `headers`、API Key、`token`、JWT 或手机号。
- 收费失败、空结果或结果不理想时不自动重试；相同 `toolName + arguments` 在同一任务内不重复调用。
- 先处理 MCP/schema/`isError`；text JSON 只解析一次；再检查下游错误字段和业务结果。

# TikTok Shop ERP 数据分析（Analytics）

本 skill 调用 TikTok Shop **卖家 ERP 分析**开放接口。统一经 LinkFox 网关：

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
> 📌 官方入口：[Get Video Performances](https://partner.tiktokshop.com/docv2/page/get-video-performances-202403)
> 📌 完整参考：`linkfox-tiktok-shop-analytics--apis--<api>.md`

## Prerequisites

> 旧脚本调用已移除；使用本页 `MCP 调用`。
2. 需要时间范围：`start_date` / `end_date`（通常 `YYYYMMDD`）。

## Core Concepts

| 概念 | 说明 |
|------|------|
| path 白名单 | `analytics/`、`authorization/` |
| Get Video Performances | `GET analytics/202403/shop_videos/performance` |
| 时间窗 | Query：`start_date`、`end_date`（必填） |
| 分页 | `page_size` / `page_token` |

## Available Scripts

| 脚本 | 作用 |
|------|------|
| `proxy_call` | 检测 auth skill |
| `proxy_call` | 具名 API |
| `proxy_call` | 通用 path/method |
| `proxy_call` | 取 `shop_cipher` |
| `proxy_call` | 视频表现列表 |

## Usage Examples

> 旧 HTTP/脚本示例已移除；使用本页 `MCP 调用` 的完整 `proxy_call` 参数结构。

## Important Limitations

- 当前以 **Get Video Performances（202403）** 为主；单视频详情/商品绩效等可后续扩展。
- 不含达人可购物视频发布（`linkfox-tiktok-video`）。

**Feedback**：`skillName` = `linkfox-tiktok-shop-analytics`。
