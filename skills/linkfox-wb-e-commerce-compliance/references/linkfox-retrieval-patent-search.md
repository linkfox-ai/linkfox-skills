# linkfox-retrieval-patent-search

## MCP 调用

| 项 | 值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `zhihuiya/querySearchPatent` |
| `arguments` | 直接使用本 reference 的请求参数对象，不包裹 `body`、`params` 或 `data` |

```json
{
  "toolName": "zhihuiya/querySearchPatent",
  "arguments": {
    "queryText": "TACD: virtual reality",
    "limit": 10,
    "offset": 0
  }
}
```

`toolName` 精确匹配且区分大小写。WorkBuddy 自动注入 Authorization；禁止在 MCP 配置或 `arguments` 中加入 headers、API Key、token、JWT、手机号或其他凭证。MCP 或 `proxy_call` 缺失时停止，禁止 curl、`urllib`、`requests`、`httpx` 或脚本直连工具网关，也不 HTTP fallback。

先检查 MCP/schema/`isError`，再读取 structured content 或只解析一次 text JSON，然后检查下游 `errcode`、`errorCode`、`code`、`errmsg` 或 `msg`，最后读取业务字段。失败、空结果或结果不理想时不自动重试；同一任务内相同 `toolName + arguments` 不重复调用。

## 来源响应字段表

来源：`skills/linkfox-zhihuiya-retrieval-patent-search/references/api.md` 的响应字段章节。仅转录响应字段，未引入来源的请求、调用、认证、错误、成本或工作流内容。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | 200 表示成功 |
| `errmsg` | string | `ok` 表示成功，否则为错误描述 |
| `total` | integer | 本次返回结果数 |
| `data` | array | 专利列表 |
| `columns` | array | 渲染的列（仅渲染元信息，非数据记录，长度可能与 `data` 不一致） |
| `type` | string | 渲染的样式（如 `tableListWorkbenches`） |
| `costToken` | integer | 消耗token |
| `allRecordsCount` | integer | 检索命中总数 |
| `data[].patentId` | string | 智慧芽专利 ID |
| `data[].pn` | string | 公开（公告）号 |
| `data[].title` | string | 专利标题 |
| `data[].apdt` | integer | 申请日（YYYYMMDD） |
| `data[].pbdt` | integer | 公开日（YYYYMMDD） |
| `data[].apno` | string | 申请号 |
| `data[].authority` | string | 受理局（如 `US`） |
| `data[].inventor` | string | 发明人（多人以 `\|` 分隔） |
| `data[].originalAssignee` | string | 原始申请人（多个以 `\|` 分隔） |
| `data[].currentAssignee` | string | 当前申请人（多个以 `\|` 分隔） |



以下归档该子能力的执行说明与 API 细节，按统一 WorkBuddy 路由调用。

## 执行说明

---
name: linkfox-retrieval-patent-search
description: 通过 Analytics 检索式（如 TACD: 关键词）在专利数据服务专利数据库中检索专利列表，返回专利ID、公开号及命中总数。当用户提到专利检索式检索、专利表达式搜索、Analytics检索式、TACD检索、专利关键词检索、检索式查专利、专利语义检索、patent expression search, patent query syntax, Analytics query, TACD search, 专利数据服务, 专利数据服务专利检索时触发此技能。即使用户未明确提及"检索式"或"专利数据服务"，只要用户希望用检索式/表达式语法在专利库中检索专利列表，也应触发此技能。
---

# patent-data Patent Expression Search

This skill searches the patent-data (专利数据服务) patent database using an Analytics query expression (e.g. `TACD: virtual reality`), returning a list of matching patents with their patent IDs and publication numbers, plus the total hit count.

## Core Concepts

**Expression-based patent search** uses patent-data's Analytics query syntax to retrieve patents matching a field-scoped boolean expression. Unlike image-based search, this is a text query against the full patent corpus.

**Query expression (`queryText`)** holds an Analytics expression. Common field-scoped syntax:

| Syntax | Scope |
|--------|-------|
| `TACD: <term>` | Title + Abstract + Claims + Description |
| `TAC: <term>` | Title + Abstract + Claims |
| `TA: <term>` | Title + Abstract |
| `AND` / `OR` / `NOT` | Boolean operators (combine terms/fields) |

> This skill returns a **list** of patents (`patentId` + `pn`). To retrieve detailed bibliographic data, full text, legal status, family, or images for a specific patent, feed the returned `patentId`/`pn` into the corresponding `linkfox-bibliography` / `linkfox-simple-bibliography` / `linkfox-legal-status` / `linkfox-patent-family` skills.

## Data Fields

Each `data[]` item (one matching patent):

| Field | Description |
|-------|-------------|
| patentId | patent-data internal patent ID |
| pn | Publication (announcement) number |
| title | Patent title |
| apdt | Application date (integer, YYYYMMDD) |
| pbdt | Publication date (integer, YYYYMMDD) |
| apno | Application number |
| authority | Patent office / authority (e.g. `US`) |
| inventor | Inventor(s), pipe-separated |
| originalAssignee | Original applicant(s), pipe-separated |
| currentAssignee | Current assignee(s), pipe-separated |

Top-level fields:

| Field | Description |
|-------|-------------|
| data | 专利列表（每项含上表 10 个字段） |
| total | Number of records returned in this response |
| allRecordsCount | Total hits matching the query expression |
| costToken | Token cost for this query |
| columns | Render metadata (display hints, not data records) |
| type | Render style (e.g. `tableListWorkbenches`) |
| errcode | `200` on success |
| errmsg | `ok` on success |

> The top-level `columns` array is render metadata and may be longer than the real `data` list — do not treat it as data.

## Parameter Guide

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| queryText | Yes | - | Analytics 检索式，最大 12000 字符 |
| limit | No | 10 | 返回专利个数，1–1000 |
| offset | No | 0 | 偏移量，0–19999；`limit + offset` ≤ 20000 |
| sort | No | - | 排序数组，元素 `{field, order}` |
| stemming | No | 0 | 截词检索：`1` 开启 / `0` 关闭，默认关闭 |
| collapseType | No | ALL | 去重方式：ALL / APNO / DOCDB / INPADOC / EXTEND |
| collapseBy | No | - | 去重排序字段：APD / PBD / AUTHORITY / SCORE |
| collapseOrder | No | - | 去重排序顺序：OLDEST / LATEST |
| collapseOrderAuthority | No | - | 受理局优先级数组（仅 `collapseBy=AUTHORITY` 时有效），按输入顺序保留对应专利 |

### Sort object

| `field` | Meaning |
|---------|---------|
| PBDT_YEARMONTHDAY | Publication date |
| APD_YEARMONTHDAY | Application date |
| ISD | Issue / grant date |
| SCORE | Query relevance |

`order`: `DESC` or `ASC`. Example: `[{"field":"SCORE","order":"DESC"}]`.

### Collapse (deduplication)

| `collapseType` | Description |
|----------------|-------------|
| ALL | No dedup |
| APNO | By application number |
| DOCDB | By simple family |
| INPADOC | By INPADOC family |
| EXTEND | By 专利数据服务 extended family |

`collapseBy` selects which representative record to keep (APD/PBD/AUTHORITY/SCORE); `collapseOrder` picks OLDEST or LATEST.

## Usage Examples

**1. Basic expression search**
```
检索 TACD: virtual reality 的专利，返回 10 条
```
Action: `{"queryText": "TACD: virtual reality", "limit": 10}`

**2. Sort by relevance**
```
用检索式 TACD: drone AND camera 查专利，按相关性排序
```
Action: `{"queryText": "TACD: drone AND camera", "sort": [{"field": "SCORE", "order": "DESC"}]}`

**3. Paginate**
```
翻到第 2 页，每页 10 条
```
Action: `{"queryText": "TACD: virtual reality", "offset": 10, "limit": 10}`

**4. Dedup by DOCDB family**
```
检索 TACD: virtual reality，按简单同族去重，保留最新
```
Action: `{"queryText": "TACD: virtual reality", "collapseType": "DOCDB", "collapseBy": "APD", "collapseOrder": "LATEST"}`

## Display Rules

1. **Present results as a table**: show `pn`, `title`, `apdt`/`pbdt` (format as dates), `inventor`, `currentAssignee`, `authority` per item.
2. **Show totals**: always state `allRecordsCount` (total hits) and the current page range (`offset`–`offset+limit`).
3. **Default sort**: if the user does not specify a sort, actively inject `{"field": "SCORE", "order": "DESC"}` so results are relevance-ordered; respect any sort the user explicitly requests.
4. **Large result sets**: present a summary table first, note the total, and offer to expand specific patents.
5. **Expand via sibling skills**: to get full metadata for a patent, direct the user to `linkfox-bibliography` / `linkfox-simple-bibliography`; do not re-query this search skill for details.
6. **No fabrication**: only display fields actually present in the response; never invent titles, dates, or assignees not returned.

## Important Limitations

- **`queryText` is required** and must be a valid Analytics expression. Missing it returns `errcode 400`.
- **Paging ceiling**: `limit + offset` must be ≤ 20000; `limit` max 1000; `offset` max 19999.
- **List-only output**: this skill returns `patentId` + `pn` (and basic fields). Full bibliographic/full-text/legal data must be fetched via dedicated `the dedicated references` skills.
- **No auto-retry on empty/error**: if the query returns no hits or an error, do not automatically swap keywords or rewrite the expression; confirm with the user first (each call costs credits).
- **Permission/quota**: a `501 "No permission or API package quota"` response means the current key lacks the query-search permission/quota. This is a permission/package issue (not merely low balance) and **cannot be resolved by recharging alone** — do not retry; surface it to the user to open/enable the query-search API package.

## User Expression & Scenario Quick Reference

**Applicable** — Find patents by query expression:

| User Says | Scenario |
|-----------|----------|
| "检索 TACD: virtual reality 的专利" | Basic expression search |
| "用检索式查虚拟现实相关专利" | Expression search |
| "检索式：TAC AND camera" | Boolean expression |
| "按公开日排序检索" | Sorted search |
| "按简单同族去重" | Deduplicated search |
| "翻到第 2 页" | Pagination |

**Not applicable** — Needs beyond expression search:

- Bibliographic detail of a known patent ID/number (use `linkfox-bibliography`)
- Image-based patent search (use `linkfox-patent-image-search`)
- Legal status / family / full-text / PDF (use dedicated `the dedicated references` skills)

**Boundary judgment**: When the user already has a patent ID or publication number and wants its metadata → use the bibliography skill. When the user wants to **discover** patents matching a query expression → this skill.

## 积分消耗规则

按动态规则计费：消耗积分 = 3 × 返回data条数。每条为 1 条检索式检索专利结果

> **重要**：本技能的服务按倍数动态计算，返回条数越多消耗越大，必须提醒用户，由用户决定是否继续。优先用较小的 `limit` 验证检索式命中，确认后再决定是否扩大范围或翻页。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*



## API 参考

# 专利数据服务-检索式专利检索 API 参考

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| queryText | string | 是 | Analytics 检索式，最大 12000 字符。支持字段前缀语法（如 `TACD:`、`TAC:`、`TA:`）与布尔运算（`AND`/`OR`/`NOT`）。 |
| limit | integer | 否 | 返回专利个数，范围 1–1000，默认 10 |
| offset | integer | 否 | 偏移量，范围 0–19999，默认 0；`limit + offset` 不能超过 20000 |
| sort | array | 否 | 排序条件数组，每个元素 `{field, order}`。`field` 取 `PBDT_YEARMONTHDAY`/`APD_YEARMONTHDAY`/`ISD`/`SCORE`；`order` 取 `DESC`/`ASC` |
| stemming | integer | 否 | 是否开启截词检索：`1` 开启 / `0` 关闭，默认关闭 |
| collapseType | string | 否 | 专利去重条件，不传默认 `ALL`。取值：`ALL`（不去重）、`APNO`（按申请号去重）、`DOCDB`（按简单同族去重）、`INPADOC`（按 INPADOC 同族去重）、`EXTEND`（按 专利数据服务 同族去重） |
| collapseBy | string | 否 | 专利去重排序字段：`APD`（申请日）/`PBD`（公开日）/`AUTHORITY`（受理局）/`SCORE`（相关性） |
| collapseOrder | string | 否 | 专利去重排序顺序：`OLDEST`（最早）/`LATEST`（最新） |
| collapseOrderAuthority | array | 否 | 受理局优先级数组（仅当 `collapseBy=AUTHORITY` 时有效），按输入顺序的受理局优先级保留对应专利 |

> `queryText` 为必填项；缺失时网关返回 `errcode: 400, errmsg: "queryText 为必填项"`。

> **检索式示例**：`TACD: virtual reality`（在标题/摘要/权利要求/说明书中检索 "virtual reality"）；`TAC: drone AND camera`（标题/摘要/权利要求中同时包含 drone 与 camera）。

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errcode 字段区分（errcode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errcode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析 `data`、`allRecordsCount` 等业务字段 |
| 400 | 参数错误 | 检查 `queryText` 是否提供、`limit`/`offset` 范围是否合法 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理 |
| 402 | 积分不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理 |
| 501 | 无权限或套餐配额耗尽 | `errmsg` 含 "No permission or API package quota has exceeded the limit"：当前 Key 未开通检索式检索专利权限或配额已用尽。属权限/套餐问题（非单纯余额不足），**充值无法解决**，**不要重试**，提示用户开通/启用检索式检索专利 API 套餐后重试 |
| 其他非200值 | 业务异常 | 参考 `errmsg` 字段获取具体错误原因 |

错误响应示例：

缺少 `queryText`：

```json
{"errcode": 400, "errmsg": "queryText 为必填项"}
```

无权限或配额耗尽：

```json
{"errcode": 501, "errmsg": "检索式检索专利失败: No permission or API package quota has exceeded the limit!"}
```

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-retrieval-patent-search",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

**Field rules:**
- `skillName`: Use this skill's `name` from the YAML frontmatter
- `sentiment`: Choose ONE — `POSITIVE` (praise), `NEUTRAL` (suggestion without emotion), `NEGATIVE` (complaint or error)
- `category`: Choose ONE — `BUG` (malfunction or wrong data), `COMPLAINT` (user dissatisfaction), `SUGGESTION` (improvement idea), `OTHER`
- `content`: Include what the user said or intended, what actually happened, and why it is a problem or praise
