# linkfox-amazon-store-customer-feedback — API 参考

Customer Feedback **v2024-06-01**，经 LinkFox `storeTokens` + `developerProxy` 调用。

官方总览：[Customer Feedback API](https://developer-docs.amazon.com/sp-api/docs/customer-feedback-api-v2024-06-01-use-case-guide)

---

## 1. 脚本与 path

| 脚本 | GET path |
|------|----------|
| `get_item_review_topics.py` | `customerFeedback/2024-06-01/items/{asin}/reviews/topics` |
| `get_item_browse_node.py` | `customerFeedback/2024-06-01/items/{asin}/browseNode` |
| `get_item_review_trends.py` | `customerFeedback/2024-06-01/items/{asin}/reviews/trends` |
| `get_browse_node_review_topics.py` | `customerFeedback/2024-06-01/browseNodes/{browseNodeId}/reviews/topics` |
| `get_browse_node_review_trends.py` | `customerFeedback/2024-06-01/browseNodes/{browseNodeId}/reviews/trends` |
| `get_browse_node_return_topics.py` | `customerFeedback/2024-06-01/browseNodes/{browseNodeId}/returns/topics` |
| `get_browse_node_return_trends.py` | `customerFeedback/2024-06-01/browseNodes/{browseNodeId}/returns/trends` |

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

| 字段 | 必填 |
|------|------|
| asin 或 browseNodeId | 是（按接口） |
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
