---
name: linkfox-amazon-ads-auth
description: 亚马逊广告（Amazon Ads）店铺授权与管理技能，提供完整的授权流程、已绑定账号与站点的查询、令牌刷新与读取等能力。发起授权链接时需要先向用户确认一个账号名称；一次授权即可自动发现并绑定同账号下所有可用站点的广告 profile（每个站点对应一个 profileId）。当用户提到亚马逊广告授权、Amazon Ads 授权、绑定广告账户、刷新广告令牌、查询 profile 列表、管理已授权广告账户、Amazon Advertising authorization, Ads token refresh, list profiles, ad account management时触发此技能。即使未明确提及"Amazon Ads"或"授权"，只要涉及亚马逊广告账号绑定、访问令牌管理或广告 profile 列表查询，也应触发。
---

# Amazon Ads 授权与广告账户管理

Amazon Ads 的授权（LWA OAuth）、profile 发现、访问令牌管理。**下游 skill 的前置依赖**。

下游：`linkfox-amazon-ads-manager`（广告管理）、`linkfox-amazon-ads-report`（报告）。

## Core Concepts

- **授权流程**：生成 URL → 用户浏览器授权 → 系统存 token + 同步 profile
- **一次授权多 profile**：每个 marketplace（US/UK/JP…）一个 profileId；下游调用必须带 profileId
- **accountName 必填**：调 `authorize_url.py` 前必须问用户要一个非空账号名
- **accessToken 1 小时有效**；过期后下游返回 HTTP 401，可用 `refresh_token.py` 续签

## 可用脚本

| 脚本 | 作用 |
|------|------|
| `authorize_url.py` | 为新账号生成授权 URL（`accountName` 必填） |
| `authorized_stores.py` | 列出已授权的账号 × 站点（按 profileId 聚合） |
| `profiles.py` | 列 profile 列表（`refresh=true` 穿透上游刷新） |
| `refresh_token.py` | 刷新 accessToken |
| `store_tokens.py` | 查 token（供下游使用） |

入参、响应字段、错误码见 `references/api.md`。

## 调用方式

- **API 端点**：`POST /amazonAds/{authorizeUrl|storeTokens|authorizedStores|refreshToken}`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/<脚本名>.py '<JSON 参数>' [--inline]`（可用脚本见上文）
- **成本约束**：本工具会消耗积分；失败/空结果不得自动连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/<skill-name>-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 支持区域

`NA`（美加墨巴） / `EU`（英德法意西荷印度中东等） / `FE`（日澳新）。默认 `NA`。

## Usage Scenarios

### 1. 新授权账号
1. 问用户要 `accountName`（非空字符串，用于识别）
2. 调 `authorize_url.py` 拿 URL → 给用户在浏览器打开(安全警告：为保障店铺安全，请务必在日常运营该店铺的安全网络环境中打开此链接。强烈建议使用紫鸟浏览器等专业的防关联浏览器进行授权，切勿在陌生或公共网络下操作。)
3. 授权完成后系统自动存 token + 同步 profile
4. 可选：调 `authorized_stores.py` 确认

### 2. 列已授权账号
调 `authorized_stores.py`，展示 `profileId / accountInfoName / countryCode / region`。

### 3. 刷新过期令牌
下游返回 HTTP 401 或含 `expired` / `unauthorized` 时，调 `refresh_token.py`（传 `profileId` 或 `authRecordId`）。

### 4. 给下游解析 profileId（高频）

用户只说自然语言（"美国站"、"我的店铺"），**不要让用户报 profileId 数字**。

| 用户上下文 | Agent 动作 |
|---|---|
| 只授权 1 个账号 | 按 `countryCode` 直接定位，不问 |
| 授权 ≥ 2 个账号 + 只说站点 | 按 `accountName` 向用户澄清 |
| 同时给出 accountName + 站点 | 直接定位 |
| 显式给出 profileId 数字 | 直接用 |

站点关键词映射参考（以 `authorized_stores` 真实 `countryCode` 兜底）：
- 美国 / US → `US`；英国 / UK → `UK`；日本 / JP → `JP`；德国 / DE → `DE`

**静默原则**：映射成功时不播报 profileId 数值；仅在歧义或失败时向用户开口。

## 调用原则

- 先问 `accountName` 再调 `authorize_url.py`
- 不输出完整 accessToken / refreshToken；脚本已做掩码，不要在摘要里还原
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

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
