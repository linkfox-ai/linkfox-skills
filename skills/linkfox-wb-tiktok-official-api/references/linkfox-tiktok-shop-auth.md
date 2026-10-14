---
name: linkfox-tiktok-shop-auth
description: TikTok Shop ERP（小店）专用授权与管理技能，固定 appType=erp，提供 OAuth 授权、已授权 ERP 店铺查询与可选手动刷新；已入库凭证仅保留响应字段契约，不读取或展示。业务调用经 developerProxy 时授权已后台化（按 openId 选择上下文，401/过期自动刷新），一般无需手动 refresh。region 支持 global / us。当用户提到 TikTok Shop 授权、绑定 TikTok 小店、TikTok ERP 店铺授权、查询已授权 TikTok 小店、TikTok Shop ERP authorization, bind TikTok Shop, authorized TikTok shops 时触发。仅 ERP，不含联盟 affiliate 或达人/视频号 creator。
---

## MCP 调用

| 项 | 固定值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `tiktokShop/authorizeUrl`、`tiktokShop/authorizedStores`、`tiktokShop/storeTokens`、`tiktokShop/refreshToken`（按本页子能力选择） |
| `arguments` | 直接使用本 reference 的请求对象；不得额外包裹 `body`、`data` 或另一层 `arguments` |
| 响应字段来源 | `skills/linkfox-tiktok-shop-auth/SKILL.md`；只按其响应契约核对字段表 |

```json
{"toolName":"tiktokShop/authorizedStores","arguments":{"appType":"erp","region":"global"}}
```

- `toolName` 精确匹配且区分大小写；MCP 缺失时停止，禁止 HTTP fallback。
- WorkBuddy 自动注入 MCP Authorization；不得传 LinkFox `headers`、API Key、`token`、JWT 或手机号。
- 收费失败、空结果或结果不理想时不自动重试；相同 `toolName + arguments` 在同一任务内不重复调用。
- 先处理 MCP/schema/`isError`；text JSON 只解析一次；再检查下游错误字段和业务结果。

# TikTok Shop ERP 授权与权限管理

本 skill **仅负责 TikTok Shop ERP（小店）** 的 OAuth 授权、已授权店铺列表，以及可选的令牌查询/手动刷新。是后续通过 `tiktokShop/developerProxy`（`appType=erp`）调用 TikTok Shop 开放接口的前置依赖（业务侧只需 `openId`）。底层经 LinkFox 网关对接紫鸟开放平台代理。

> 🔒 **固定 `appType=erp`**。脚本会强制写入 `erp`；传入 `affiliate` / `creator` 将拒绝。联盟授权、达人授权均不在本 skill 范围。

> ⚠️ **达人/视频号授权**请用 **`linkfox-tiktok-video-auth`**（`/tiktokVideo`）。

> 📌 **业务接口不在本 skill**：商品、订单、履约、财务等按功能拆成独立 ERP 业务 skill（均依赖本 skill 选店拿 `openId`），经 `tiktokShop/developerProxy` 调用。

## ERP Skill 套件（按功能切换）

| Skill | 职责 |
|-------|------|
| **`linkfox-tiktok-shop-auth`**（本 skill） | ERP 授权 + 选店（+ 可选令牌查询/手动刷新） |
| **`linkfox-tiktok-shop-product`** | ERP 商品：刊登检查、类目、创建/编辑、上下架、价库 |
| **`linkfox-tiktok-shop-order`** | ERP 订单：订单列表、订单详情 |
| **`linkfox-tiktok-shop-fulfillment`** | ERP 履约：拆单属性（后续可扩发货/包裹） |
| **`linkfox-tiktok-shop-logistics`** | ERP 物流：仓库列表（后续可扩配送选项等） |
| **`linkfox-tiktok-shop-return-refund`** | ERP 售后：拒退/拒取消原因 |
| **`linkfox-tiktok-shop-analytics`** | ERP 分析：店铺视频表现 |
| `linkfox-tiktok-shop-*`（规划中） | finance 等 |

Agent 按用户意图切换 skill：先本 skill 拿到 `openId`，再进对应业务 skill（**不必**再取/刷新 accessToken）。

## Core Concepts

**授权流程**：生成授权 URL → 用户浏览器完成 TikTok Shop 授权 → 紫鸟回调推送 Token → 按 `state` 落库。授权 URL 约 1 小时有效。

**店铺标识**：以卖家 `openId` 标识；本 skill 一律按 **`appType=erp`** 查询/刷新令牌。

**令牌生命周期（后台化）**：

- `tiktokShop/developerProxy` 按 `openId + appType` 从库取 `accessToken`；`ttsAccessToken` 字段**已废弃**（传入也会被忽略）。
- 上游返回 **HTTP 401** 或 body 含 token expired/invalid 时，网关**自动 refresh 一次并重试**，同时回写库中的 accessToken / refreshToken / 过期时间。
- **无**按 `accessTokenExpireIn` 提前刷新，也**无**定时刷新任务；`/storeTokens` 只读库，不校验过期。
- 业务 skill **不要**在调用前手动 `/refreshToken`。手动刷新仅用于排查或用户明确要求。
- `refreshToken` 本身过期 → 须重新授权。

## Data Fields

### Authorization URL Response

| Field | Type | Description |
|-------|------|-------------|
| authorizeUrl | string | TikTok Shop ERP 授权链接（约 1 小时有效） |

### Authorized Store Item（本 skill 仅展示 erp）

| Field | Type | Description |
|-------|------|-------------|
| openId | string | 卖家唯一标识 |
| sellerName | string | 店铺名称 |
| sellerBaseRegion | string | 店铺所在区域（如 ID） |
| appType | string | 固定为 `erp` |
| region | string | `global` / `us` |

### Store Tokens

| Field | Type | Description |
|-------|------|-------------|
| accessToken | string | 调用 TikTok Shop ERP 开放接口的凭证 |
| refreshToken | string | 续签用 |
| accessTokenExpireIn | integer | accessToken 过期 Unix 时间戳 |
| refreshTokenExpireIn | integer | refreshToken 过期 Unix 时间戳 |

## Supported Regions

| region | 说明 |
|--------|------|
| global | 全球（默认） |
| us | 美国站 |

`appType` **固定为 `erp`**，不可选。

## API Usage

详见 `linkfox-tiktok-shop-auth--api.md`。

### Available Scripts

- `proxy_call` — 生成 ERP 授权 URL（可选 `shopName` / `region`；强制 `appType=erp`）
- `proxy_call` — 列出已授权店铺，**仅返回 `appType=erp`**
- `proxy_call` — `storeTokens` 响应契约归档；不得为读取或展示凭证而调用，业务调用不需要
- `proxy_call` — （可选）手动刷新 ERP access_token；**业务调用不需要**（proxy 会自动刷新）

## Usage Scenarios

### Scenario 1: Authorize New ERP Shop

1. 确认 `region`（美国站 `us`，否则默认 `global`）。可选 `shopName`。
2. 调用 `tiktokShop/authorizeUrl`（`appType=erp`）。
3. 把 `authorizeUrl` 给用户浏览器打开（约 1 小时有效）。
4. 授权完成后可选调 `authorized_stores` 确认。

### Scenario 2: List ERP Shops

调用 `tiktokShop/authorizedStores`，只展示 `appType=erp` 店铺。

### Scenario 3: Manual Refresh Token（可选）

仅当用户**明确要求**手动刷新，或排查令牌问题时使用。传入 `openId`（调用固定 `appType=erp`）。日常业务调用**不要**先刷新——`developerProxy` 遇 401/过期会自动 refresh 并重试。`refreshToken` 过期则重新授权。

### Scenario 4: Store Tokens Contract

`storeTokens` 仅保留 endpoint 与响应字段契约。不得为读取、展示、保存或转发凭证而调用；ERP 业务只使用 `openId` 选择后台授权上下文。

### Scenario 5: Prepare for ERP Business Skill

1. `authorized_stores` 选店 → 得到 `openId`
2. 切换到对应 `linkfox-tiktok-shop-*` 业务 skill，脚本只传 `openId`（token 由网关解析）

## Display Rules

1. 只呈现授权状态与非凭证店铺数据，不做业务建议。
2. 响应字段表中的凭证字段仅用于契约记录，不得读取后展示、保存或转发。
3. 授权链接须说明约 1 小时失效。
4. 过期字段为绝对 Unix 时间戳；业务侧勿据此主动 refresh。
5. 用户提到达人/视频号/联盟授权时，**勿用本 skill**。

## Important Limitations

- **仅 ERP**：拒绝 `affiliate` / `creator`。
- **不含业务 API**：商品/订单等进对应 shop 业务 skill。
- **达人授权** → `linkfox-tiktok-video-auth`。
- 授权链接约 1 小时有效；用户只能管理自己的店铺。
- 无提前/定时刷新；依赖 developerProxy 被动刷新。

## User Expression & Scenario Quick Reference

**Applicable**：

| User Says | Scenario |
|-----------|----------|
| "授权我的 TikTok Shop / 小店 / ERP" | ERP 新店授权 |
| "看看已授权的 TikTok 小店" | 列 ERP 店铺 |
| "TikTok 小店令牌过期了" | 优先：直接重试业务 API（proxy 自动 refresh）；仅用户坚持手动时用 Scenario 3 |
| "获取某 TikTok 小店访问令牌" | 不展示或导出凭证；说明 ERP 业务仅需 `openId`，授权异常按 onboarding 处理 |

**Not applicable**：

| User Says | 应使用 |
|-----------|--------|
| 达人/视频号授权 | `linkfox-tiktok-video-auth` |
| 联盟 affiliate 授权 | 不在本 skill（当前未提供专用 skill） |
| 拉取 TikTok Shop 商品 / 订单 / 履约 / 仓库 / 售后 / 分析等业务数据 | 对应 `linkfox-tiktok-shop-*`（商品 **product**，订单 **order**，履约 **fulfillment**，仓库 **logistics**，售后 **return-refund**，分析 **analytics**） |

## Quick Reference

| API | Path | Purpose |
|-----|------|---------|
| Get Authorization URL | tiktokShop/authorizeUrl | 生成 ERP 授权链接 |
| List Authorized Stores | tiktokShop/authorizedStores | 店铺列表（本 skill 过滤 erp） |
| Query Store Tokens | tiktokShop/storeTokens | 仅保留响应契约；不得用于读取或展示凭证 |
| Refresh Token | tiktokShop/refreshToken | （可选）手动刷新；日常业务不需要 |

**Feedback**：见 `linkfox-tiktok-shop-auth--api.md`，`skillName`：`linkfox-tiktok-shop-auth`。

<!-- LF_LARGE_RESPONSE_BLOCK -->
## Handling Large Responses

```
> 旧脚本调用已移除；使用本页 `MCP 调用`。
> 旧脚本调用已移除；使用本页 `MCP 调用`。
```

> Pick `--out-dir` outside any git working tree. Persisted responses may contain auth-sensitive data — do not commit them.

> Entry scripts: `proxy_call`, `proxy_call`, `proxy_call`, `proxy_call`.
<!-- /LF_LARGE_RESPONSE_BLOCK -->

---
*For more skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
