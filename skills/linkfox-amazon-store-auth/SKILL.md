---
name: linkfox-amazon-store-auth
description: 亚马逊店铺授权与管理技能，提供完整的授权流程、令牌刷新、已授权店铺查询以及访问令牌获取能力。获取授权链接时店铺名 sellerName 为必填，用于区分已授权店铺。当用户提到亚马逊店铺授权、绑定亚马逊店铺、刷新令牌、查询店铺令牌、管理授权店铺、Amazon seller authorization, bind Amazon seller account, refresh access token, query store tokens, manage authorized stores时触发此技能。只要其需求涉及亚马逊卖家账号授权、访问令牌管理或店铺列表查询，也应触发此技能。
---

# Amazon 店铺授权与管理

本 skill 负责 **亚马逊卖家店铺的 OAuth 授权、已授权店铺列表、访问令牌获取与刷新**，是拉取报告、查询库存、同步订单等所有下游操作的前置依赖。

> 📌 **Related skill**：如果用户需要 **拉取亚马逊店铺报告**（库存 / 订单 / 销售 / 财务报告等），请切换到 `linkfox-amazon-store-report`。该 skill 依赖本 skill 提供的授权与令牌能力。

## Core Concepts

Selling Partner API 是亚马逊为卖家提供的官方接口。本 skill 负责 OAuth 2.0 授权流程与令牌生命周期管理：

**授权流程**：生成授权 URL → 用户在 Amazon 完成授权 → Amazon 回调并附带授权码 → 系统用授权码换取令牌 → 令牌安全保存。

**店铺名（`sellerName`）必填**：调用 `/spApi/authorizeUrl` 前**必须**向用户询问并获取一个清晰、非空的店铺名。它用来在"已授权店铺列表"中标记该账号；不要留空或使用空白字符串。

**令牌生命周期**：`accessToken` 通常 1 小时过期；`refreshToken` 用于在不重新授权的前提下续签新的 `accessToken`。

## Data Fields

### Authorization URL Response

| Field | Type | Description |
|-------|------|-------------|
| authorizeUrl | string | 让用户在浏览器打开的 Amazon 授权链接 |

### Authorized Store Item

| Field | Type | Description |
|-------|------|-------------|
| sellerId | string | Amazon Seller ID (Merchant ID) |
| sellerName | string | 店铺名（授权时必填） |
| region | string | 市场区域代码 NA / EU / FE |

### Store Tokens

| Field | Type | Description |
|-------|------|-------------|
| accessToken | string | 调用亚马逊开放接口的凭证 |
| refreshToken | string | 用于续签 accessToken |
| expiresIn | integer | accessToken 过期秒数 |
| tokenType | string | 通常为 "bearer" |

## Supported Regions

| Code | Name | Marketplaces |
|------|------|--------------|
| NA | 北美 | 美国、加拿大、墨西哥 |
| EU | 欧洲 | 英国、德国、法国、意大利、西班牙、荷兰等 |
| FE | 远东 | 日本、澳大利亚、新加坡、印度 |

默认区域为 **NA**。当用户未指定区域时，使用 NA。

## API Usage

本 skill 经 LinkFox 网关调用店铺授权相关接口，详见 `references/api.md`。

### Available Scripts

- `scripts/authorize_url.py` — 为新店铺生成授权 URL（`sellerName` 必填）
- `scripts/authorized_stores.py` — 列出所有已授权店铺
- `scripts/refresh_token.py` — 刷新某店铺的访问令牌
- `scripts/store_tokens.py` — 查询某店铺的访问令牌（供下游 skill 使用）

## Usage Scenarios

### Scenario 1: Authorize New Store

**User request**：「我要授权我的亚马逊北美站点」

**Steps**：
1. **询问店铺名 `sellerName`**（若用户未提供）。`/spApi/authorizeUrl` 要求 `sellerName` 为非空字符串；向用户说明这只是在 LinkFox 里识别店铺的标签，建议与 Seller Central 后台名字保持一致。
2. 调用 `/spApi/authorizeUrl`，传入 `region` 与 `sellerName`
3. 把返回的 `authorizeUrl` 给用户，让其在浏览器中打开
4. 用户在 Amazon 完成授权 → Amazon 回调系统 → 系统自动保存授权
5. 可选：调用 `/spApi/authorizedStores` 确认授权成功

### Scenario 2: View Authorized Stores

**User request**：「列一下我已授权的亚马逊店铺」

**Steps**：
1. 调用 `/spApi/authorizedStores`
2. 展示店铺列表（sellerName / sellerId / region）
3. 按 sellerId、region 排序

### Scenario 3: Refresh Expired Token

**User request**：「我店铺的令牌过期了，帮我刷新」

**Steps**：
1. 调用 `/spApi/refreshToken`，传入 `sellerId`（可选 `region`）
2. 返回新的 `accessToken` / `refreshToken`
3. 数据库自动更新令牌信息

### Scenario 4: Query Store Tokens

**User request**：「获取北美站点 A123 店铺的访问令牌」

**Steps**：
1. 调用 `/spApi/storeTokens`，传入 `sellerId` 与 `region`
2. 返回全部令牌信息（供下游业务调用）

### Scenario 5: Prepare Tokens for Any Store Operation (Standard Preparation Workflow)

当用户提出任何涉及卖家后台数据的请求（拉报告、查库存、看订单等），**本 skill 负责前置的"选店 → 取令牌"流程**，具体业务由相应的下游 skill 接手。

**Steps**：
1. **列出已授权店铺**：调用 `/spApi/authorizedStores`
2. **让用户选择店铺**：如果有多家店铺，请用户明确选哪一家
3. **获取该店铺令牌**：调用 `/spApi/storeTokens`，传入所选店铺的 `sellerId` 与 `region`
4. **把 `accessToken` 交给下游 skill**（例如 `linkfox-amazon-store-report`）执行具体操作

**Why this workflow is critical**：
- 用户可能同时授权了多家不同区域的店铺
- 每家店铺的令牌与权限彼此独立
- 调用必须使用与店铺匹配的令牌，跳过"选店"会导致歧义和错误

## Display Rules

1. **先有店铺名再生成授权链接**：若用户未提供 `sellerName`，**必须先问**，不允许带空值调用 `/spApi/authorizeUrl`。
2. **只呈现数据**：展示授权结果、店铺列表、令牌信息即可，不做业务建议。
3. **安全意识**：不要明文显示完整的 `accessToken`/`refreshToken`，只展示前 10 个字符等掩码形式。
4. **清晰引导**：返回授权链接时，明确告知用户在浏览器中打开并完成授权。
5. **错误说明**：授权失败时，基于错误码解释原因并给出建议。
6. **成功确认**：授权完成后与用户确认，可选择展示该店铺基本信息。

## Important Limitations

- **sellerName 必填**：`/spApi/authorizeUrl` 必须传入非空 `sellerName`；脚本与 agent 在调用前务必校验。
- **令牌有效期**：`accessToken` 1 小时过期，需及时刷新。
- **区域专属**：每次店铺授权都与具体区域绑定，不同区域需分别授权。
- **用户隔离**：用户只能查看/管理自己授权的店铺。
- **回调白名单**：系统回调 URL 必须在授权方（紫鸟）处加白名单。

## User Expression & Scenario Quick Reference

**Applicable** — 授权与令牌管理场景：

| User Says | Scenario |
|-----------|----------|
| "授权我的亚马逊店铺" / "Authorize my Amazon store" | 新店铺授权 |
| "看看已授权的亚马逊店铺" / "Show my authorized stores" | 列出已授权店铺 |
| "令牌过期了" / "My token expired" | 刷新令牌 |
| "获取 XXX 店铺的访问令牌" / "Get access token for store" | 查询店铺令牌 |
| "绑定我的亚马逊账号" / "Connect my Amazon seller account" | 新店铺授权 |

**Not applicable** — 超出本 skill 的业务：

- **拉取亚马逊报告** → 请使用 `linkfox-amazon-store-report`
- 产品 listing 管理、订单处理、库存管理、广告投放 → 由其他 skill 负责

**Boundary judgment**：
- 本 skill 只负责「授权 + 管店铺 + 管令牌 + 为下游准备 accessToken」。
- 当用户要做具体卖家后台业务（如拉报告）时：
  1. 本 skill 执行 Scenario 5 的标准前置流程
  2. 随后切换到对应下游 skill 完成业务逻辑
- 不要直接越过本 skill 去调具体 Amazon 开放接口。

## Quick Reference

### Authorization & Token Management APIs

| API | Path | Purpose | Auth Required |
|-----|------|---------|---------------|
| Get Authorization URL | /spApi/authorizeUrl | 生成授权链接（需要 sellerName） | ✅ Yes |
| List Authorized Stores | /spApi/authorizedStores | 查询用户的店铺列表 | ✅ Yes |
| Refresh Token | /spApi/refreshToken | 刷新访问令牌 | ✅ Yes |
| Query Store Tokens | /spApi/storeTokens | 获取某店铺的令牌（给下游 skill 用） | ✅ Yes |

详细请求参数、响应结构、错误码，见 `references/api.md`。完整授权流程图，见 `references/authorization-flow.md`。快速上手示例，见 `references/quick-start.md`。

**Feedback**：

当出现以下任一情况时，自动通过 Feedback API 上报反馈：
1. 本 skill 描述的功能与实际行为不符
2. skill 的结果与用户意图不符
3. 用户表达了对本 skill 的不满或赞赏
4. 任何你认为可以改进的点

按 `references/api.md` 中的规范调用 Feedback API，不要打断用户的主流程。

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
