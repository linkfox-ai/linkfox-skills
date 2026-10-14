---
name: linkfox-tiktok-shop-product
description: TikTok Shop ERP 商品（Product）业务技能，经 tiktokShop/developerProxy（appType=erp）转发 TikTok Product Open API：刊登前置检查、授权店铺 cipher、类目/属性/品牌、搜索/创建/编辑商品、刊登校验、上下架、改价改库存、删除恢复。依赖 linkfox-tiktok-shop-auth 选店（传 openId；token 后台化，勿手动 refresh）。当用户提到 TikTok 小店商品、ERP 商品、刊登前置条件、check listing prerequisites、创建商品、编辑商品、搜索商品、上架下架、改价、改库存、类目属性、品牌、product listing、TikTok Shop product API 时触发。**不含授权**（用 linkfox-tiktok-shop-auth）；**不含达人/视频号商品**（用 linkfox-tiktok-video-products）。
---

## MCP 调用

| 项 | 固定值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `tiktokShop/developerProxy` |
| `arguments` | 直接使用本 reference 的请求对象；不得额外包裹 `body`、`data` 或另一层 `arguments` |
| 响应字段来源 | `skills/linkfox-tiktok-shop-product/SKILL.md`；只按其响应契约核对字段表 |

```json
{
  "toolName": "tiktokShop/developerProxy",
  "arguments": {"appType": "erp", "openId": "<openId>", "path": "product/202312/prerequisites", "method": "GET"}
}
```

- `toolName` 精确匹配且区分大小写；MCP 缺失时停止，禁止 HTTP fallback。
- WorkBuddy 自动注入 MCP Authorization；不得传 LinkFox `headers`、API Key、`token`、JWT 或手机号。
- 收费失败、空结果或结果不理想时不自动重试；相同 `toolName + arguments` 在同一任务内不重复调用。
- 先处理 MCP/schema/`isError`；text JSON 只解析一次；再检查下游错误字段和业务结果。

# TikTok Shop ERP 商品（Product）

本 skill 调用 TikTok Shop **卖家 ERP 商品**开放接口。统一经 LinkFox 网关：

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

> 📌 **前置依赖**：`linkfox-tiktok-shop-auth`（固定 ERP）。勿用 `linkfox-tiktok-video-auth`。
> 📌 **勿手动刷新 token**：业务调用只需 `openId`；网关遇 401/过期会自动续签。
> 📌 **转发说明 + 接口索引**：`linkfox-tiktok-shop-product--api.md`
> 📌 **每个接口的完整官方参数/响应/错误码**：`linkfox-tiktok-shop-product--apis--<api>.md`（已收录 Partner Center 原文 + LinkFox 映射）

## Prerequisites

> 旧脚本调用已移除；使用本页 `MCP 调用`。
2. 本 skill **不实现**授权；也**不必**在调用前手动 `/refreshToken`。

## Core Concepts

| 概念 | 说明 |
|------|------|
| 转发入口 | 仅 `POST tiktokShop/developerProxy`，**固定 `appType=erp`** |
| path | 相对路径，如 `product/202312/prerequisites`；白名单前缀 `product/`、`authorization/` |
| shop_cipher | 来自 `get_authorized_shops` 的 `data.shops[].cipher`；必须显式传入；可先调用 Get Authorized Shops 取得 |
| 签名 | 调用方**不要**传 `app_key`/`sign`/`timestamp`（紫鸟注入） |
| 响应 | 先看网关 `developerProxy.httpStatus`，再解析 `body` 内 TikTok `code`/`message` |

## 调用入口与本地辅助

| 入口 | 作用 |
|------|------|
| `proxy_call` | 使用 `tiktokShop/developerProxy` 执行本域已收录的商品 API；具体 `path`、`method`、Query 与 Body 见各 API reference |
| `scripts/upload_product_image.py` | 读取本地图片并生成图片上传所需的 Base64 `arguments`；不联网、不读取凭证 |
| `scripts/_product_endpoints.py` | 本地 endpoint 与参数校验元数据；不发起网关请求 |

## 标准流程

1. **`linkfox-tiktok-shop-auth`**：`authorized_stores` 选 ERP 店 → 得到 `openId`
2. （推荐）`get_authorized_shops` → 拿到 `shop_cipher`（多店必须显式传）
3. （推荐）`check_listing_prerequisites` → 全部 `is_failed=false` 再刊登
4. 类目/属性/品牌 → `create_product` / `check_product_listing` → `activate_product`
5. 日常：`search_products` / `update_price` / `update_inventory` / 上下架

## Usage Examples

> 旧 HTTP/脚本示例已移除；使用本页 `MCP 调用` 的完整 `proxy_call` 参数结构。

## Display Rules

1. 勿输出完整 `accessToken` / 完整 `shop_cipher` 以外的敏感信息时可掩码 token。
2. 展示 `check_results` 时逐条说明 `check_item` + `fail_reasons`。
3. 网关 `errcode=1005` → path 未白名单，联系运维放行 `product/`、`authorization/`。

## Important Limitations

- **仅 ERP**：`appType` 固定 erp。
- **不含授权**；达人橱窗选品用 `linkfox-tiktok-video-products`。
- **图片上传**：`upload_product_image` 可调用。脚本读取本地图片并以 `multipartFileBase64` 发送 JSON 给网关；网关解码后构造 TikTok 所需的 `multipart/form-data`（文件字段 `data`）。上传成功后使用返回的 `data.uri` 创建或编辑商品。不要把 Base64 放进普通 `body`。
- **通用文件上传**：`upload_product_file` 尚未纳入可调用脚本。
- **Global Product** 跨境全球商品第二期再加。

## 积分消耗规则

不消耗积分（以网关实际计费为准；若返回积分不足按 onboarding 处理）。

**Feedback**：`skillName` = `linkfox-tiktok-shop-product`（见 `linkfox-tiktok-shop-product--api.md`）。

---
*More skills: [LinkFox Skills](https://skill.linkfox.com/)*
