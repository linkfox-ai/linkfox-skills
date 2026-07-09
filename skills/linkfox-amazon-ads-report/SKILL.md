---
name: linkfox-amazon-ads-report
description: 亚马逊广告（Amazon Ads）报告一站式获取技能，覆盖 Sponsored Products (SP) / Sponsored Brands (SB) / Sponsored Display (SD) 全部报告类型。脚本自动完成报告的创建、等待、下载和解压，直接返回可读的结构化数据。真实可用的报告类型及每类的列清单/groupBy/filters 以 `references/report-types/<adProduct-dir>/<reportTypeId>.md` 为单一真相源。当用户提到拉取亚马逊广告报告、下载 Amazon Ads 报告、获取 SP/SB/SD 广告活动/关键词/搜索词/投放商品/购买商品/广告组/流量异常/Prompt 扩展等任意报告时触发。本技能依赖 linkfox-amazon-ads-auth。Sponsored Television (ST) / Amazon DSP 暂未覆盖。
---

# Amazon Ads 报告获取

报告一站式获取：脚本自动完成报告的创建、等待（约 2–10 分钟）、下载和解压，直接返回可读的结构化数据。
脚本本身不做"该选哪些列 / 该怎么分组"的业务判断，这些由 agent 先查 `references/report-types/` 下对应的 `.md` 文件，再显式传给脚本。

**依赖 `linkfox-amazon-ads-auth`**（脚本启动自动检查；未安装时 exit 42，stderr 打 `DEPENDENCY_MISSING`）。

### ⚠️ 多账号场景：调用前必须解析好 profileId

用户经常只说自然语言（"美国站"、"日本站"、"我的店铺"），本 skill 的所有脚本都必须拿到数字 `profileId` 才能调。按下列顺序处理，**不要跳过**：

1. 先调 `linkfox-amazon-ads-auth` 的 `authorized_stores.py` 拉出用户已授权的账号 × 站点清单。
2. 根据用户提到的站点（映射到 `countryCode`，如 美国→`US`）匹配候选 profile：
   - **只有 1 个候选** → 静默取对应 profileId，继续调用；不要把 profileId 数字播报给用户。
   - **≥ 2 个候选（同站点下多个授权账号）** → **必须向用户澄清**，用 `accountName` 问："你在美国站授权了 A 和 B 两个账号，这次用哪个？"
   - **0 个候选** → 告知用户该站点未授权，引导去 `linkfox-amazon-ads-auth` 做授权。
3. **严禁**让用户直接报 profileId 数字。
4. **严禁**在歧义下"挑第一个"或"选默认"绕过澄清。

完整决策表见 `linkfox-amazon-ads-auth` SKILL.md 的 **Usage Scenarios 第 4 节**。

## 调用方式

- **API 端点**：`POST /amazonAds/developerProxy`（不同操作通过请求体区分；完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/<脚本名>.py '<JSON 参数>' [--inline]`（可用脚本见上文脚本一览）
- **成本约束**：本工具会消耗积分；失败/空结果不得自动换关键词、翻页或连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/<skill-name>-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## Core Concepts

- **覆盖**：SP / SB / SD 全部报告类型（以 `references/report-types/` 下存在的 `.md` 为准；ST / DSP 暂未覆盖）
- **一站式**：脚本内部自动完成报告创建 → 等待生成（约 2–10 分钟）→ 下载 → 解压，调用方只需等最终结果
- **单脚本**：`get_report.py`（覆盖 SP / SB 全部 adProduct）
- **元数据 vs. 运行参数**：
  - 每个报告类型的**可用字段**（timeUnit / groupBy / filters / 全部列名）集中在 `references/report-types/<adProduct-dir>/<reportTypeId>.md`
  - **脚本运行参数**（等待间隔、访问链接时效等）见本文件和 `references/api.md`

## 可用脚本

| 脚本 | 职责 |
|------|------|
| `get_report.py` ⭐ | 一站式执行。**必填** `adProduct` / `groupBy` / `columns`，由 agent 从 report-types/ 提取后传入 |
| `check_auth_dependency.py` | 检测 linkfox-amazon-ads-auth 是否安装 |

完整脚本参数、响应结构见 `references/api.md`。

## Agent 调用流程

Agent 触达"拉取亚马逊广告报告"类需求时，**必须**按下列顺序：

1. **定 reportTypeId**：按用户意图挑选（如"上周花费"→ `spCampaigns`；"哪个商品卖得好"→ `spAdvertisedProduct` / `sbPurchasedProduct`；"用户搜什么词找到我"→ `spSearchTerm`）
2. **查 reference**：打开 `references/report-types/<adProduct-dir>/<reportTypeId>.md`
   - **frontmatter** 给出：`adProduct` / `groupBy`（Configuration 表推荐的） / `timeUnit`(可枚举) / `format` / `dateRange` / `filters`
   - **Base metrics 表** 给出：此报告类型允许的全部列名
3. **向用户咨询可定制条件**（用户答"默认/随便"时跳过，进入第 4 步的默认选择）：
   - `timeUnit`：DAILY（按日拆分）还是 SUMMARY（汇总）
   - `columns` 扩展：是否要归因列（sales7d / purchases7d / acosClicks7d / roasClicks7d）、视频指标、newToBrand 等
   - `filters`：是否过滤 campaignStatus / keywordType / adStatus 等
4. **按用户回复或默认构造 columns**（见下节 "默认条件"）
5. **调脚本**：`adProduct` / `groupBy` / `columns` 三个必填字段**显式**传入

## 默认条件（用户未指定时使用）

| 条件 | 默认规则 |
|------|---------|
| `timeUnit` | 日期跨度 ≤ 7 天 → `DAILY`；> 7 天 → `SUMMARY` |
| `columns` 身份维度 | `DAILY` 时必含 `date`；`SUMMARY` 时必含 `startDate` + `endDate`；再追加该报告的主键字段（参考 frontmatter 中 groupBy 对应的主键，如 campaignId+campaignName / advertisedAsin+advertisedSku / searchTerm / keyword 等） |
| `columns` 基础指标 | `impressions` / `clicks` / `cost`（以该报告 Base metrics 存在的为准） |
| `columns` 归因指标 | **仅当用户提到"销售/转化/ROI/ACOS"等意图时追加**：`sales7d` / `purchases7d` / `acosClicks7d` / `roasClicks7d`（以 Base metrics 存在者为准） |
| `filters` | 不加（全量返回） |
| `groupBy` | 取 frontmatter `groupBy` 数组的第一个值（即 Configuration 表里 Amazon 官方推荐的主维度） |

## 请求示例

所有 example 都显式传入三个必填字段（`adProduct` / `groupBy` / `columns`）。

### 1. SP 广告活动报告（最常见）

```bash
python scripts/get_report.py '{
  "profileId": 1234567890, "region": "NA",
  "reportTypeId": "spCampaigns",
  "adProduct": "SPONSORED_PRODUCTS",
  "groupBy": ["campaign"],
  "columns": ["date","campaignId","campaignName","impressions","clicks","cost"],
  "startDate": "2026-04-27","endDate": "2026-05-03",
  "timeUnit": "DAILY"
}'
```

### 2. SP 搜索词报告（含归因）

```bash
python scripts/get_report.py '{
  "profileId": 1234567890, "region": "NA",
  "reportTypeId": "spSearchTerm",
  "adProduct": "SPONSORED_PRODUCTS",
  "groupBy": ["searchTerm"],
  "columns": ["searchTerm","keyword","matchType","impressions","clicks","cost",
              "sales7d","sales14d","purchases7d","acosClicks14d","roasClicks14d",
              "startDate","endDate"],
  "startDate": "2026-04-01","endDate": "2026-04-30",
  "timeUnit": "SUMMARY",
  "filters": [{"field":"keywordType","values":["BROAD","PHRASE","EXACT"]}]
}'
```

### 3. SB 广告组报告

```bash
python scripts/get_report.py '{
  "profileId": 1234567890, "region": "NA",
  "reportTypeId": "sbAdGroup",
  "adProduct": "SPONSORED_BRANDS",
  "groupBy": ["adGroup"],
  "columns": ["adGroupId","adGroupName","impressions","clicks","cost","purchases","sales","startDate","endDate"],
  "startDate": "2026-04-01","endDate": "2026-04-30"
}'
```

### 4. SD 广告活动报告

```bash
python scripts/get_report.py '{
  "profileId": 1234567890, "region": "NA",
  "reportTypeId": "sdCampaigns",
  "adProduct": "SPONSORED_DISPLAY",
  "groupBy": ["campaign"],
  "columns": ["date","campaignId","campaignName","impressions","clicks","cost","purchases","sales"],
  "startDate": "2026-04-27","endDate": "2026-05-03",
  "timeUnit": "DAILY"
}'
```

### 5. 轮询一个已有 reportId（救回上次超时 / 手工恢复）

当上次运行因为客户端轮询窗口太短退出、但报告在 Amazon 侧仍在跑时，直接传入 `reportId` 即可跳过创建，继续轮询并下载。此模式下只需 `profileId` / `region` / `reportId`，其余字段不必填。

```bash
python scripts/get_report.py '{
  "profileId": 1234567890, "region": "NA",
  "reportId": "7df1ef5d-45ba-40cc-b607-ff2148cf4f5e",
  "maxAttempts": 60, "pollInterval": 30
}'
```

> **自动恢复**：如果调用方未传 `reportId`、且 Amazon 对同参数请求触发去重（返回 HTTP 425 `The Request is a duplicate of : <uuid>`），脚本会自动解析出老 reportId 并转为轮询该老报告，无需重试。

## 响应格式

成功：
```json
{
  "success": true,
  "reportId": "4ee811a0-...",
  "reportTypeId": "spCampaigns",
  "startDate": "2026-04-28", "endDate": "2026-05-04",
  "downloadPath": "C:/.../tmp/report_data.json",
  "extractedFileHttpUrl": "http://127.0.0.1:51234/download",
  "extractedFileHttpServeSeconds": 300
}
```

失败：
```json
{"error":"Upstream HTTP 400","httpStatus":400,
 "body":"{\"code\":\"400\",\"detail\":\"startDate to endDate range (32 days) must not exceed maximum range (31 days)\"}"}
```

## 调用原则

- 用户指定了 reportTypeId 就只拉那一种，不擅自替换
- 报告失败（非 2xx 或 status=FAILED）时如实告知错误原因，不盲目重试
- 成功后把报告的本地文件路径和访问链接完整展示给用户，并提醒访问链接有时效（默认 5 分钟内有效，过期需重新拉取）
- **超时不是失败**：当脚本返回 `status=STILL_PROCESSING`（exit code=2），说明客户端已等满默认 10 分钟但报告仍在 Amazon 侧生成。此时 **必须**向用户说明情况并询问是否继续等待，绝不能当成失败处理。参考回复："报告还在 Amazon 侧生成中（已等 10 分钟），要继续等吗？可以选：A. 再等 ~20 分钟（maxAttempts=60）、B. 再等 ~1 小时（maxAttempts=120）、C. 先停，我稍后用 reportId 回来。" 用户选 A/B → 用 `resumeHint.params` 切到仅轮询模式续跑

## 常见错误

| 状态 | 含义 | 建议 |
|------|------|------|
| `Missing required parameters: adProduct/groupBy/columns` | 调用方未显式传入三必填 | 回到 "Agent 调用流程" 第 2 步，从 `references/report-types/<adProduct-dir>/<reportTypeId>.md` 读出并补上 |
| `HTTP 401` | accessToken 过期 | 调 ads-auth 的 `refresh_token.py` 后重试 |
| `HTTP 403` | 未关联广告账户或权限不足 | 到 Amazon Ads 后台检查经理账户/广告账户关联 |
| `HTTP 400 "must not exceed maximum range"` | 日期跨度超限（多数 31 天） | 拆分拉取后本地合并；具体上限看对应 `.md` frontmatter `dateRange.maxSpanDays` |
| `HTTP 400` 含 `columns`/`groupBy` 校验错 | 列名拼写错 / 与 reportTypeId 不匹配 / 超出 Base metrics | 对照 `.md` 文件 Base metrics 表核对 |
| `status=FAILED` 含 `failureReason` | 上游生成失败 | 多为日期窗口或权限问题，按 failureReason 具体处理 |
| `status=STILL_PROCESSING` (exit 2) | 客户端轮询窗口耗尽但报告仍在生成 | **不是失败**。stdout 已含 `reportId` 与 `resumeHint.params`。询问用户是否继续等，用该 params（带 `reportId` + 更大 `maxAttempts`）切到仅轮询模式续跑 |
| `HTTP 425 "duplicate of"` | 同参数已有在跑的报告 | 脚本自动解析并转为轮询该老 reportId，正常情况下调用方无需干预 |
| exit 42 | 依赖 skill 未安装 | 先装 `linkfox-amazon-ads-auth` |

## 日期与数据

- **日期跨度上限**：多数报告 31 天；`sbPurchasedProduct` 是 731 天；`spGrossAndInvalids` / `sbGrossAndInvalids` / `sdGrossAndInvalids` 是 365 天（以 frontmatter 为准）
- **回溯窗口**：SP 默认 95 天、SB 60 天、GrossAndInvalids 365 天；具体以 frontmatter `dateRange.dataRetentionDays` 为准
- **数据延迟约 12 小时**；`endDate >= 今天` 脚本 stderr 警告但不拦截
- **空数据不等于报错**：账号当期无投放时报告会成功生成，JSON 可能为 `[]` 或指标全 0

## Not Applicable

- Brand Analytics / Retail Analytics / Attribution 报告 → 不在本 skill
- 报告删除 / 修改 / 定时任务 → 不在本 skill
- 实体元数据（campaign 名、keyword 匹配类型等）→ `linkfox-amazon-ads-manager`
- 授权 / token → `linkfox-amazon-ads-auth`

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
