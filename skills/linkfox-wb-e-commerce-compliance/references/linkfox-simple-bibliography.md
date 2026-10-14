# linkfox-simple-bibliography

## MCP 调用

| 项 | 值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `zhihuiya/simpleBibliography` |
| `arguments` | 直接使用本 reference 的请求参数对象，不包裹 `body`、`params` 或 `data` |

```json
{
  "toolName": "zhihuiya/simpleBibliography",
  "arguments": {
    "patentNumber": "US20230012345A1"
  }
}
```

`toolName` 精确匹配且区分大小写。WorkBuddy 自动注入 Authorization；禁止在 MCP 配置或 `arguments` 中加入 headers、API Key、token、JWT、手机号或其他凭证。MCP 或 `proxy_call` 缺失时停止，禁止 curl、`urllib`、`requests`、`httpx` 或脚本直连工具网关，也不 HTTP fallback。

先检查 MCP/schema/`isError`，再读取 structured content 或只解析一次 text JSON，然后检查下游 `errcode`、`errorCode`、`code`、`errmsg` 或 `msg`，最后读取业务字段。失败、空结果或结果不理想时不自动重试；同一任务内相同 `toolName + arguments` 不重复调用。

## 来源响应字段表

来源：`skills/linkfox-zhihuiya-simple-bibliography/references/api.md` 的响应字段章节。仅转录响应字段，未引入来源的请求、调用、认证、错误、成本或工作流内容。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `total` | integer | 记录数 |
| `allRecordsCount` | integer | 总记录数 |
| `data` | array | 著录项列表（详见下方数据字段说明） |
| `columns` | array | 渲染的列定义 |
| `type` | string | 渲染的样式 |
| `costToken` | integer | 消耗token |
| `data[].patentId` | string | 专利ID |
| `data[].title` | string | 专利标题 |
| `data[].abstractContent` | string | 专利摘要 |
| `data[].publicationNumber` | string | 公开号 |
| `data[].pn` | string | 公开公告号 |
| `data[].country` | string | 国家代码 |
| `data[].publicationCountry` | string | 公开国家 |
| `data[].publicationDate` | string | 公开日期 |
| `data[].publicationKind` | string | 公开类型代码 |
| `data[].patentType` | string | 专利类型（发明、实用新型、外观设计等） |
| `data[].kind` | string | 专利类型代码 |
| `data[].applicationNo` | string | 申请号 |
| `data[].applicationDate` | string | 申请日期 |
| `data[].applicants` | array | 申请人列表 |
| `data[].inventors` | array | 发明人列表 |
| `data[].assignees` | array | 专利权人列表 |
| `data[].assigneeAddresses` | array | 专利权人地址列表 |
| `data[].ipcMain` | string | IPC主分类号 |
| `data[].ipcFurther` | array | IPC副分类号列表 |
| `data[].cpcMain` | string | CPC主分类号 |
| `data[].cpcFurther` | array | CPC副分类号列表 |
| `data[].loc` | array | LOC分类号列表 |
| `data[].gbc` | array | GBC分类号列表 |
| `data[].priorityClaims` | array | 优先权声明列表 |
| `data[].pctApplicationNo` | string | PCT申请号 |
| `data[].pctFilingDate` | string | PCT申请日期 |
| `data[].pctEntryDate` | string | PCT进入日期 |
| `data[].citedPatents` | array | 引用专利列表 |
| `data[].citedNonPatents` | array | 引用非专利文献列表 |



以下归档该子能力的执行说明与 API 细节，按统一 WorkBuddy 路由调用。

## 执行说明

---
name: linkfox-simple-bibliography
description: 从专利数据服务专利数据库查询专利简要著录（书目）数据。当用户提到专利著录信息查询、专利基本信息获取、专利书目数据、专利公开详情、按专利号查询发明人、专利申请人信息、专利摘要获取、专利分类号（IPC/CPC）、专利引用查询或任何通过专利ID、公开号检索结构化元数据的请求、patent brief bibliography, patent basic info, patent number lookup, patent abstract, 专利数据服务, patent metadata时触发此技能。即使用户未明确提及"专利数据服务"或"著录信息"，只要其需求涉及查询特定专利的核心著录字段，也应触发此技能。
---

# patent-data Patent Simple Bibliography

This skill guides you on how to query simple bibliographic data for patents using the patent-data patent database, helping users retrieve structured patent metadata efficiently.

## Core Concepts

The patent-data Simple Bibliography tool retrieves basic bibliographic (front-page) information for patents. Given one or more patent IDs or publication numbers, it returns structured metadata including title, abstract, applicants, inventors, assignees, classification codes, filing dates, priority claims, and citation references.

**Lookup modes**: You can look up patents by either `patentId` (patent-data internal patent ID) or `patentNumber` (public publication/grant number). If both are supplied, `patentId` takes priority. Multiple values are separated by commas, with a maximum of 100 per request.

## Parameter Guide

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| patentId | string | Conditionally | patent-data internal patent ID. Comma-separated for multiple values, max 100. At least one of `patentId` or `patentNumber` must be provided. |
| patentNumber | string | Conditionally | Public publication/grant number (e.g., `US11234567B2`, `CN115000000A`). Comma-separated for multiple values, max 100. At least one of `patentId` or `patentNumber` must be provided. |

**Priority rule**: When both `patentId` and `patentNumber` are present, the API uses `patentId` and ignores `patentNumber`.

## Response Data Fields

| Field | API Name | Description |
|-------|----------|-------------|
| Patent ID | patentId | patent-data internal patent identifier |
| Title | title | Patent title |
| Abstract | abstractContent | Patent abstract text |
| Publication Number | publicationNumber | Publication number |
| Publication/Grant Number | pn | Full publication/grant number |
| Country Code | country | Country code of the patent |
| Publication Country | publicationCountry | Country where the patent was published |
| Publication Date | publicationDate | Publication date |
| Publication Kind | publicationKind | Kind code of the publication |
| Patent Type | patentType | Type of patent (e.g., invention, utility model, design) |
| Kind Code | kind | Patent kind code |
| Application Number | applicationNo | Application number |
| Application Date | applicationDate | Application filing date |
| Applicants | applicants | List of applicants |
| Inventors | inventors | List of inventors |
| Assignees | assignees | List of patent assignees/owners |
| Assignee Addresses | assigneeAddresses | List of assignee addresses |
| IPC Main | ipcMain | Main IPC classification code |
| IPC Further | ipcFurther | Additional IPC classification codes |
| CPC Main | cpcMain | Main CPC classification code |
| CPC Further | cpcFurther | Additional CPC classification codes |
| LOC | loc | Locarno classification codes (design patents) |
| GBC | gbc | GBC classification codes |
| Priority Claims | priorityClaims | List of priority claim entries |
| PCT Application No | pctApplicationNo | PCT international application number |
| PCT Filing Date | pctFilingDate | PCT international filing date |
| PCT Entry Date | pctEntryDate | PCT national phase entry date |
| Cited Patents | citedPatents | List of cited patent references |
| Cited Non-Patents | citedNonPatents | List of cited non-patent literature |

## Usage Examples

**1. Look up a single patent by publication number**
```
User: "Show me the bibliographic info for patent US11234567B2."
Action: Call with patentNumber = "US11234567B2"
```

**2. Look up multiple patents by publication number**
```
User: "Get the basic info for CN115000000A, EP4000000A1, and JP2023100000A."
Action: Call with patentNumber = "CN115000000A,EP4000000A1,JP2023100000A"
```

**3. Look up patents by patent-data patent ID**
```
User: "Retrieve bibliography for patent IDs abc123 and def456."
Action: Call with patentId = "abc123,def456"
```

**4. Retrieve inventor and applicant information**
```
User: "Who are the inventors and applicants for patent US20230001234A1?"
Action: Call with patentNumber = "US20230001234A1", then extract the inventors and applicants fields from the response.
```

**5. Check patent classification codes**
```
User: "What IPC and CPC codes does patent EP3999999B1 have?"
Action: Call with patentNumber = "EP3999999B1", then present ipcMain, ipcFurther, cpcMain, and cpcFurther from the response.
```

**6. Get patent abstract and citation references**
```
User: "Show me the abstract and cited patents for CN114000000B."
Action: Call with patentNumber = "CN114000000B", then display abstractContent and citedPatents.
```

## Display Rules

1. **Present data clearly**: Show bibliographic results in well-structured tables or grouped sections. For a single patent, use a key-value layout. For multiple patents, use a table with the most relevant columns.
2. **Selective display**: When results contain many fields, prioritize showing title, publication number, applicants, inventors, application date, publication date, IPC/CPC main codes, and abstract. Show additional fields only when the user specifically asks.
3. **List fields**: For array fields (inventors, applicants, assignees, classification codes, citations), present them as comma-separated values or bulleted lists depending on length.
4. **Empty fields**: Omit fields that are null or empty from the display rather than showing blank entries.
5. **Error handling**: When a query fails, explain the reason based on the error message and suggest the user verify the patent number or ID format.
6. **Batch result notice**: When querying many patents at once, remind the user that the maximum is 100 per request.
## Important Limitations

- **Maximum batch size**: Up to 100 patent IDs or publication numbers per request.
- **At least one identifier required**: Either `patentId` or `patentNumber` must be provided; omitting both will cause an error.
- **patentId takes priority**: If both parameters are supplied, only `patentId` is used.
- **Data scope**: This tool returns simple bibliographic data only. It does not return full-text claims, detailed descriptions, legal status, or patent family information.

## User Expression & Scenario Quick Reference

**Applicable** -- Patent bibliographic data retrieval:

| User Says | Scenario |
|-----------|----------|
| "Look up patent XX" / "Get info for patent XX" | Single patent bibliography lookup |
| "Who invented patent XX" / "Who is the applicant" | Inventor / applicant retrieval |
| "What's the IPC code for XX" / "Classification of XX" | Classification code lookup |
| "Show me the abstract of XX" | Abstract retrieval |
| "When was patent XX filed" / "Publication date of XX" | Date information lookup |
| "What patents does XX cite" | Citation reference lookup |
| "Get bibliographic data for these patents: A, B, C" | Batch bibliography query |
| "Patent basic info" / "Patent front page data" | General bibliography retrieval |

**Not applicable** -- Needs beyond simple bibliographic data:

- Full-text patent claims or detailed description
- Patent legal status or prosecution history
- Patent family / equivalents analysis
- Patent valuation or landscaping
- Freedom-to-operate or infringement analysis
- Patent search by keyword or semantic query (this tool requires specific patent identifiers)

## 积分消耗规则

按动态规则计费：消耗积分 = 81 × 返回data条数。每条为 1 条简版专利著录项结果

> **重要**：本技能的服务按倍数动态计算，可能一次性消耗大量积分，必须提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*



## API 参考

# 专利数据服务简单著录项 API 参考

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| patentId | string | 条件必填 | 专利ID（专利ID和公开号两个参数必须要有一个，如果两个都存在，会优先使用专利ID）。多个专利ID之间用英文逗号 `,` 隔开，最大支持100个 |
| patentNumber | string | 条件必填 | 公开公告号（专利ID和公开号两个参数必须要有一个，如果两个都存在，会优先使用专利ID）。多个公开公告号之间用英文逗号 `,` 隔开，最大支持100个 |


## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errorCode 字段区分（errorCode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errorCode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析业务字段 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 402 | - | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 其他非200值 | 业务异常 | 参考 `errmsg` 字段获取具体错误原因 |

错误响应示例：

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-xxx-xxx",
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

