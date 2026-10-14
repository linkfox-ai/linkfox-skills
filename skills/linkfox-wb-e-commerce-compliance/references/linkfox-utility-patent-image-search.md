# linkfox-utility-patent-image-search

## MCP 调用

| 项 | 值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `zhihuiya/patentImageSearch` |
| `arguments` | 直接使用本 reference 的请求参数对象，不包裹 `body`、`params` 或 `data` |

```json
{
  "toolName": "zhihuiya/patentImageSearch",
  "arguments": {
    "url": "https://example.com/product-image.jpg",
    "patentType": "U",
    "model": 3,
    "limit": 10
  }
}
```

`toolName` 精确匹配且区分大小写。WorkBuddy 自动注入 Authorization；禁止在 MCP 配置或 `arguments` 中加入 headers、API Key、token、JWT、手机号或其他凭证。MCP 或 `proxy_call` 缺失时停止，禁止 curl、`urllib`、`requests`、`httpx` 或脚本直连工具网关，也不 HTTP fallback。

先检查 MCP/schema/`isError`，再读取 structured content 或只解析一次 text JSON，然后检查下游 `errcode`、`errorCode`、`code`、`errmsg` 或 `msg`，最后读取业务字段。失败、空结果或结果不理想时不自动重试；同一任务内相同 `toolName + arguments` 不重复调用。

## 来源响应字段表

来源：`skills/linkfox-zhihuiya-utility-patent-image-search/references/api.md` 的响应字段章节。仅转录响应字段，未引入来源的请求、调用、认证、错误、成本或工作流内容。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `total` | integer | 本次返回的记录数 |
| `allRecordsCount` | integer | 数据库中匹配的总记录数 |
| `data` | array | 匹配的专利记录列表 |
| `columns` | array | 渲染的列定义 |
| `type` | string | 渲染的样式 |
| `costToken` | integer | 消耗token |
| `data[].patentId` | string | 相似专利ID |
| `data[].patentPn` | string | 相似专利号 |
| `data[].apno` | string | 申请号 |
| `data[].title` | string | 专利名称 |
| `data[].inventor` | string | 发明人 |
| `data[].originalAssignee` | string | 原始申请人 |
| `data[].currentAssignee` | string | 当前申请人 |
| `data[].authority` | string | 受理局（国家代码） |
| `data[].url` | string | 相似的专利附图URL |
| `data[].score` | number | 相似度分数（分数越高越相似；仅当 field 为 `SCORE` 时有效） |
| `data[].loc` | array | LOC分类（洛迦诺分类号） |
| `data[].locMatch` | integer | 是否命中高权重LOC：`1`（命中）、`0`（未命中）。仅当 model=1 且 field=SCORE 时有效 |
| `data[].apdt` | integer | 申请日（时间戳） |
| `data[].pbdt` | integer | 公开日（时间戳） |
| `data[].imgId` | string | 专利附图img_id（仅当 `returnImgId` 为 true 时返回） |

### 本地图片两阶段上传

本地图片不能直接作为 `url`。先调用 `proxy_call`：

```json
{"toolName":"oss/file/presignedPut","arguments":{"contentType":"image/png","fileExtension":"png"}}
```

该预签名响应契约来自 `skills/linkfox-zhihuiya-utility-patent-image-search/scripts/upload_image.py`：

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | `200` 表示成功 |
| `errmsg` | string | 失败时的错误说明 |
| `url` | string | 预签名 PUT URL；来源脚本以此上传并去掉查询参数得到公开 URL |

再把返回的预签名 URL、本地路径和内容类型交给 `scripts/upload_image.py`；该 helper 只执行对象存储 PUT，不读取 LinkFox 凭证，也不访问工具网关。上传成功后的公开 URL 再作为专利图片检索的 `url`。



以下归档该子能力的执行说明与 API 细节，按统一 WorkBuddy 路由调用。

## 执行说明

---
name: linkfox-utility-patent-image-search
description: 基于专利数据服务的专利图片相似度搜索，支持通过图片URL检索实用新型专利。当用户提到实用新型专利图片搜索、实用新型专利侵权检查、实用新型专利搜索、以图搜专利、实用新型专利相似度检测、专利图片匹配、专利形状/图案/色彩匹配、检查产品结构是否侵犯已有实用新型专利、patent image search, utility model patent search, patent reverse image search, utility model patent lookup, 专利数据服务, patent similarity时触发此技能。即使用户未明确提及"专利数据服务"或"专利图片"，只要其需求涉及通过图片查找相似实用新型专利或排查实用新型专利风险，也应触发此技能。本技能仅支持实用新型专利，外观设计专利检索请使用 linkfox-patent-image-search。
---

# patent-data Utility Patent Image Search

This skill guides you on how to perform image-based patent similarity searches using the patent-data patent database, helping users identify potentially similar **utility model patents**. This skill supports utility model patents only; for design patents use `linkfox-patent-image-search`.

## Core Concepts

**Patent Image Search** uses visual AI models to compare a given product or design image against a global patent image database. It returns a ranked list of similar patents, enabling users to evaluate infringement risks or conduct prior-art research.

**This skill supports utility model patents only:**

| Type | Code | Description |
|------|------|-------------|
| Utility Model Patent | `U` | Protects the functional shape/structure of a product |

**Search models** for utility model patents:

| Model ID | Strategy | Recommendation |
|----------|----------|----------------|
| 3 | Match Shape | Shape-only comparison |
| 4 | Match Shape/Pattern/Color | Recommended for utility model patents (default) |

> Design patents (model 1/2) are not supported by this skill. Use `linkfox-patent-image-search` instead.

**Scoring logic**: A higher `score` value means greater visual similarity. When presenting results, sort by score in descending order (highest similarity first) so users can prioritize the most relevant patents for review.

## Parameter Guide

### Required Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| url | The image URL to search against | `https://example.com/product.jpg` |
| patentType | Patent type, fixed to `U` (utility model) by this skill | `U` |
| model | Search model ID: `3` (shape only) or `4` (recommended) | `4` |

### Common Optional Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| country | Patent authority country codes, comma-separated (e.g., `CN,US,JP`) | All countries |
| legalStatus | Legal status codes, comma-separated | None |
| simpleLegalStatus | Simple legal status: `0` (expired), `1` (active), `2` (pending) | None |
| assignees | Applicant / patent holder name | None |
| applyStartTime | Application start date (`yyyyMMdd`) | None |
| applyEndTime | Application end date (`yyyyMMdd`) | None |
| publicStartTime | Publication start date (`yyyyMMdd`) | None |
| publicEndTime | Publication end date (`yyyyMMdd`) | None |
| limit | Number of results to return (1-100) | 10 |
| offset | Pagination offset (0-1000) | 0 |
| field | Sort field: `SCORE`, `APD`, `PBD`, `ISD` | `SCORE` |
| order | Sort order: `desc` or `asc` (for APD/PBD/ISD) | `desc` |
| lang | Title language preference: `original`, `cn`, `en` | `original` |
| preFilter | Enable country pre-filtering: `1` (on) / `0` (off) | `1` |
| stemming | Enable stemming: `1` (on) / `0` (off) | `0` |
| mainField | Search within title, abstract, claims, description, publication number, application number, applicant, inventor, IPC/UPC/LOC | None |
| includeMachineTranslation | Include machine-translated data in search | None |
| scoreExpansion | Enable score expansion | None |
| isHttps | Return HTTPS image URLs: `1` (yes) / `0` (no) | `0` |
| returnImgId | Return image IDs in results | `false` |

> Note: The `loc` (Locarno classification) parameter applies to design patents only and is not relevant for utility model searches.

### Commonly Used Country Codes

| Code | Country/Region |
|------|---------------|
| CN | China |
| US | United States |
| JP | Japan |
| KR | South Korea |
| EP | European Patent Office |
| WO | WIPO |
| DE | Germany |
| GB | United Kingdom |
| FR | France |
| AU | Australia |

## Usage Examples

**1. Basic utility model patent search (recommended starting point)**
Search for utility model patents similar to a product image, matching shape/pattern/color across all countries:
```json
{
  "url": "https://example.com/my-product.jpg",
  "patentType": "U",
  "model": 4,
  "limit": 20
}
```

**2. Utility model patent search limited to specific countries**
Search only in China and the United States:
```json
{
  "url": "https://example.com/my-product.jpg",
  "patentType": "U",
  "model": 4,
  "country": "CN,US",
  "limit": 20
}
```

**3. Shape-only utility model patent search**
Compare by shape only (ignore pattern/color):
```json
{
  "url": "https://example.com/my-product.jpg",
  "patentType": "U",
  "model": 3,
  "country": "CN",
  "limit": 20
}
```

**4. Search only active patents within a date range**
Find active utility model patents filed after 2020:
```json
{
  "url": "https://example.com/my-product.jpg",
  "patentType": "U",
  "model": 4,
  "simpleLegalStatus": "1",
  "applyStartTime": "20200101",
  "limit": 30
}
```

**5. Search by specific assignee**
Find patents held by a particular company:
```json
{
  "url": "https://example.com/my-product.jpg",
  "patentType": "U",
  "model": 4,
  "assignees": "Apple Inc.",
  "limit": 20
}
```

**6. Get results with Chinese-translated titles**
```json
{
  "url": "https://example.com/my-product.jpg",
  "patentType": "U",
  "model": 4,
  "lang": "cn",
  "limit": 20
}
```

## Display Rules

1. **Sort by score**: Always sort results by `score` in descending order (highest similarity first) to help users quickly identify the most relevant infringement risks.

2. **Show complete details**: When summarizing results or generating reports, include ALL of the following for each patent -- do NOT omit or abbreviate:
   - Application number (`apno`)
   - Patent title in Chinese (use `lang: cn` or provide translation)
   - Inventor (`inventor`)
   - Patent drawing (the matched `url` image)
   - **Every** patent image in the image list
   - Patent abstract
   - Patent description
   - IPC/UPC classification information
   - Radar result (`radarResult`) if available
   - Patent specification

3. **Legal disclaimer**: Always append a friendly reminder at the end of results:
   > This search result was generated by LinkfoxAgent. It is recommended to consult a professional patent attorney for legal advice.

4. **Score explanation**: Remind users that the score represents visual similarity -- a higher score indicates a closer match, but does not constitute a legal determination of infringement.

5. **Pagination guidance**: When the total count exceeds the returned results, inform users about the total number of matching patents and guide them to use `offset` and `limit` for additional pages.

6. **Error handling**: When a query fails, explain the reason and suggest adjustments (e.g., verify the image URL is publicly accessible, check country codes, adjust date formats).
## User Expression & Scenario Quick Reference

**Applicable** -- Image-based utility model patent similarity searches:

| User Says | Scenario |
|-----------|----------|
| "Check if my product structure infringes any utility model patents" | Utility model patent infringement check |
| "Search for similar utility model patents" | Utility model patent similarity search |
| "Find utility model patents that look like this image" | Visual utility model patent lookup |
| "Are there any utility model patents similar to my product structure" | Utility model risk assessment |
| "Utility model patent search by image" | Utility model search |
| "Check utility model patent risks for this product in China and US" | Multi-country utility model patent check |
| "Find active utility model patents in this category" | Filtered utility model patent search |
| "Who holds utility model patents similar to this design" | Competitor patent discovery |

**Not applicable** -- Needs beyond utility model patent image search:
- Text-based patent search (keyword/abstract/claim search)
- Design patent image search (use `linkfox-patent-image-search` instead)
- Patent legal status monitoring or annuity management
- Patent valuation or licensing negotiation
- Freedom-to-operate (FTO) legal opinions
- Patent family or citation analysis

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

# 专利数据服务专利图像检索 API 参考

## 请求参数

POST Body（JSON）：

### 必填参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| url | string | 是 | 图像的URL（最大1000字符） |
| patentType | string | 是 | 专利类型：`D`（外观专利）或 `U`（实用新型专利）。默认：`D` |
| model | integer | 是 | 图像检索模型。外观专利：`1`（智能联想，推荐）、`2`（搜索此图）；实用新型专利：`3`（匹配形状）、`4`（匹配形状/图案/色彩，推荐） |

### 可选参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| country | string | 否 | 专利受理局（国家/组织/地区代码），多个用英文逗号隔开。例如：`CN,US,JP`。不传时代表查询全部专利受理局的数据 |
| loc | string | 否 | LOC分类（洛迦诺分类号），多个分类号可以用逻辑符 AND/OR/NOT 连接 |
| legalStatus | string | 否 | 专利的法律状态，多个用英文逗号隔开。可选值：`1`（公开）、`2`（实质审查）、`3`（授权）、`8`（避免重复授权）、`11`（撤回）、`12`（撤回-未指定类型）、`17`（撤回-视为撤回）、`18`（撤回-主动撤回）、`13`（驳回）、`14`（全部撤销）、`15`（期限届满）、`16`（未缴年费）、`21`（权利恢复）、`22`（权利终止）、`23`（部分无效）、`24`（申请终止）、`30`（放弃）、`19`（放弃-视为放弃）、`20`（放弃-主动放弃）、`25`（放弃-未指定类型）、`222`（PCT未进入指定国-指定期内）、`223`（PCT进入指定国-指定期内）、`224`（PCT进入指定国-指定期满）、`225`（PCT未进入指定国-指定期满） |
| simpleLegalStatus | string | 否 | 专利的简单法律状态，多个用英文逗号隔开。可选值：`0`（失效）、`1`（有效）、`2`（审中）、`220`（PCT指定期满）、`221`（PCT指定期内）、`999`（未确认） |
| assignees | string | 否 | 申请（专利权）人（最大1000字符） |
| applyStartTime | string | 否 | 专利申请起始时间，格式：`yyyyMMdd` |
| applyEndTime | string | 否 | 专利申请截止时间，格式：`yyyyMMdd` |
| publicStartTime | string | 否 | 专利公开起始时间，格式：`yyyyMMdd` |
| publicEndTime | string | 否 | 专利公开截止时间，格式：`yyyyMMdd` |
| limit | integer | 否 | 返回专利条数，1-100。默认：`10` |
| offset | integer | 否 | 偏移量，0-1000。默认：`0` |
| field | string | 否 | 返回结果排序字段：`SCORE`（按照最相关排序）、`APD`（按照申请日排序）、`PBD`（按照公开日排序）、`ISD`（按照授权日排序）。默认：`SCORE` |
| order | string | 否 | 当 field 选择 APD/PBD/ISD 时有效：`desc`（降序）或 `asc`（升序）。默认：`desc` |
| lang | string | 否 | 设置标题的语言优先选择：`original`（专利原文标题）、`cn`（专利中文翻译标题）、`en`（专利英文翻译标题）。默认：`original` |
| preFilter | integer | 否 | 是否开启前置国家/LOC过滤：`1`（开启）、`0`（关闭）。默认：`1` |
| stemming | integer | 否 | 是否开启截词功能：`1`（开启）、`0`（关闭）。默认：`0` |
| mainField | string | 否 | 专利主要字段，包括标题、摘要、权利要求、说明书、公开号、申请号、申请人、发明人和IPC/UPC/LOC分类号（最大1000字符） |
| includeMachineTranslation | boolean | 否 | 搜索包含机器翻译数据 |
| scoreExpansion | boolean | 否 | 分数拓展 |
| isHttps | integer | 否 | 选择是否返回https域名图片：`1`（返回https）、`0`（返回http）。默认：`0` |
| returnImgId | boolean | 否 | 是否返回img_id。默认：`false` |

**注意**：
- `model` 参数须与 `patentType` 匹配：模型1-2用于外观专利（`D`），模型3-4用于实用新型专利（`U`）

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

---

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
