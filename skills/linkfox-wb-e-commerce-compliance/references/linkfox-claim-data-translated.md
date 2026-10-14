# linkfox-claim-data-translated

## MCP 调用

| 项 | 值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `zhihuiya/claimDataTranslated` |
| `arguments` | 直接使用本 reference 的请求参数对象，不包裹 `body`、`params` 或 `data` |

```json
{
  "toolName": "zhihuiya/claimDataTranslated",
  "arguments": {
    "patentNumber": "CN115000000A",
    "lang": "en"
  }
}
```

`toolName` 精确匹配且区分大小写。WorkBuddy 自动注入 Authorization；禁止在 MCP 配置或 `arguments` 中加入 headers、API Key、token、JWT、手机号或其他凭证。MCP 或 `proxy_call` 缺失时停止，禁止 curl、`urllib`、`requests`、`httpx` 或脚本直连工具网关，也不 HTTP fallback。

先检查 MCP/schema/`isError`，再读取 structured content 或只解析一次 text JSON，然后检查下游 `errcode`、`errorCode`、`code`、`errmsg` 或 `msg`，最后读取业务字段。失败、空结果或结果不理想时不自动重试；同一任务内相同 `toolName + arguments` 不重复调用。

## 来源响应字段表

来源：`skills/linkfox-zhihuiya-claim-data-translated/references/api.md` 的响应字段章节。仅转录响应字段，未引入来源的请求、调用、认证、错误、成本或工作流内容。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `total` | integer | 记录数 |
| `data` | array | 专利列表（详见下方） |
| `columns` | array | 渲染的列定义 |
| `costToken` | integer | 消耗token |
| `type` | string | 渲染的样式 |
| `data[].patentId` | string | 专利ID |
| `data[].pn` | string | 公开(公告)号 |
| `data[].pnRelated` | string | 替代专利的公开号（仅当使用同族专利替代时提供） |
| `data[].claims` | string | 权利要求翻译文本 |



以下归档该子能力的执行说明与 API 细节，按统一 WorkBuddy 路由调用。

## 执行说明

---
name: linkfox-claim-data-translated
description: 从专利数据服务专利数据库获取翻译后的专利权利要求。当用户询问专利权利要求、权利要求翻译、查看特定语言（中文、英文或日文）的权利要求、通过专利ID或公开号查询专利权利、分析权利要求文本、claim translation, patent claim translation, 专利数据服务, patent translation时触发此技能。即使用户未明确提及"翻译版权利要求"，只要其需求涉及获取特定语言的专利权利要求内容，也应触发此技能。
---

# patent-data Patent Claims (Translated)

This skill guides you on how to query translated patent claims from the patent-data (专利数据服务) patent database, enabling users to retrieve claim texts in Chinese, English, or Japanese for one or more patents.

## Core Concepts

Patent claims define the legal scope of protection granted by a patent. This tool retrieves the **translated text** of patent claims, supporting three languages: Chinese (`cn`), English (`en`), and Japanese (`jp`). You can look up patents by their internal patent ID or by their publication (announcement) number.

**Family patent substitution**: When claims are unavailable for a specific patent, the tool can optionally substitute claims from a related family patent. This is controlled by the `replaceByRelated` parameter.

## Data Fields

| Field | API Name | Description | Example |
|-------|----------|-------------|---------|
| Patent ID | patentId | Internal patent identifier | 84a1b2c3-... |
| Publication Number | pn | Publication (announcement) number of the patent | CN112345678A |
| Related Publication Number | pnRelated | Publication number of the substitute family patent (only present when family substitution is used) | US20210012345A1 |
| Claims | claims | Translated patent claim text | 1. A method for... |

## Supported Languages

| Code | Language |
|------|----------|
| en | English (default) |
| cn | Chinese |
| jp | Japanese |

Default language is **en** (English). Use English when the user does not specify a language.

## Parameter Guide

### Patent Identification

You must provide **at least one** of the following:

- **patentId** -- The internal patent ID. When both `patentId` and `patentNumber` are provided, `patentId` takes precedence. Multiple values separated by commas, up to 100 patents per request.
- **patentNumber** -- The publication or announcement number. Multiple values separated by commas, up to 100 patents per request.

### Optional Parameters

- **lang** -- Target translation language: `en` (English, default), `cn` (Chinese), or `jp` (Japanese).
- **replaceByRelated** -- Whether to substitute claims from a family patent when the original claims are unavailable: `1` = yes, `0` = no (default).

## Usage Examples

**1. Get English claims for a single patent by publication number**
```
patentNumber: "CN112345678A"
lang: "en"
```

**2. Get Chinese claims for multiple patents by publication number**
```
patentNumber: "US20210012345A1,EP3456789B1"
lang: "cn"
```

**3. Get Japanese claims with family patent fallback**
```
patentNumber: "JP2021123456A"
lang: "jp"
replaceByRelated: 1
```

**4. Query by patent ID**
```
patentId: "84a1b2c3-d4e5-6f78-9abc-def012345678"
lang: "en"
```

## Display Rules

1. **Present claims clearly**: Show the translated claim text with proper formatting. If multiple patents are returned, separate each patent's claims with its publication number as a heading.
2. **Family substitution notice**: When `pnRelated` is present in the response, clearly inform the user that the claims were sourced from a related family patent and show the substitute publication number.
3. **Language notice**: State the language of the returned claims so the user knows which translation they are viewing.
4. **Large results**: When multiple patents are returned, summarize the count and show a few representative entries, reminding the user of the total.
5. **Error handling**: When a query fails, explain the reason based on the error response and suggest checking the patent ID or publication number.
## Important Limitations

- **At least one identifier required**: Either `patentId` or `patentNumber` must be provided; otherwise the query will fail.
- **Batch limit**: A maximum of 100 patents per request.
- **Language support**: Only Chinese (`cn`), English (`en`), and Japanese (`jp`) are supported.
- **Family substitution**: Substitute claims are only returned when `replaceByRelated` is set to `1` and the original claims are unavailable.

## User Expression & Scenario Quick Reference

**Applicable** -- Queries related to patent claim text and translation:

| User Says | Scenario |
|-----------|----------|
| "Show me the claims for patent XX" | Single patent claim lookup |
| "Translate claims to Chinese/Japanese" | Claim translation |
| "What does patent XX claim?" | Claim content retrieval |
| "Get claims for these patents: XX, YY" | Batch patent claim lookup |
| "Claims unavailable, try family patent" | Family patent substitution |
| "Patent rights scope of XX" | Claim text retrieval |

**Not applicable** -- Needs beyond patent claim translation:

- Patent search or discovery (finding patents by keyword)
- Patent citation or legal status analysis
- Patent abstract or description retrieval
- Patent portfolio analytics or statistics

## 积分消耗规则

按动态规则计费：消耗积分 = 81 × 返回data条数。每条为 1 条专利权利要求翻译结果

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

# 专利数据服务-权利要求翻译 API 参考

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| patentId | string | 否* | 专利ID，多个用英文逗号隔开，上限100条。当与 `patentNumber` 同时存在时优先使用专利ID。最大长度：60000字符 |
| patentNumber | string | 否* | 公开(公告)号，多个用英文逗号隔开，上限100条。最大长度：60000字符 |
| lang | string | 否 | 翻译语言，支持 `en`（英文，默认）、`cn`（中文）、`jp`（日语）。最大长度：1000字符 |
| replaceByRelated | integer | 否 | 权利要求无法获取时是否用同族专利替代：`1` 是，`0` 否（默认） |

> *`patentId` 和 `patentNumber` 两个参数必须至少提供一个。如果两个都存在，会优先使用 `patentId`。


## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errorCode 字段区分（errorCode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errorCode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析 `data` 等业务字段 |
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

