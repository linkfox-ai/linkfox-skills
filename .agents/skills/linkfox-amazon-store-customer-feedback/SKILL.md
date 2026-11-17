---
name: linkfox-amazon-store-customer-feedback
description: 亚马逊商品与类目买家反馈洞察。用于按 ASIN 或 browse node 查询评论主题、主题提及量、星级影响、评价趋势、退货主题和退货趋势，帮助分析产品口碑及类目问题。用户提到亚马逊评论分析、评价主题、差评原因、评论趋势、退货原因、退货趋势、ASIN 口碑洞察、类目反馈、MENTIONS、STAR_RATING_IMPACT、Customer Feedback API 时触发。即使未明确提及 API，只要希望从聚合反馈中判断某个亚马逊商品或类目的常见好评、差评或退货问题，也应触发此技能。
---

# Amazon 店铺 Customer Feedback

本 skill 与 **`linkfox-amazon-store-auth`** 等同属 **Amazon Store** 系列：依赖 **`linkfox-amazon-store-auth`** 选店（`sellerId`+`region`）；直接 **`POST /spApi/developerProxy`** 传入 `sellerId`+`region`，由服务端解析 token（勿传 `amzAccessToken`，除非兼容旧调用）。转发 **GET**。

> 说明：接口属于 **Customer Feedback（买家评论/退货洞察）**，不是 Orders 订单 API。订单见 **`linkfox-amazon-store-orders`**。

## 调用方式

- **API 端点**：`POST /spApi/developerProxy`（不同操作通过请求体区分；完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/<脚本名>.py '<JSON 参数>' [--inline]`（可用脚本见上文脚本一览）
- **成本约束**：本工具会消耗算力；失败/空结果不得自动换关键词、翻页或连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-amazon-store-customer-feedback-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 解决认证和算力问题
发生以下异常情况时，采用 references/onboarding.md 引导解决问题：

### 异常情况
- **未配置API Key**：环境变量未配置 `LINKFOX_AGENT_API_KEY`，也未配置 `LINKFOXAGENT_API_KEY`。
- **响应401或402状态码**
- **响应提示算力或余额不足**：消息含"算力余额不足/计费不足/余额不足/quota exceeded/insufficient balance/套餐到期/需充值/请充值"，或类似含义的内容。

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
| `get_item_review_topics.py` | `.../items/{asin}/reviews/topics` |
| `get_item_browse_node.py` | `.../items/{asin}/browseNode` |
| `get_item_review_trends.py` | `.../items/{asin}/reviews/trends` |
| `get_browse_node_review_topics.py` | `.../browseNodes/{browseNodeId}/reviews/topics` |
| `get_browse_node_review_trends.py` | `.../browseNodes/{browseNodeId}/reviews/trends` |
| `get_browse_node_return_topics.py` | `.../browseNodes/{browseNodeId}/returns/topics` |
| `get_browse_node_return_trends.py` | `.../browseNodes/{browseNodeId}/returns/trends` |

前缀均为 **`customerFeedback/2024-06-01/`**。共享模块：**`_spapi_customer_feedback_common.py`**。

---

## Quick Parameters

- 公共：`sellerId`、`region`、`marketplaceId`（或 `marketplaceIds` 取首项）。
- ASIN 类：`asin`；topics 类另需 **`sortBy`**。
- Browse node 类：`browseNodeId`（可先 `get_item_browse_node` 取得）。

---

## Scripts

```bash
export LINKFOXAGENT_API_KEY="<your-key>"

python scripts/get_item_review_topics.py '{"sellerId":"A1...","region":"NA","asin":"B0...","marketplaceId":"ATVPDKIKX0DER","sortBy":"MENTIONS"}'

python scripts/get_item_browse_node.py '{"sellerId":"A1...","region":"NA","asin":"B0...","marketplaceId":"ATVPDKIKX0DER"}'

python scripts/get_browse_node_review_topics.py '{"sellerId":"A1...","region":"NA","browseNodeId":"123456","marketplaceId":"ATVPDKIKX0DER","sortBy":"STAR_RATING_IMPACT"}'
```

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
- 向用户先说明店铺保护，再给原因、处理和等待时间。可回复：“为保护您的亚马逊店铺安全，检测到 Amazon SP-API 连续返回{原因}，当前已进入短暂保护。请先{处理动作}，预计{等待时间}后再试；这不代表封号，也不是套餐或算力限制。”不要只说“LinkFox 限流”或“服务器繁忙”。

## 算力消耗规则

不消耗算力。

**Feedback：** `skillName`：`linkfox-amazon-store-customer-feedback`。

---
*更多跨境 skill：[LinkFox Skills](https://skill.linkfox.com/)*

