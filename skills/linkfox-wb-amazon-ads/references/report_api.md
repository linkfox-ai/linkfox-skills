


## MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`amazonAds/developerProxy`
- `arguments` 直接传共享代理业务对象，保留 `region`、`profileId`、`path`、`method`、`body`、`contentType`；不得额外包裹。
- WorkBuddy 自动注入 Authorization；禁止 `headers`、API Key、token 或 JWT。禁止 HTTP fallback。
- 同一任务相同 `toolName + arguments` 不重复调用。失败、空结果和未完成状态不自动重建报告。
- 先检查 MCP schema、`isError` 和代理错误；text JSON 只解析一次，再检查 `httpStatus` / `body` 及 Amazon 状态。

```json
{"toolName":"amazonAds/developerProxy","arguments":{"region":"NA","profileId":1234567890,"path":"reporting/reports","method":"POST","body":"{\"name\":\"SP campaign report\",\"startDate\":\"2026-08-01\",\"endDate\":\"2026-08-07\",\"configuration\":{\"adProduct\":\"SPONSORED_PRODUCTS\",\"groupBy\":[\"campaign\"],\"columns\":[\"campaignId\",\"impressions\",\"clicks\",\"cost\"],\"reportTypeId\":\"spCampaigns\",\"timeUnit\":\"SUMMARY\",\"format\":\"GZIP_JSON\"}}","contentType":"application/vnd.createasyncreportrequest.v3+json"}}
```
状态查询示例：

```json
{"toolName":"amazonAds/developerProxy","arguments":{"region":"NA","profileId":1234567890,"path":"reporting/reports/REPORT_ID","method":"GET","body":"","contentType":"application/json"}}
```

# linkfox-amazon-ads-report — 参数与字段参考

Amazon Ads 报告自动化获取（SP / SB 覆盖；SD / ST / DSP 暂未覆盖）。授权见 `linkfox-amazon-ads-auth`；广告管理见 `linkfox-amazon-ads-manager`。

> **报告类型真相源**：`report_types_index.md` 及同目录的 `report_types_<sp|sb|sd>_<reportTypeId>.md` 文件。每个文件保留完整 columns / groupBy / filters / timeUnit / 日期约束。

## 支持的报告类型

完整列表见 `report_types_index.md`。常用快速索引：

| reportTypeId | 业务含义 | 文件 |
|--------------|---------|------|
| `spCampaigns` | 广告活动级（SP） | `report_types_sp_spCampaigns.md` |
| `spAdvertisedProduct` | 投放商品级（SP） | `report_types_sp_spAdvertisedProduct.md` |
| `spSearchTerm` | 搜索词级（SP） | `report_types_sp_spSearchTerm.md` |
| `spTargeting` | 定向/关键词级（SP） | `report_types_sp_spTargeting.md` |
| `sbCampaigns` / `sbAdGroup` / `sbAds` / ... | Sponsored Brands | `report_types_sb_*.md` |

## 输入参数

MCP 链路分为创建和状态查询两个独立调用。创建需要下表字段；状态查询只需要 `profileId`、`region` 与已有 `reportId`。同一任务不重复执行相同状态查询，未完成时返回 reportId，等待用户后续明确继续。

### 必填（全链路模式）

| 参数 | 类型 | 说明 |
|------|------|------|
| `profileId` | number | 从 ads-auth 获取 |
| `region` | string | `NA` / `EU` / `FE` |
| `reportTypeId` | string | 见 `report_types_index.md` |
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

### 状态查询参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `profileId` | number | 是 | 创建报告时使用的 profile |
| `region` | string | 是 | `NA` / `EU` / `FE` |
| `reportId` | string | 是 | 创建响应返回的报告 ID |

旧入口的本地轮询、依赖检查、下载服务和缓存控制项不得放进 `proxy_call.arguments`；MCP 新链路不提供对应本地服务。

## 日期限制

- **跨度上限**：以对应 `.md` 文件 frontmatter 的 `dateRange.maxSpanDays` 为准（多数 31 天；`sbPurchasedProduct` 731 天；GrossAndInvalids 系列 365 天）。超出返回 HTTP 400 `"must not exceed maximum range"`。
- **回溯上限**：以 `dateRange.dataRetentionDays` 为准（SP 多为 95 天，SB 60 天）。
- **数据延迟**：~12 小时；建议 `endDate <= 昨天`。

## 各报告类型的列

每个 reportTypeId 的完整 Base metrics、allowed groupBy、filters 枚举值，统一在对应 `report_types_<sp|sb|sd>_<reportTypeId>.md` 中维护：

- `.md` 的 **frontmatter** 提供 `adProduct` / `groupBy` / `timeUnit`（可选值）/ `format` / `filters` / `dateRange`
- **Base metrics 表**列出此报告类型支持的**全部列名**；按业务需要选子集

归因窗口后缀约定：`_1d` / `_7d` / `_14d` / `_30d` 表示 1/7/14/30 天归因窗口（点击或曝光归因的销售额、订单量、件数等）。具体每个字段支持哪些窗口，以对应 `.md` 文件的 Base metrics 表为准（不是所有字段都有全部 4 个窗口版本）。

## 工作流与输出

MCP 流程：创建报告 → 从 Amazon 响应体读取并保存 `reportId` → 在用户要求查询时调用状态 endpoint → `COMPLETED` 后读取响应中的下载资源。每个状态查询都是独立收费调用，不自动轮询；`PENDING` / `PROCESSING` 表示仍在生成，不得自动重建报告。WorkBuddy 自动处理 MCP Authorization。

来源明确的 Amazon 状态为 `PENDING` / `PROCESSING` / `COMPLETED` / `FAILED`。旧入口额外合成的状态、自动轮询、下载、解压、落盘、本机 HTTP 服务及恢复参数均不是下游响应。

## 错误码

| httpStatus / 状态 | 含义 | 建议 |
|-------------------|------|------|
| 200 | 请求成功 | 解析 `body`；创建时保存 `reportId`，完成后使用 Amazon 返回的资源信息 |
| 400 | 入参错（日期超限 / reportTypeId 非法 / columns 不适配） | 按 `detail` 修正 |
| 401 | accessToken 过期 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 402 | 积分或余额不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 403 | profileId 无权限 | 核对 profileId |
| 404 | reportId 不存在或已过期 | 重新发起报告 |
| 422 | columns / groupBy 与 reportTypeId 不适配 | 对照对应 `report_types_*.md` 的 Base metrics / frontmatter 核对 |
| 425 | 同参数已有报告请求 | 展示原始响应；仅在响应明确提供旧 `reportId` 时由用户决定是否查询，不自动解析并续调 |
| 429 | 限流（来源说明约 30 req/min/profile） | 不密集重试；等待后由用户决定是否发起新调用 |
| `status=FAILED` | 上游生成失败 | 看 `failureReason` |
| `status=PENDING/PROCESSING` | Amazon 仍在生成 | 保存 `reportId`，等待用户后续明确要求再查询 |

---

## Feedback API

与上面的工具 API **base URL 不同**：



- `sentiment`: `POSITIVE` / `NEUTRAL` / `NEGATIVE`
- `category`: `BUG` / `COMPLAINT` / `SUGGESTION` / `OTHER`



## 响应字段表

来源：`skills/linkfox-amazon-ads-report/references/api.md`。该来源的“成功响应”和“未完成响应”是旧 caller 合成结构，不是 `developerProxy` 下游响应，故不纳入。来源只明确提及以下 Amazon 业务字段，但没有完整说明它们在 `body` 内的固定嵌套位置；不得自行推导。

| 响应字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | number | developerProxy 下游 HTTP 状态 |
| `body` | string/object | Amazon 原始响应体；完整嵌套属性来源未说明 |
| `error` | string | 代理错误摘要 |
| `details` | string/object | 错误详情；来源未说明内部固定结构 |

来源明确提及 Amazon 业务字段 `reportId`、`status`、`failureReason` 和完成后的预签名资源 URL，但未定义它们在 `body` 中的固定父对象与全部属性，因此不推测字段路径。
