# linkfox-amazon-ads-report — 参数与字段参考

Amazon Ads 报告自动化获取（SP / SB 覆盖；SD / ST / DSP 暂未覆盖）。授权见 `linkfox-amazon-ads-auth`；广告管理见 `linkfox-amazon-ads-manager`。

> **📌 报告类型的真相源**：每个 `reportTypeId` 的完整规格（可用 columns / groupBy / filters / timeUnit / 日期约束 / 官方示例）在 `references/report-types/<adProduct-dir>/<reportTypeId>.md`，**按 adProduct 分目录**：
> - `report-types/sp/`（Sponsored Products）
> - `report-types/sb/`（Sponsored Brands）
>
> 目录总览见 `report-types/index.md`。本文件仅给运行时脚本参数与通用规则。

## 支持的报告类型

完整列表见 `report-types/index.md` 及各 adProduct 子目录下的 `index.md`。常用快速索引：

| reportTypeId | 业务含义 | 文件 |
|--------------|---------|------|
| `spCampaigns` | 广告活动级（SP） | `report-types/sp/spCampaigns.md` |
| `spAdvertisedProduct` | 投放商品级（SP） | `report-types/sp/spAdvertisedProduct.md` |
| `spSearchTerm` | 搜索词级（SP） | `report-types/sp/spSearchTerm.md` |
| `spTargeting` | 定向/关键词级（SP） | `report-types/sp/spTargeting.md` |
| `sbCampaigns` / `sbAdGroup` / `sbAds` / ... | Sponsored Brands | `report-types/sb/*.md` |

## 输入参数

脚本支持两种模式：

- **全链路模式（默认）**：创建报告 → 轮询 → 下载。需要下表全部必填字段。
- **仅轮询模式**：入参中显式传入 `reportId`（见下方"可选流程参数"），跳过创建，只需 `profileId` / `region`，其余全部可省略。用于救回上次客户端超时但报告仍在跑的场景。

### 必填（全链路模式）

| 参数 | 类型 | 说明 |
|------|------|------|
| `profileId` | number | 从 ads-auth 获取 |
| `region` | string | `NA` / `EU` / `FE` |
| `reportTypeId` | string | 见 `report-types/index.md` 各 adProduct 子目录下的完整列表 |
| `adProduct` | string | 取自对应 `.md` 文件的 frontmatter（`SPONSORED_PRODUCTS` / `SPONSORED_BRANDS`）|
| `groupBy` | list | 取自对应 `.md` 文件的 frontmatter |
| `columns` | list | 取自对应 `.md` 文件 Base metrics 表的子集 |
| `startDate` | string | `YYYY-MM-DD`（含当天） |
| `endDate` | string | `YYYY-MM-DD`（含当天） |

### 可选业务参数

| 参数 | 默认 | 说明 |
|------|------|------|
| `name` | `{reportTypeId}_{startDate}_{endDate}` | 报告显示名 |
| `timeUnit` | `SUMMARY` | `DAILY`（每天一行） / `SUMMARY`（整期一行） |
| `format` | `GZIP_JSON` | 响应文件格式 |
| `filters` | 空 | 过滤条件数组，字段与取值见对应 `.md` 文件 |

### 可选流程参数

| 参数 | 默认 | 说明 |
|------|------|------|
| `reportId` | 无 | 若显式传入，脚本进入**仅轮询模式**：跳过创建步骤，直接对该 reportId 轮询与下载。此时只要 `profileId` / `region` + `reportId`，其他字段可省 |
| `pollInterval` | 30 | 轮询间隔秒 |
| `maxAttempts` | 20 | 最大轮询次数（默认 10 分钟上限） |
| `skipDepCheck` | false | 跳过依赖检查 |
| `serveExtractedFileHttp` | true | 是否启本机 HTTP 服务 |
| `serveHost` | `127.0.0.1` | 绑定地址（仅本机可访问） |
| `servePort` | 0 | 端口（0=系统分配） |
| `serveSeconds` | 300 | HTTP 服务存活秒 |
| `includeAmazonSourceUrl` | false | 响应中带预签名 URL |

## 日期限制

- **跨度上限**：以对应 `.md` 文件 frontmatter 的 `dateRange.maxSpanDays` 为准（多数 31 天；`sbPurchasedProduct` 731 天；GrossAndInvalids 系列 365 天）。超出返回 HTTP 400 `"must not exceed maximum range"`。
- **回溯上限**：以 `dateRange.dataRetentionDays` 为准（SP 多为 95 天，SB 60 天）。
- **数据延迟**：~12 小时；`endDate >= 今天` 脚本会 stderr 警告但不拦截。建议 `endDate <= 昨天`。

## 各报告类型的列

每个 reportTypeId 的完整 Base metrics 列表、allowed groupBy、filters 枚举值，统一在 `report-types/<adProduct-dir>/<reportTypeId>.md` 中维护：

- `.md` 的 **frontmatter** 提供 `adProduct` / `groupBy` / `timeUnit`（可选值）/ `format` / `filters` / `dateRange`
- **Base metrics 表**列出此报告类型支持的**全部列名**；调用方按业务需要选子集

归因窗口后缀约定：`_1d` / `_7d` / `_14d` / `_30d` 表示 1/7/14/30 天归因窗口（点击或曝光归因的销售额、订单量、件数等）。具体每个字段支持哪些窗口，以对应 `.md` 文件的 Base metrics 表为准（不是所有字段都有全部 4 个窗口版本）。

## 工作流与输出

脚本流程：依赖检查 → 取 token → 创建报告 → 等待生成（每 `pollInterval` 秒查询一次状态）→ 下载 GZIP_JSON（Amazon 预签名 URL 约 1 小时有效）→ 解压为可读 JSON → 通过本机 `127.0.0.1` 上的临时 HTTP 服务对调用方暴露（`serveSeconds` 后自动关闭）→ 输出调用结果 JSON（含本地文件路径与访问链接）。

`status` 枚举：`PENDING` / `PROCESSING` / `COMPLETED` / `FAILED`。

### 成功响应

```json
{
  "success": true,
  "reportId": "4ee811a0-6aaa-4ceb-9d31-d3bcecf85430",
  "status": "COMPLETED",
  "reportTypeId": "spCampaigns",
  "startDate": "2026-04-28", "endDate": "2026-05-04",
  "pollAttempts": 13, "elapsedSeconds": 255,
  "downloadPath": "C:/.../tmp/report-xxx.json",
  "extractedFileHttpUrl": "http://127.0.0.1:51234/report-xxx.json",
  "serveExpiresAt": "2026-05-06T14:54:03+08:00"
}
```

### 失败响应

**a) 创建阶段非 2xx**：
```json
{"error":"Upstream HTTP 400","httpStatus":400,
 "body":"{\"code\":\"400\",\"detail\":\"startDate to endDate range (32 days) must not exceed maximum range (31 days)\"}"}
```

**b) 报告生成失败**（`failureReason` 从上游透传）：
```json
{"success":false,"error":"Report generation failed with status=FAILED",
 "reportId":"4ee811a0-...","status":"FAILED",
 "failureReason":"Requested columns are not supported for this report type.",
 "pollAttempts":3}
```

**c) 轮询超时**（报告未坏，仅客户端等待窗口耗尽 — **exit code = 2**）：
```json
{
  "success": false,
  "status": "STILL_PROCESSING",
  "reportId": "4ee811a0-...",
  "reportTypeId": "spCampaigns",
  "profileId": 1234567890,
  "lastStatus": "PROCESSING",
  "pollAttempts": 20,
  "elapsedSeconds": 600,
  "message": "客户端已等 ~600 秒（20 次轮询）报告仍在 Amazon 侧生成，并未失败。用 reportId 切换到仅轮询模式即可继续等待。",
  "resumeHint": {
    "mode": "poll-only",
    "note": "传入 reportId + 更大的 maxAttempts 继续轮询同一份报告",
    "params": {"profileId": 1234567890, "region": "NA", "reportId": "4ee811a0-...", "maxAttempts": 60, "pollInterval": 30}
  }
}
```

调用方收到此响应应视为"未完成"而非"失败"，询问用户是否继续等待，直接把 `resumeHint.params` 作为入参续调 `get_report.py`。

## 错误码

| httpStatus / exit | 含义 | 建议 |
|-------------------|------|------|
| 200 | 成功 | 消费 `extractedFileHttpUrl` 或 `downloadPath` |
| 400 | 入参错（日期超限 / reportTypeId 非法 / columns 不适配） | 按 `detail` 修正 |
| 401 | accessToken 过期 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 402 | 积分或余额不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 403 | profileId 无权限 | 核对 profileId |
| 404 | reportId 不存在或已过期 | 重新发起报告 |
| 422 | columns / groupBy 与 reportTypeId 不适配 | 对照 `report-types/<adProduct-dir>/<reportTypeId>.md` 的 Base metrics / frontmatter 核对 |
| 425 | 同参数已有在跑的报告，Amazon 做了去重；body 形如 `"The Request is a duplicate of : <reportId>"` | **脚本自动解析该 reportId 并无缝转为轮询该老报告**，正常情况下无需干预；若调用方自行处理，也可把 reportId 拿出来，下次改用仅轮询模式（`{..., "reportId":"<uuid>"}`） |
| 429 | 限流（~30 req/min/profile） | 间隔 30s 重试 |
| `status=FAILED` | 上游生成失败 | 看 `failureReason` |
| `status=STILL_PROCESSING` (exit 2) | 客户端轮询窗口耗尽但报告仍在 Amazon 侧生成 | **非失败**。stdout 已输出 `reportId` 与 `resumeHint.params`。询问用户是否继续等，用 params 切到仅轮询模式续跑（maxAttempts=60 约 30 分钟 / =120 约 1 小时） |
| exit 42 | 依赖 skill 未安装 | 先装 `linkfox-amazon-ads-auth` |

## 调用示例

```bash
# 1. SP 广告活动汇总（DAILY，一周）
python get_report.py '{"profileId":1111111111,"region":"NA",
  "reportTypeId":"spCampaigns",
  "adProduct":"SPONSORED_PRODUCTS",
  "groupBy":["campaign"],
  "columns":["date","campaignId","campaignName","impressions","clicks","cost"],
  "startDate":"2026-04-27","endDate":"2026-05-03",
  "timeUnit":"DAILY"}'

# 2. SP 搜索词 + 多归因窗口 + 过滤仅看关键词匹配
python get_report.py '{"profileId":1111111111,"region":"NA",
  "reportTypeId":"spSearchTerm",
  "adProduct":"SPONSORED_PRODUCTS",
  "groupBy":["searchTerm"],
  "columns":["searchTerm","keyword","matchType","impressions","clicks","cost",
             "sales7d","sales14d","sales30d",
             "purchases7d","purchases14d","purchases30d",
             "acosClicks14d","roasClicks14d","startDate","endDate"],
  "startDate":"2026-04-01","endDate":"2026-04-30",
  "timeUnit":"SUMMARY",
  "filters":[{"field":"keywordType","values":["BROAD","PHRASE","EXACT"]}]}'

# 3. SP 投放商品 + 长时间等待 + 不启本机 HTTP
python get_report.py '{"profileId":1111111111,"region":"NA",
  "reportTypeId":"spAdvertisedProduct",
  "adProduct":"SPONSORED_PRODUCTS",
  "groupBy":["advertiser"],
  "columns":["advertisedAsin","advertisedSku","impressions","clicks","cost",
             "sales7d","acosClicks7d","roasClicks7d","startDate","endDate"],
  "startDate":"2026-04-01","endDate":"2026-04-30",
  "timeUnit":"SUMMARY",
  "maxAttempts":60,"pollInterval":20,"serveExtractedFileHttp":false}'

# 4. 仅轮询一个已有 reportId（救回上次超时）
python get_report.py '{"profileId":1111111111,"region":"NA",
  "reportId":"7df1ef5d-45ba-40cc-b607-ff2148cf4f5e",
  "maxAttempts":60,"pollInterval":30}'
```

---

## Feedback API

与上面的工具 API **base URL 不同**：

```bash
curl -X POST https://skill-api.linkfox.com/api/v1/public/feedback \
  -H "Content-Type: application/json" \
  -d '{"skillName":"linkfox-amazon-ads-report","sentiment":"POSITIVE",
       "category":"OTHER","content":"报告拉取顺利"}'
```

- `sentiment`: `POSITIVE` / `NEUTRAL` / `NEGATIVE`
- `category`: `BUG` / `COMPLAINT` / `SUGGESTION` / `OTHER`
