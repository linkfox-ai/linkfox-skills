# Reference archive: linkfox-amazon-store-customer-feedback

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
    "path": "customerFeedback/2024-06-01/items/{asin}/reviews/topics",
    "method": "GET",
    "queryString": "<按本 reference 的参数规则编码；无查询参数时省略>"
  }
}
```

`toolName` 必须精确匹配并区分大小写。WorkBuddy 自动注入 Authorization；`arguments` 中不得加入网关 `headers`、API Key、Amazon access/refresh token、JWT、手机号或其他凭证。MCP/`proxy_call` 缺失时停止，禁止 curl、`urllib`、`requests`、`httpx` 或本地脚本回退。同一任务内相同 `toolName + arguments` 不重复调用；失败、空结果或不理想时不自动重试。先检查 MCP/schema/`isError`，再读取 structured content 或仅解析一次 text JSON，随后检查下游 `errcode`/`code`、`errmsg`/`msg`、`httpStatus`，最后按响应字段读取结果。

## 来源响应字段表

来源：`skills/linkfox-amazon-store-customer-feedback/references/api.md`。仅转录来源响应章节明确给出的字段或响应 JSON；未说明属性不作推断。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `body` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |


---
name: linkfox-amazon-store-customer-feedback
description: 亚马逊商品与类目买家反馈洞察。用于按 ASIN 或 browse node 查询评论主题、主题提及量、星级影响、评价趋势、退货主题和退货趋势，帮助分析产品口碑及类目问题。用户提到亚马逊评论分析、评价主题、差评原因、评论趋势、退货原因、退货趋势、ASIN 口碑洞察、类目反馈、MENTIONS、STAR_RATING_IMPACT、Customer Feedback API 时触发。即使未明确提及 API，只要希望从聚合反馈中判断某个亚马逊商品或类目的常见好评、差评或退货问题，也应触发此技能。
---

# Amazon 店铺 Customer Feedback


> 说明：接口属于 **Customer Feedback（买家评论/退货洞察）**，不是 Orders 订单 API。订单见 **`linkfox-amazon-store-orders`**。

## 调用方式

仅按本文开头的 MCP 契约调用；预签名上传/下载例外仅使用本 skill 保留的对应本地 helper。


## 认证和积分问题

按 `references/onboarding.md` 分层处理 MCP 401、下游 401/402、403 和其他业务错误。


## 官方参考索引

| 能力 | 文档 |
|------|------|
| getItemReviewTopics | [getItemReviewTopics](https://developer-docs.amazon.com/sp-api/reference/getitemreviewtopics) |
| getItemBrowseNode | [getItemBrowseNode](https://developer-docs.amazon.com/sp-api/reference/getitembrowsenode) |
| getBrowseNodeReviewTopics | [getBrowseNodeReviewTopics](https://developer-docs.amazon.com/sp-api/reference/getbrowsenodereviewtopics) |
| getItemReviewTrends | [getItemReviewTrends](https://developer-docs.amazon.com/sp-api/reference/getitemreviewtrends) |
| getBrowseNodeReviewTrends | [getBrowseNodeReviewTrends](https://developer-docs.amazon.com/sp-api/reference/getbrowsenodereviewtrends) |
| getBrowseNodeReturnTopics | [getBrowseNodeReturnTopics](https://developer-docs.amazon.com/sp-api/reference/getbrowsenodereturntopics) |
| getBrowseNodeReturnTrends | [getBrowseNodeReturnTrends](https://developer-docs.amazon.com/sp-api/reference/getbrowsenodereturntrends) |

---

## Prerequisites

1. 依赖 **`linkfox-amazon-store-auth`**。
2. 通常需 **Brand Analytics** 或 **Selling Partner Insights** 等角色；站点以官方为准（常见 US/UK/DE 等）。
3. **ASIN** 一般为**子体 ASIN**；topics 类接口需 **`sortBy`**：`MENTIONS` 或 `STAR_RATING_IMPACT`（常各调一次对比）。

---

## Current Capabilities

| 脚本 | path 要点 |
|------|-----------|
| `get_item_review_topics` 操作 | `.../items/{asin}/reviews/topics` |
| `get_item_browse_node` 操作 | `.../items/{asin}/browseNode` |
| `get_item_review_trends` 操作 | `.../items/{asin}/reviews/trends` |
| `get_browse_node_review_topics` 操作 | `.../browseNodes/{browseNodeId}/reviews/topics` |
| `get_browse_node_review_trends` 操作 | `.../browseNodes/{browseNodeId}/reviews/trends` |
| `get_browse_node_return_topics` 操作 | `.../browseNodes/{browseNodeId}/returns/topics` |
| `get_browse_node_return_trends` 操作 | `.../browseNodes/{browseNodeId}/returns/trends` |

前缀均为 **`customerFeedback/2024-06-01/`**。共享模块：**`_spapi_customer_feedback_common` 操作**。

---

## Quick Parameters

- 公共：`sellerId`、`region`、`marketplaceId`（或 `marketplaceIds` 取首项）。
- ASIN 类：`asin`；topics 类另需 **`sortBy`**。
- Browse node 类：`browseNodeId`（可先 `get_item_browse_node` 取得）。

---

## Scripts



---

## Display Rules

1. 先看 **`developerProxy.errcode` / `httpStatus`**，再读各脚本解析字段（如 **`itemReviewTopics`**）。
2. 网关白名单需包含 **`customerFeedback/2024-06-01/`**。
3. 数据刷新频率以 Amazon 为准（通常按周）。

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

**Feedback：** `skillName`：`linkfox-amazon-store-customer-feedback`。

---
*更多跨境 skill：[LinkFox Skills](https://skill.linkfox.com/)*

## Archived reference: api.md

# linkfox-amazon-store-customer-feedback — API 参考

Customer Feedback **v2024-06-01**，经 LinkFox `storeTokens` + `developerProxy` 调用。

官方总览：[Customer Feedback API](https://developer-docs.amazon.com/sp-api/docs/customer-feedback-api-v2024-06-01-use-case-guide)

---

## 1. 脚本与 path

| 脚本 | GET path |
|------|----------|
| `get_item_review_topics` 操作 | `customerFeedback/2024-06-01/items/{asin}/reviews/topics` |
| `get_item_browse_node` 操作 | `customerFeedback/2024-06-01/items/{asin}/browseNode` |
| `get_item_review_trends` 操作 | `customerFeedback/2024-06-01/items/{asin}/reviews/trends` |
| `get_browse_node_review_topics` 操作 | `customerFeedback/2024-06-01/browseNodes/{browseNodeId}/reviews/topics` |
| `get_browse_node_review_trends` 操作 | `customerFeedback/2024-06-01/browseNodes/{browseNodeId}/reviews/trends` |
| `get_browse_node_return_topics` 操作 | `customerFeedback/2024-06-01/browseNodes/{browseNodeId}/returns/topics` |
| `get_browse_node_return_trends` 操作 | `customerFeedback/2024-06-01/browseNodes/{browseNodeId}/returns/trends` |

---

## 2. 公共入参

| 字段 | 必填 | 说明 |
|------|------|------|
| sellerId | 是 | |
| region | 是 | NA / EU / FE 等 |
| marketplaceId | 是 | 单站点；或 `marketplaceIds` 数组取第一个 |
| skipDepCheck | 否 | |

---

## 3. 按接口

### getItemReviewTopics / getBrowseNodeReviewTopics / getBrowseNodeReturnTopics

| 字段 | 必填 | 约束 |
|------|------|------|
| asin 或 browseNodeId | 是（按接口） | 与所选接口一致 |
| sortBy | 是 | `MENTIONS` \| `STAR_RATING_IMPACT` |

Query：`marketplaceId`、`sortBy`

解析字段：`itemReviewTopics` / `browseNodeReviewTopics` / `browseNodeReturnTopics`

### getItemBrowseNode

| 字段 | 必填 |
|------|------|
| asin | 是 |

Query：`marketplaceId`  
解析字段：`itemBrowseNode`

### getItemReviewTrends / getBrowseNodeReviewTrends / getBrowseNodeReturnTrends

Query：`marketplaceId`  
解析字段：`itemReviewTrends` / `browseNodeReviewTrends` / `browseNodeReturnTrends`

---

## 4. 推荐调用顺序（ASIN）

1. `get_item_review_topics`（`sortBy=MENTIONS` 与 `STAR_RATING_IMPACT` 各一次）
2. `get_item_review_trends`
3. `get_item_browse_node` → 取 `browseNodeId`
4. 对 browse node 调用 review/return 的 topics 与 trends

---

## 5. 限制

- 非订单接口；订单用 **`linkfox-amazon-store-orders`**。
- **401**：HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。
- **402**：HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。
- **403**：角色或站点不支持。
- **1005**：网关需放行 `customerFeedback/2024-06-01/`。

---

## 6. Feedback

`skillName`: **`linkfox-amazon-store-customer-feedback`**

## Archived reference: onboarding.md

认证和积分问题统一按本 skill 的 `references/onboarding.md` 处理。
