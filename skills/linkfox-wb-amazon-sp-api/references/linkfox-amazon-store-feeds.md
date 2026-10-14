# Reference archive: linkfox-amazon-store-feeds

本文件归档该子能力的执行说明、API 契约、参数约束、错误处理和工作流；按需阅读相关章节。

## Capability instructions


## MCP 调用

| 项 | 值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `spApi/developerProxy` |
| `arguments` | 直接使用本 reference 对应的网关请求对象 |

```json
{
  "toolName": "spApi/developerProxy",
  "arguments": {
    "sellerId": "A1234567890",
    "region": "NA",
    "path": "feeds/2021-06-30/documents",
    "method": "POST",
    "body": "<按本 reference 构造的 JSON 字符串；无请求体时省略>"
  }
}
```

`toolName` 必须精确匹配并区分大小写。WorkBuddy 自动注入 Authorization；`arguments` 中不得加入网关 `headers`、API Key、Amazon access/refresh token、JWT、手机号或其他凭证。MCP/`proxy_call` 缺失时停止，禁止 curl、`urllib`、`requests`、`httpx` 或本地脚本回退。同一任务内相同 `toolName + arguments` 不重复调用；失败、空结果或不理想时不自动重试。先检查 MCP/schema/`isError`，再读取 structured content 或仅解析一次 text JSON，随后检查下游 `errcode`/`code`、`errmsg`/`msg`、`httpStatus`，最后按响应字段读取结果。

## 来源响应字段表

来源：`skills/linkfox-amazon-store-feeds/references/api.md`。仅转录来源响应章节明确给出的字段或响应 JSON；未说明属性不作推断。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `errcode` | number | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `httpStatus` | number | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `body` | string | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |


---
name: linkfox-amazon-store-feeds
description: 亚马逊店铺 Feed 批量数据提交与处理状态管理。用于创建 Feed 文档、向预签名地址上传 Feed 内容、提交库存或 Listing 等批量文件、查询或列出 Feed、获取结果文档以及取消 Feed。用户提到亚马逊 Feed、批量更新库存或商品、提交 Listing Feed、POST_FLAT_FILE、feedType、feedDocumentId、feedId、Feed 处理状态、Feed 结果、取消 Feed、Feeds API 时触发。即使未明确说“Feed”，只要希望通过亚马逊 SP-API 批量提交结构化商品或库存数据，也应触发此技能；单个 Listing 的增删改查使用 linkfox-amazon-store-listings。
---

# Amazon 店铺 Feeds


## 调用方式

仅按本文开头的 MCP 契约调用；预签名上传/下载例外仅使用本 skill 保留的对应本地 helper。


## 认证和积分问题

按 `references/onboarding.md` 分层处理 MCP 401、下游 401/402、403 和其他业务错误。


## 官方参考索引

| 能力 | 文档 |
|------|------|
| createFeedDocument | [createFeedDocument](https://developer-docs.amazon.com/sp-api/reference/createfeeddocument) |
| getFeedDocument | [getFeedDocument](https://developer-docs.amazon.com/sp-api/reference/getfeeddocument) |
| createFeed | [createFeed](https://developer-docs.amazon.com/sp-api/reference/createfeed) |
| getFeed | [getFeed](https://developer-docs.amazon.com/sp-api/reference/getfeed) |
| getFeeds | [getFeeds](https://developer-docs.amazon.com/sp-api/reference/getfeeds) |
| cancelFeed | [cancelFeed](https://developer-docs.amazon.com/sp-api/reference/cancelfeed) |

---

## Prerequisites

2. 应用需具备 **Feeds** 相关角色；`feedType` 须与上传文件格式匹配（见 Amazon Feed Type Values 文档）。

---

## 典型工作流

1. **`create_feed_document` 操作** → 得到 `feedDocumentId` 与 **`url`**（上传地址）。
2. **`scripts/upload_feed_document.py`** → 对 `url` **PUT** 上传 feed 文件（**不经** developerProxy）。
3. **`create_feed` 操作** → 传入 `inputFeedDocumentId`、`feedType`、`marketplaceIds`。
4. **`get_feed` 操作** / **`get_feeds` 操作** → 轮询 `processingStatus`（如 IN_QUEUE、IN_PROGRESS、DONE、FATAL）。
5. 处理完成后用 **`get_feed_document` 操作** 下载 **resultFeedDocumentId** 对应文档（再按返回 URL 自行下载结果文件）。

---

## Current Capabilities

| 能力 | path | method | 脚本 |
|------|------|--------|------|
| createFeedDocument | `feeds/2021-06-30/documents` | POST | `create_feed_document` 操作 |
| getFeedDocument | `feeds/2021-06-30/documents/{feedDocumentId}` | GET | `get_feed_document` 操作 |
| createFeed | `feeds/2021-06-30/feeds` | POST | `create_feed` 操作 |
| getFeed | `feeds/2021-06-30/feeds/{feedId}` | GET | `get_feed` 操作 |
| getFeeds | `feeds/2021-06-30/feeds` | GET | `get_feeds` 操作 |
| cancelFeed | `feeds/2021-06-30/feeds/{feedId}` | DELETE | `cancel_feed` 操作 |
| 上传文档内容 | createFeedDocument 返回的 URL | PUT | `scripts/upload_feed_document.py` |

共享模块：**`_spapi_feeds_common` 操作**。

---

## Scripts 示例



---

## Display Rules

1. 先看 **`developerProxy.errcode` / `httpStatus`**；createFeedDocument 常为 **201**，createFeed 常为 **202**。
2. **getFeeds** 分页：仅用上一页 **`nextToken`** 作为下一请求的 **`paginationToken` 参数名在 Amazon 侧为 `nextToken`**（脚本字段名 `nextToken`）。
3. **upload** 失败与 SP-API 网关无关，检查 `uploadUrl` 是否过期、**Content-Type** 是否与 createFeedDocument 一致。
4. 网关 path 白名单需包含 **`feeds/2021-06-30/`** 前缀。

---

## Important Limitations

- 本 skill **不**代替 Amazon 侧 feed 文件 schema 校验；`feedType`、TSV/XML 格式以官方为准。
- 下载 **getFeedDocument** 返回的 **url** 内容需另行 HTTP GET（与 upload 类似，不经 developerProxy）。
- 详见 **`references/api.md`**。

## Amazon SP-API 接口保护与重试指引

同一店铺连续收到 Amazon SP-API 的 400、403、404 或 429 时，网关会返回 450、453、454 或 459 并短暂冷却。这些自定义状态码不是 Amazon 原生状态，也不表示封号；目的是避免持续异常或高频调用扩大店铺风险。

| 状态与 message | 范围 | 触发与冷却 | 处理 |
|---|---|---|---|
| `450`：`400，请求异常，请优化您的参数` | 店铺+接口 | 60 秒内超过 3 次：5 分钟；10 分钟内超过 4 次：20 分钟 | 停止原参数重试，检查必填字段、marketplace、ID、日期和请求体 |
| `453`：`403，店铺未授权，请先授权` | 店铺全部接口 | 60 秒内超过 2 次：5 分钟；10 分钟内超过 4 次：30 分钟 | 停止该店铺调用，检查授权、权限、店铺归属和区域 |
| `454`：`404，资源不存在，请优化您的参数` | 店铺+接口 | 60 秒内超过 3 次：5 分钟；10 分钟内超过 4 次：30 分钟 | 确认资源 ID、所属店铺/站点、资源状态和接口路径 |
| `459`：`429限流中，请降低频率` | 店铺+接口 | 首次：15 秒；2 分钟内超过 2 次：30 秒；3 分钟内超过 4 次：2 分钟 | 降低并发、分页和轮询频率并逐级退避 |

- 立即停止自动或并发重试，不得通过换脚本或重复创建任务绕过保护；优先遵循 `retryAfter`、`blockedUntil`，没有时按表中时长说明。
- 450/453/454 必须先修正参数、授权或资源标识，冷却后最多谨慎重试一次；再次触发则停止调用。453 期间停止该店铺全部 SP-API。
- 保留已有 `reportId`、`feedId` 等任务 ID；写操作结果不确定时先查询状态，不直接重放。
- 向用户先说明店铺保护，再给原因、处理和等待时间。可回复：“为保护您的亚马逊店铺安全，检测到 Amazon SP-API 连续返回{原因}，当前已进入短暂保护。请先{处理动作}，预计{等待时间}后再试；这不代表封号，也不是套餐或积分限制。”不要只说“LinkFox 限流”或“服务器繁忙”。

## 积分消耗规则

不消耗积分。

**Feedback：** `skillName`：`linkfox-amazon-store-feeds`。

---
*更多跨境 skill：[LinkFox Skills](https://skill.linkfox.com/)*

## Archived reference: api.md

# linkfox-amazon-store-feeds — API 参考（Feeds v2021-06-30）

## 1. 调用链

| 步骤 | 端点 | 说明 |
|------|------|------|
| 2 | ``proxy_call` 的 `spApi/developerProxy`` | 转发 SP-API（除文档上传/下载 URL 外） |


### developerProxy Body

| 字段 | 说明 |
|------|------|
| region | NA / EU / FE |
| path | 如 `feeds/2021-06-30/feeds`，无前导 `/` |
| method | GET / POST / DELETE |
| queryString | 无 `?` 前缀 |
| body | POST 时为 JSON 字符串 |
| contentType | 一般 `application/json` |

网关响应：`errcode`、`httpStatus`、`body`（字符串）。成功 HTTP 可能为 **200 / 201 / 202 / 204**。

---

## 2. 脚本入参摘要

### 公共

| 字段 | 必填 | 说明 |
|------|------|------|
| sellerId | 是 | 卖家 ID |
| region | 是 | 区域 |
| skipDepCheck | 否 | 跳过本地 auth 探测 |

### create_feed_document operation

| 字段 | 必填 | 说明 |
|------|------|------|
| contentType | 是 | 与将要上传的文件 MIME 一致，如 `text/tab-separated-values; charset=UTF-8` |

解析字段：**`feedDocument`**（含 `feedDocumentId`、`url` 等，以 Amazon 为准）。

### upload_feed_document operation（不经 developerProxy）

| 字段 | 必填 | 说明 |
|------|------|------|
| uploadUrl | 是 | createFeedDocument 返回的 `url` |
| contentType | 是 | 与 createFeedDocument 相同 |
| filePath | 三选一 | 本地文件路径 |
| content | 三选一 | UTF-8 字符串内容 |
| contentBase64 | 三选一 | Base64 编码内容 |

### create_feed operation

| 字段 | 必填 | 说明 |
|------|------|------|
| feedType | 是 | 如 `POST_FLAT_FILE_INVLOADER_DATA` |
| marketplaceIds | 是 | 1～25 个站点 ID |
| inputFeedDocumentId | 是 | 已上传内容的文档 ID |
| feedOptions | 否 | 因 feedType 而异的对象 |

### get_feed operation / cancel_feed operation

| 字段 | 必填 |
|------|------|
| feedId | 是 |

### get_feeds operation

| 字段 | 必填 | 说明 |
|------|------|------|
| feedTypes | 条件 | 与 nextToken 二选一；最多 10 个 |
| nextToken | 条件 | 分页时**单独**传此参数 |
| marketplaceIds | 否 | 最多 10 个 |
| processingStatuses | 否 | CANCELLED, DONE, FATAL, IN_PROGRESS, IN_QUEUE |
| createdSince / createdUntil | 否 | ISO 8601 |
| pageSize | 否 | 1～100，默认 10 |

### get_feed_document operation

| 字段 | 必填 | 说明 |
|------|------|------|
| feedDocumentId | 是 | |
| enableContentEncodingUrlHeader | 否 | boolean；GZIP 时便于客户端自动解压 |

---

## 3. Feed 标准流程

```text
createFeedDocument → PUT uploadUrl (upload_feed_document operation)
    → createFeed → poll getFeed until DONE/FATAL
    → getFeedDocument(resultFeedDocumentId) → GET 结果 url
```

---

## 4. 常见 feedType（示例）

以 [Feed Type Values](https://developer-docs.amazon.com/sp-api/docs/feed-type-values) 为准，例如：

- `POST_PRODUCT_DATA` / `POST_INVENTORY_AVAILABILITY_DATA`
- `POST_FLAT_FILE_INVLOADER_DATA`
- `POST_ORDER_FULFILLMENT_DATA`

---

## 5. 错误与限制

- **401**：HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。
- **402**：HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。
- **403**：权限或 feedType 未授权。
- **1005**（网关）：path 未在白名单，需放行 `feeds/2021-06-30/`。
- **429**：降频；getFeeds 等有独立 usage plan。
- 上传 URL 有时效，过期需重新 createFeedDocument。

---

## 6. Feedback

上报问题时注明 **`skillName`: `linkfox-amazon-store-feeds`**，并附 `developerProxy` JSON（脱敏）。

## Archived reference: onboarding.md

认证和积分问题统一按本 skill 的 `references/onboarding.md` 处理。
