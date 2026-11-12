---
name: linkfox-amazon-store-auth
description: 亚马逊卖家店铺授权与账号连接管理。用于生成授权链接、绑定店铺、查询已授权店铺、检查授权状态、刷新访问令牌和本地取消/解绑授权；生成授权链接时需要 sellerName 区分店铺。用户提到亚马逊店铺授权、绑定或连接 Amazon Seller 账号、查看已授权店铺、授权失效、刷新令牌、token 状态、取消授权、解绑店铺、停用授权、Amazon seller authorization、bind seller account、refresh access token、disconnect seller account 时触发。即使未明确说“授权”，只要其他亚马逊店铺操作因未绑定店铺、凭证过期或需要选择授权账号而无法继续，也应触发此技能。
---

# Amazon 店铺授权与管理

本 skill 负责 **亚马逊卖家店铺的 OAuth 授权、已授权店铺列表、授权状态查询、令牌刷新与本地取消授权**，是拉取报告、查询库存、同步订单等所有下游操作的前置依赖。下游业务经 `developerProxy` 传入 `sellerId`+`region` 即可，**无需**先取 raw token。

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

### Store Tokens（授权状态，非 raw token 下发）

`POST /spApi/storeTokens` 返回**状态与元数据**（具体字段以网关为准），供确认授权是否有效、何时过期。**不要**将响应当作下游 `developerProxy` 的 token 来源。

| Field | Type | Description |
|-------|------|-------------|
| status | string | 授权/令牌状态（如有效、过期、缺失） |
| authRecordId | integer | 授权记录 ID（如有） |
| expiresIn | integer | 距 accessToken 过期的秒数（如有） |
| tokenExpiresAt | string | 绝对过期时间（如有） |
| message | string | 补充说明 |
| errcode / errmsg | integer / string | 网关错误（失败时） |

> 兼容说明：旧版网关可能仍返回 `accessToken`/`refreshToken`；Agent **不应**优先读取或传递给下游。下游应使用 `sellerId`+`region` 调 `developerProxy`。

## Supported Regions

| Code | Name | Marketplaces |
|------|------|--------------|
| NA | 北美 | 美国、加拿大、墨西哥 |
| EU | 欧洲 | 英国、德国、法国、意大利、西班牙、荷兰等 |
| FE | 远东 | 日本、澳大利亚、新加坡、印度 |

默认区域为 **NA**；解绑时按 Scenario 5 明确目标区域。

## 调用方式

- **API 端点**：`POST /spApi/{authorizeUrl|storeTokens|authorizedStores|refreshToken|cancelAuthorization}`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/<脚本名>.py '<JSON 参数>' [--inline]`（可用脚本见上文）
- **成本约束**：本工具会消耗算力；失败/空结果不得自动连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/<skill-name>-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 解决认证和算力问题
发生以下异常情况时，采用 references/onboarding.md 引导解决问题：

### 异常情况
- **未配置API Key**：环境变量未配置 `LINKFOX_AGENT_API_KEY`，也未配置 `LINKFOXAGENT_API_KEY`。
- **响应401或402状态码**
- **响应提示算力或余额不足**：消息含"算力余额不足/计费不足/余额不足/quota exceeded/insufficient balance/套餐到期/需充值/请充值"，或类似含义的内容。

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
2. 返回刷新**状态与元数据**（如 `status`、`message`、`expiresIn`）；服务端更新令牌
3. 下游可直接重试 `developerProxy`（传入相同 `sellerId`+`region`），**无需**读取 raw token

### Scenario 4: Query Store Token Status

**User request**：「查一下北美站点 A123 店铺的授权/令牌状态」

**Steps**：
1. 调用 `/spApi/storeTokens`，传入 `sellerId` 与 `region`
2. 向用户展示**状态字段**（`status`、`expiresIn`、`tokenExpiresAt`、`message` 等）
3. **不要**把响应当作下游 proxy 的 token；业务调用直接带 `sellerId`+`region`

### Scenario 5: Cancel Local Authorization

**User request**：「取消/解绑我的亚马逊店铺授权」

仅在用户要求时执行。当前用户按 API key 对应的成员身份识别；共用该身份的使用者会一起受影响。

**Steps**：

1. 从用户指定目标或 `/spApi/authorizedStores` 确定 `sellerId + region`；不使用默认区域，有歧义时让用户选择。
2. 说明解绑覆盖整个区域；若用户只要求单站点，须先取得对整个区域解绑的明确同意。
3. 调用 `/spApi/cancelAuthorization`，传入选定的 `sellerId` 与 `region`。
4. 按 `references/api.md` 解释结果；后续重新查询店铺，不自动重新授权。

### Scenario 6: Prepare Account Selector for Any Store Operation (Standard Preparation Workflow)

当用户提出任何涉及卖家后台数据的请求（拉报告、查库存、看订单等），**本 skill 负责前置的「选店 → 确认授权」**，具体业务由相应的下游 skill 接手。

**Steps**：
1. **列出已授权店铺**：调用 `/spApi/authorizedStores`
2. **让用户选择店铺**：如果有多家店铺，请用户明确选哪一家，确定 `sellerId` 与 `region`
3. （可选）调用 `/spApi/storeTokens` **仅作状态确认**（过期则先 `refreshToken`）
4. **把 `sellerId`+`region` 交给下游 skill**（例如 `linkfox-amazon-store-report`），由下游直接调 `developerProxy`

**Why this workflow is critical**：
- 用户可能同时授权了多家不同区域的店铺
- 每家店铺的令牌与权限彼此独立
- 必须使用与店铺匹配的 `sellerId`+`region`，跳过「选店」会导致歧义和错误

## Display Rules

1. **先有店铺名再生成授权链接**：若用户未提供 `sellerName`，**必须先问**，不允许带空值调用 `/spApi/authorizeUrl`。
2. **只呈现数据**：展示授权结果、店铺列表、令牌信息即可，不做业务建议。
3. **安全意识**：响应若含 legacy token 字段，不要明文展示；优先呈现 `status` / 过期时间等元数据。
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
| "查 XXX 店铺授权状态" / "Check store token status" | 查询授权状态（storeTokens） |
| "绑定我的亚马逊账号" / "Connect my Amazon seller account" | 新店铺授权 |
| "取消授权" / "解绑这个亚马逊店铺" / "Disconnect seller account" | 本地取消/解绑授权 |

**Not applicable** — 超出本 skill 的业务：

- **拉取亚马逊报告** → 请使用 `linkfox-amazon-store-report`
- 产品 listing 管理、订单处理、库存管理、广告投放 → 由其他 skill 负责

**Boundary judgment**：
- 本 skill 只负责「授权 + 管店铺 + 令牌刷新/状态查询 + 为下游准备 `sellerId`+`region` 选店信息」。
- **不要**为下游 `developerProxy` 调用 `storeTokens` 取 raw `accessToken`（除非兼容极旧客户端且用户明确要求）。
- 当用户要做具体卖家后台业务（如拉报告）时：
  1. 本 skill 执行 Scenario 6 的标准前置流程（选店）
  2. 随后切换到对应下游 skill，直接 `developerProxy` + `sellerId`+`region`
- 不要直接越过本 skill 去调具体 Amazon 开放接口。

## Quick Reference

### Authorization & Token Management APIs

| API | Path | Purpose | Auth Required |
|-----|------|---------|---------------|
| Get Authorization URL | /spApi/authorizeUrl | 生成授权链接（需要 sellerName） | ✅ Yes |
| List Authorized Stores | /spApi/authorizedStores | 查询用户的店铺列表 | ✅ Yes |
| Refresh Token | /spApi/refreshToken | 刷新访问令牌 | ✅ Yes |
| Query Store Token Status | /spApi/storeTokens | 查询某店铺授权/令牌状态（非下游 token 来源） | ✅ Yes |
| Cancel Authorization | /spApi/cancelAuthorization | 本地取消/解绑当前用户的店铺授权 | ✅ Yes |

详细请求参数、响应结构、错误码，见 `references/api.md`。完整授权流程图，见 `references/authorization-flow.md`。快速上手示例，见 `references/quick-start.md`。

## Amazon SP-API 接口保护与重试指引

同一店铺连续收到 Amazon SP-API 的 400、403、404 或 429 时，网关会返回 450、453、454 或 459 并短暂冷却。这些自定义状态码不是 Amazon 原生状态，也不表示封号；目的是避免持续异常或高频调用扩大店铺风险。

| 状态与 message | 范围 | 触发与冷却 | 处理 |
|---|---|---|---|
| `450`：`400，请求异常，请优化您的参数` | 店铺+接口 | 60 秒内超过 3 次：5 分钟；10 分钟内超过 4 次：20 分钟 | 停止原参数重试，检查必填字段、marketplace、ID、日期和请求体 |
| `453`：`403，店铺未授权，请先授权` | 店铺全部接口 | 60 秒内超过 2 次：5 分钟；10 分钟内超过 4 次：30 分钟 | 停止该店铺调用，检查授权、权限、店铺归属和区域 |
| `454`：`404，资源不存在，请优化您的参数` | 店铺+接口 | 60 秒内超过 3 次：5 分钟；10 分钟内超过 4 次：30 分钟 | 确认资源 ID、所属店铺/站点、资源状态和接口路径 |
| `459`：`429限流中，请降低频率` | 店铺+接口 | 首次：15 秒；2 分钟内超过 2 次：30 秒；3 分钟内超过 4 次：2 分钟 | 降低并发、分页和轮询频率并逐级退避 |

- 立即停止自动或并发重试，不得通过换脚本或重复创建任务绕过保护；优先遵循 `retryAfter`、`blockedUntil`，没有时按表中时长说明。
- 450/453/454 必须先修正参数、授权或资源标识，冷却后最多谨慎重试一次；再次触发则停止调用。453 期间停止该店铺全部 SP-API。
- 保留已有 `reportId`、`feedId` 等任务 ID；写操作结果不确定时先查询状态，不直接重放。
- 向用户先说明店铺保护，再给原因、处理和等待时间。可回复：“为保护您的亚马逊店铺安全，检测到 Amazon SP-API 连续返回{原因}，当前已进入短暂保护。请先{处理动作}，预计{等待时间}后再试；这不代表封号，也不是套餐或算力限制。”不要只说“LinkFox 限流”或“服务器繁忙”。

## 算力消耗规则

不消耗算力。

**Feedback**：

当出现以下任一情况时，自动通过 Feedback API 上报反馈：
1. 本 skill 描述的功能与实际行为不符
2. skill 的结果与用户意图不符
3. 用户表达了对本 skill 的不满或赞赏
4. 任何你认为可以改进的点

按 `references/api.md` 中的规范调用 Feedback API，不要打断用户的主流程。

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
