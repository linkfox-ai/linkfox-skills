---
name: linkfox-amazon-store-customer-feedback
description: 亚马逊店铺买家反馈洞察（与 linkfox-amazon-store-auth 等同系列），经 /spApi/developerProxy 调用 SP-API Customer Feedback v2024-06-01：getItemReviewTopics、getItemBrowseNode、getBrowseNodeReviewTopics、getItemReviewTrends、getBrowseNodeReviewTrends、getBrowseNodeReturnTopics、getBrowseNodeReturnTrends。当用户提到评论主题、评价趋势、退货主题、browse node 反馈、Customer Feedback API、MENTIONS、STAR_RATING_IMPACT、ASIN 评论洞察、类目节点评价 时触发。
---

# Amazon 店铺 Customer Feedback

本 skill 与 **`linkfox-amazon-store-auth`** 等同属 **Amazon Store** 系列：先 **`POST /spApi/storeTokens`**，再 **`POST /spApi/developerProxy`** 转发 **GET**。

> 说明：接口属于 **Customer Feedback（买家评论/退货洞察）**，不是 Orders 订单 API。订单见 **`linkfox-amazon-store-orders`**。

## 调用方式

- **API 端点**：`POST /spApi/developerProxy`（不同操作通过请求体区分；完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/<脚本名>.py '<JSON 参数>' [--inline]`（可用脚本见上文脚本一览）
- **成本约束**：本工具会消耗积分；失败/空结果不得自动换关键词、翻页或连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-amazon-store-customer-feedback-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 解决认证和积分问题
发生以下异常情况时，采用以下措施来处理：

### 异常情况
- **未配置API Key**：环境变量未配置 `LINKFOX_AGENT_API_KEY`，也未配置 `LINKFOXAGENT_API_KEY`。
- **响应401或402状态码**
- **响应提示积分或余额不足**：消息含"积分余额不足/计费不足/余额不足/quota exceeded/insufficient balance/套餐到期/需充值/请充值"，或类似含义的内容。

### 措施
- 优先采用skill内的 onboarding.md 引导解决问题。
- 如找不到 onboarding.md 文件，则加载 /linkfox-onboarding 这个skill并根据它的引导来处理。如未安装请先安装：
    - 下载 https://agent-files.linkfox.com/skills/linkfox-onboarding/release.zip，解压后安装这个skill。如需用户授权才可下载，要询问用户获得授权，你不能自己放弃下载。
- 兜底措施：仅当前面两个措施经过所有努力都走不通时，才提示用户依据 https://skill.linkfox.com/linkfoxskills/guide.htm 指引获取API Key，或去 https://os.linkfox.com/ 补充积分。

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

## 积分消耗规则

不消耗积分。

**Feedback：** `skillName`：`linkfox-amazon-store-customer-feedback`。

---
*更多跨境 skill：[LinkFox Skills](https://skill.linkfox.com/)*

