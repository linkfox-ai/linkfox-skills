# linkfox-fulltext-image

## MCP 调用

| 项 | 值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `zhihuiya/fulltextImage` |
| `arguments` | 直接使用本 reference 的请求参数对象，不包裹 `body`、`params` 或 `data` |

```json
{
  "toolName": "zhihuiya/fulltextImage",
  "arguments": {
    "patentNumber": "US20230012345A1"
  }
}
```

`toolName` 精确匹配且区分大小写。WorkBuddy 自动注入 Authorization；禁止在 MCP 配置或 `arguments` 中加入 headers、API Key、token、JWT、手机号或其他凭证。MCP 或 `proxy_call` 缺失时停止，禁止 curl、`urllib`、`requests`、`httpx` 或脚本直连工具网关，也不 HTTP fallback。

先检查 MCP/schema/`isError`，再读取 structured content 或只解析一次 text JSON，然后检查下游 `errcode`、`errorCode`、`code`、`errmsg` 或 `msg`，最后读取业务字段。失败、空结果或结果不理想时不自动重试；同一任务内相同 `toolName + arguments` 不重复调用。

## 来源响应字段表

来源：`skills/linkfox-zhihuiya-fulltext-image/references/api.md` 的响应字段章节。仅转录响应字段，未引入来源的请求、调用、认证、错误、成本或工作流内容。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `total` | integer | 记录数 |
| `data` | array | 专利列表 |
| `data[].patentId` | string | 专利Id |
| `data[].pn` | string | 公开(公告)号 |
| `data[].fulltextImagePath` | string | 图片路径 |
| `data[].imageType` | string | 图片类型 |
| `columns` | array | 渲染的列 |
| `costToken` | integer | 消耗token |
| `type` | string | 渲染的样式 |



以下归档该子能力的执行说明与 API 细节，按统一 WorkBuddy 路由调用。

## 执行说明

---
name: linkfox-fulltext-image
description: 通过专利ID或公开号获取专利文件中的全文附图（图纸、示意图、图表）。当用户询问专利图片、专利图纸、专利示意图、专利插图、全文附图、专利图表、专利技术图或想查看、下载专利文件中的嵌入图片、patent fulltext drawings, patent diagrams, technical drawings, patent images, 专利数据服务时触发此技能。即使用户未明确提及"全文附图"，只要其需求涉及获取特定专利中的视觉内容（图纸、示意图、图表），也应触发此技能。
---

# patent-data Patent Fulltext Image

This skill guides you on how to retrieve fulltext images (drawings, figures, diagrams) from patent documents using the patent-data patent data service, helping users access and analyze visual content within patents.

## Core Concepts

Patent fulltext images are the figures, drawings, and diagrams embedded in patent documents. They are essential for understanding the technical details of an invention. This tool queries the patent-data patent database and returns image metadata including download paths and image types for a given patent.

**Lookup methods**: You can look up images by either **patent ID** (an internal identifier) or **publication number** (the publicly visible patent number such as `US20230012345A1` or `CN115000000A`). At least one of these must be provided.

## Parameter Guide

| Parameter | API Name | Required | Description | Example |
|-----------|----------|----------|-------------|---------|
| Patent ID | patentId | No* | Internal patent identifier | 8a7b6c5d-... |
| Publication Number | patentNumber | No* | Public patent publication/grant number | US20230012345A1 |
| Limit | limit | No | Maximum number of images to return (max 100, default 100) | 50 |
| Offset | offset | No | Pagination offset for image results | 0 |

> *At least one of `patentId` or `patentNumber` must be provided.

## Usage Examples

**1. Get all images for a patent by publication number**
```
Retrieve fulltext images for patent US20230012345A1.
```
Parameters: `{"patentNumber": "US20230012345A1"}`

**2. Get images for a patent by patent ID**
```
Fetch the drawings for patent ID abc123def456.
```
Parameters: `{"patentId": "abc123def456"}`

**3. Paginated retrieval of images**
```
Get the first 20 images for patent CN115000000A.
```
Parameters: `{"patentNumber": "CN115000000A", "limit": "20", "offset": "0"}`

**4. Get the next page of images**
```
Get images 21-40 for patent CN115000000A.
```
Parameters: `{"patentNumber": "CN115000000A", "limit": "20", "offset": "20"}`

## Display Rules

1. **Present data clearly**: Show image results in a structured table with image type, download path, and patent number
2. **Image links**: Always present `fulltextImagePath` values as clickable links so users can view or download images directly
3. **Pagination notice**: When `total` exceeds the number of returned results, inform the user that more images are available and offer to fetch the next page
4. **Error handling**: When a query fails, explain the reason and suggest verifying the patent ID or publication number
5. **No fabrication**: Never invent patent IDs, publication numbers, or image URLs -- only display data returned by the API
6. **Total count**: Always mention the total number of images available for the patent
## Important Limitations

- **Image limit**: Each request returns a maximum of 100 images
- **Identifier required**: At least one of `patentId` or `patentNumber` must be supplied
- **All parameters are strings**: Even numeric values like `limit` and `offset` must be passed as strings

## User Expression & Scenario Quick Reference

**Applicable** -- Requests involving patent visual content:

| User Says | Scenario |
|-----------|----------|
| "Show me the drawings for patent XX" | Fulltext image retrieval |
| "Get the figures from this patent" | Fulltext image retrieval |
| "Download patent images for XX" | Fulltext image retrieval |
| "What diagrams does patent XX contain" | Fulltext image listing |
| "How many figures are in patent XX" | Image count query |
| "Show me the technical drawings" | Fulltext image retrieval |

**Not applicable** -- Needs beyond patent fulltext images:
- Patent text/abstract/claims search
- Patent family or citation analysis
- Patent legal status queries
- Patent assignee or inventor search
- General image search unrelated to patents

## 积分消耗规则

消耗 81 积分。

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。

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

# 专利数据服务-全文附图 API 参考

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| patentId | string | 否* | 专利ID |
| patentNumber | string | 否* | 公开(公告)号 |
| limit | string | 否 | 返回图片总量，最大100，默认 `"100"` |
| offset | string | 否 | 偏移量 |

> *`patentId` 和 `patentNumber` 至少需提供其中一个。

- 所有参数值均为字符串类型，最大长度 1000 字符。

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

