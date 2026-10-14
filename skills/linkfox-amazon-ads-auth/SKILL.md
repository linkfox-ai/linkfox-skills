---
name: linkfox-amazon-ads-auth
description: 亚马逊广告（Amazon Ads）店铺授权与管理技能，提供完整的授权流程、已绑定账号与站点的查询、profile 管理、当前用户广告授权连接解绑等能力。发起授权链接时需要先向用户确认一个账号名称；一次授权即可自动发现并绑定同账号下所有可用站点的广告 profile（每个站点对应一个 profileId）。当用户提到亚马逊广告授权、Amazon Ads 授权、批量授权、绑定广告账户、解绑广告账户、断开广告连接、取消广告授权、查询 profile 列表、管理已授权广告账户、Amazon Advertising authorization, list profiles, ad account management时触发此技能。即使未明确提及"Amazon Ads"或"授权"，只要涉及亚马逊广告账号绑定、授权关系管理或广告 profile 列表查询，也应触发。授权时支持保留原手动流程或选择紫鸟 CLI 自动授权。
---

# Amazon Ads 授权与广告账户管理

Amazon Ads 的授权（LWA OAuth）、profile 发现与授权连接管理。**下游 skill 的前置依赖**。

下游：`linkfox-amazon-ads-manager`（广告管理）、`linkfox-amazon-ads-report`（报告）。

## 授权方式路由（授权任务最先执行）

本节优先于后续 `Core Concepts`、`Usage Scenarios` 和参数要求。只有用户要新增、恢复或批量执行授权时才进行选择；查询和解绑仍直接执行原场景。

需要授权且用户尚未选择方式时，必须先让用户选择：

1. **手动授权**：选择后继续执行原 Scenario 1，此时才询问并使用 `accountName`。
2. **紫鸟 CLI 自动授权**：向用户展示此选项时只用一句话说明：“紫鸟 CLI 自动授权（推荐，仅支持本机 Windows/macOS；Agent 会自动检查并推进，只有登录、系统确认或审核等必要步骤才需要你操作）”。该模式要求 CLI、紫鸟客户端和 Bridge 位于同一台用户可见的电脑；云端 Agent、远程主机/虚拟机、容器、WSL 和 Linux（包括本机 Ubuntu）均不支持，不能因为远端装得上软件就启用。用户选择后在后台完成环境、版本和现有配置检查，正常项不逐条汇报，已有可用配置直接复用。只有执行环境被明确识别为用户本机后才完整执行 `references/automatic-authorization.md`；否则提示本机使用自动授权或选择手动授权，禁止在当前环境安装 CLI、申请 Key 或打开店铺。自动模式不得询问手动流程的 `accountName`；所选紫鸟店铺的 `storeName` 用作授权标记。

用户已在当前请求中明确说“自动授权”“紫鸟 CLI 自动授权”或同义表达时，直接进入自动流程，不重复询问授权方式，也不能先询问 `accountName`。“全部授权”只表示全部所选 Amazon 店铺的 Ads 授权，并且只创建 Ads worker。

## Core Concepts

- **授权流程**：生成 URL → 用户浏览器授权 → 系统存 token + 同步 profile
- **一次授权多 profile**：每个 marketplace（US/UK/JP…）一个 profileId；下游调用必须带 profileId
- **accountName 必填**：调 `authorize_url.py` 前必须问用户要一个非空账号名
- **下游选店**：业务 skill 经 `developerProxy` 传 **`profileId`**（+ `region`），令牌由服务端透明管理和注入；本 skill 不提供 raw token 读取或手动刷新能力

## 可用脚本

| 脚本 | 作用 |
|------|------|
| `authorize_url.py` | 为新账号生成授权 URL（`accountName` 必填） |
| `authorized_stores.py` | 列出已授权的账号 × 站点（按 profileId 聚合） |
| `profiles.py` | 列 profile 列表（`refresh=true` 穿透上游刷新） |
| `cancel_authorization.py` | 按 `authRecordId` 解绑广告连接 |

入参、响应字段、错误码见 `references/api.md`。

## 调用方式

- **API 端点**：`POST /amazonAds/{authorizeUrl|authorizedStores|profiles|cancelAuthorization}`（完整参数/响应/错误码见 `references/api.md`）
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

## 支持区域

`NA`（美加墨巴） / `EU`（英德法意西荷印度中东等） / `FE`（日澳新）。默认 `NA`。

## Usage Scenarios

### 1. 新授权账号
1. 问用户要 `accountName`（非空字符串，用于识别）
2. 调 `authorize_url.py` 拿 URL → 以文本形式给用户在浏览器打开(安全警告：为保障店铺安全，请务必在日常运营该店铺的安全网络环境中打开此链接。强烈建议使用紫鸟浏览器等专业的防关联浏览器进行授权，切勿在陌生或公共网络下操作。)
3. 授权完成后系统自动存 token + 同步 profile
4. 可选：调 `authorized_stores.py` 确认

### 1B. 批量授权账号（紫鸟 CLI）

完整执行 `references/automatic-authorization.md`。每家所选店铺建立一个 Ads worker；先生成本店授权链接并用对应紫鸟店铺打开，由 Agent 仅沿本次授权链路持续推进；可恢复问题自主处理，确需用户处理时才转人工，其余店铺继续。

### 2. 列已授权账号
调 `authorized_stores.py`，展示 `profileId / accountInfoName / countryCode / region`。

### 3. 给下游准备 profileId（高频）

用户只说自然语言（"美国站"、"我的店铺"），**不要让用户报 profileId 数字**。

下游 **`linkfox-amazon-ads-manager`** / **`linkfox-amazon-ads-report`** 调用 `developerProxy` 时传入解析到的 **`profileId`** 即可；不要读取或传递 Amazon raw token。

| 用户上下文 | Agent 动作 |
|---|---|
| 只授权 1 个账号 | 按 `countryCode` 直接定位 `profileId`，不问 |
| 授权 ≥ 2 个账号 + 只说站点 | 按 `accountName` 向用户澄清后定位 `profileId` |
| 同时给出 accountName + 站点 | 直接定位 `profileId` |
| 显式给出 profileId 数字 | 直接用 |

站点关键词映射参考（以 `authorized_stores` 真实 `countryCode` 兜底）：
- 美国 / US → `US`；英国 / UK → `UK`；日本 / JP → `JP`；德国 / DE → `DE`

**静默原则**：映射成功时不播报 profileId 数值；仅在歧义或失败时向用户开口。

### 4. 解绑广告连接

仅在用户要求时执行。当前用户按 API key 对应的成员身份识别；共用该身份的使用者会一起受影响。

1. 调 `profiles.py`（不传 `refresh=true`），按 `authRecordId` 定位连接；`authorized_stores.py` 按 profile 去重，不能据此判断完整授权关系。
2. 展示连接下全部账户和站点；若用户只要求单站点，须先取得对整份连接解绑的明确同意。
3. 调 `cancel_authorization.py`，传入选定的 `authRecordId`，不能用 `profileId` 替代。
4. 按 `references/api.md` 解释结果；后续重新查询连接，不自动重新授权。

## 调用原则

- 先问 `accountName` 再调 `authorize_url.py`
- 不向用户索取、读取、展示或传递 Amazon raw token；令牌生命周期由服务端处理
- 授权失败按错误码解释原因；不擅自重试

## 常见问题

### 授权链接打开报 400，client_id 看起来被污染

现象：URL 里 `client_id` 中间出现空格 / `+`，Amazon 报 `StegoRuntimeOAuth2ClientManager:getClientDefinition`。
原因：授权链接 ~270 字符，从终端 / 聊天窗口复制时被软换行插入空格。
解决：`authorize_url.py` 成功后会同步写到剪贴板 + `~/.cache/linkfox/last_authorize_url.txt`，**从这两处复制**；浏览器地址栏 Ctrl+V 即可。建议无痕窗口打开。

### 授权回调页显示 `profile_sync_failed`

原因：当前 Amazon 账号未在广告后台创建"经理账户（Manager Account）"并关联广告账户。

解决：登录 [Amazon Ads 控制台](https://advertising.amazon.com/) → Manager accounts → 关联账户，重新授权。

## Not Applicable

- 查广告活动 / 组 / 关键词 / 商品广告 / 定向 → `linkfox-amazon-ads-manager`
- 拉广告报告（含指标） → `linkfox-amazon-ads-report`
- 修改 / 创建 / 删除广告 → 本系列为只读
- 店铺订单 / 库存 / 财务 → `linkfox-amazon-store-*`

## Amazon Ads API 接口保护与重试指引

同一广告账号/profile 连续收到 Amazon Ads API 的 400、403、404 或 429 时，网关会返回 450、453、454 或 459 并短暂冷却。这些自定义状态码不是 Amazon 原生状态，也不表示封号；目的是避免持续异常或高频调用扩大广告账号风险。

| 状态与 message | 范围 | 触发与冷却 | 处理 |
|---|---|---|---|
| `450`：`400，请求异常，请优化您的参数` | 广告账号/profile+接口 | 60 秒内超过 3 次：5 分钟；10 分钟内超过 4 次：20 分钟 | 停止原参数重试，检查 profileId、region、实体/报告 ID、日期和请求体 |
| `453`：`403，店铺未授权，请先授权` | 广告账号/profile 全部接口 | 60 秒内超过 2 次：5 分钟；10 分钟内超过 4 次：30 分钟 | 停止该广告账号调用，检查 Ads 授权、应用权限、profile 归属和区域 |
| `454`：`404，资源不存在，请优化您的参数` | 广告账号/profile+接口 | 60 秒内超过 3 次：5 分钟；10 分钟内超过 4 次：30 分钟 | 确认资源 ID、所属 profile/区域、资源状态和接口路径 |
| `459`：`429限流中，请降低频率` | 广告账号/profile+接口 | 首次：15 秒；2 分钟内超过 2 次：30 秒；3 分钟内超过 4 次：2 分钟 | 降低并发、分页和轮询频率并逐级退避 |

- 立即停止自动或并发重试，不得通过换脚本或重复创建任务绕过保护；优先遵循 `retryAfter`、`blockedUntil`，没有时按表中时长说明。
- 450/453/454 必须先修正参数、授权或资源标识，冷却后最多谨慎重试一次；再次触发则停止调用。453 期间停止该广告账号/profile 全部 Ads API。
- 保留已有 `reportId` 等任务 ID；写操作结果不确定时先查询状态，不直接重放。
- 向用户先说明广告账号保护，再给原因、处理和等待时间。可回复：“为保护您的亚马逊广告账号安全，检测到 Amazon Ads API 连续返回{原因}，当前已进入短暂保护。请先{处理动作}，预计{等待时间}后再试；这不代表封号，也不是套餐或积分限制。”不要只说“LinkFox 限流”或“服务器繁忙”。

## 算力消耗规则

不消耗算力。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
