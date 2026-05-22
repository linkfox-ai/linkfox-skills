---
name: linkfox-amazon-store-customer-feedback
description: 亚马逊店铺买家反馈洞察（与 linkfox-amazon-store-auth 等同系列），经 /spApi/developerProxy 调用 SP-API Customer Feedback v2024-06-01：getItemReviewTopics、getItemBrowseNode、getBrowseNodeReviewTopics、getItemReviewTrends、getBrowseNodeReviewTrends、getBrowseNodeReturnTopics、getBrowseNodeReturnTrends。当用户提到评论主题、评价趋势、退货主题、browse node 反馈、Customer Feedback API、MENTIONS、STAR_RATING_IMPACT、ASIN 评论洞察、类目节点评价 时触发。
---

# Amazon 店铺 Customer Feedback

本 skill 与 **`linkfox-amazon-store-auth`** 等同属 **Amazon Store** 系列：先 **`POST /spApi/storeTokens`**，再 **`POST /spApi/developerProxy`** 转发 **GET**。

> 说明：接口属于 **Customer Feedback（买家评论/退货洞察）**，不是 Orders 订单 API。订单见 **`linkfox-amazon-store-orders`**。

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

**Feedback：** `skillName`：`linkfox-amazon-store-customer-feedback`。

---
*更多跨境 skill：[LinkFox Skills](https://skill.linkfox.com/)*
