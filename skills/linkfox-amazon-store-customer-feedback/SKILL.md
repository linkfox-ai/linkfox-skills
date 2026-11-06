---
name: linkfox-amazon-store-customer-feedback
description: 亚马逊商品与类目买家反馈洞察，支持查询评论主题、主题提及量、星级影响、评论趋势、退货主题及退货趋势，用于产品口碑、差评原因和类目问题分析。适用于按 ASIN 或类目查看聚合好评、差评和退货问题；不适用于逐条评论抓取、订单查询或退货订单处理。
---
# Amazon 店铺买家反馈洞察

## 适用范围

### 适用

查看已授权亚马逊店铺可访问的商品与类目聚合买家反馈。
用户希望判断商品口碑、评论主题、星级影响、类目反馈或退货问题时，使用本技能，无需明确提及 Customer Feedback。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 这个 ASIN 的好评、差评集中在哪里 | 商品评论主题：比较提及量与星级影响。 |
| 这个商品口碑最近有什么变化 | 商品评论趋势：展示返回的时间区间与变化。 |
| 查这个商品所属类目普遍遇到的问题 | 先确定类目，再读取类目评论主题与趋势。 |
| 这个类目有哪些退货原因，最近是否变化 | 类目退货主题及退货趋势。 |

### 边界

本技能使用 Customer Feedback 聚合洞察，不属于 Orders 订单查询；订单任务转交 `linkfox-amazon-store-orders`。逐条买家评论抓取不属于本技能范围。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 商品评论主题（`getItemReviewTopics`） | POST `/spApi/developerProxy` → GET path：`customerFeedback/2024-06-01/items/{asin}/reviews/topics` | `references/api.md` | `scripts/get_item_review_topics.py` | 查询商品评论主题。 |
| 商品所属类目（`getItemBrowseNode`） | POST `/spApi/developerProxy` → GET path：`customerFeedback/2024-06-01/items/{asin}/browseNode` | `references/api.md` | `scripts/get_item_browse_node.py` | 查询商品所属类目。 |
| 商品评论趋势（`getItemReviewTrends`） | POST `/spApi/developerProxy` → GET path：`customerFeedback/2024-06-01/items/{asin}/reviews/trends` | `references/api.md` | `scripts/get_item_review_trends.py` | 查询商品评论趋势。 |
| 类目评论主题（`getBrowseNodeReviewTopics`） | POST `/spApi/developerProxy` → GET path：`customerFeedback/2024-06-01/browseNodes/{browseNodeId}/reviews/topics` | `references/api.md` | `scripts/get_browse_node_review_topics.py` | 查询类目评论主题。 |
| 类目评论趋势（`getBrowseNodeReviewTrends`） | POST `/spApi/developerProxy` → GET path：`customerFeedback/2024-06-01/browseNodes/{browseNodeId}/reviews/trends` | `references/api.md` | `scripts/get_browse_node_review_trends.py` | 查询类目评论趋势。 |
| 类目退货主题（`getBrowseNodeReturnTopics`） | POST `/spApi/developerProxy` → GET path：`customerFeedback/2024-06-01/browseNodes/{browseNodeId}/returns/topics` | `references/api.md` | `scripts/get_browse_node_return_topics.py` | 查询类目退货主题。 |
| 类目退货趋势（`getBrowseNodeReturnTrends`） | POST `/spApi/developerProxy` → GET path：`customerFeedback/2024-06-01/browseNodes/{browseNodeId}/returns/trends` | `references/api.md` | `scripts/get_browse_node_return_trends.py` | 查询类目退货趋势。 |

## 前置条件

**先完成店铺授权并确定操作目标**：依赖 `linkfox-amazon-store-auth` 选店与完成授权。运行 `python scripts/check_auth_dependency.py` 检查依赖；缺失时先安装依赖，不在本技能内另行实现授权或令牌逻辑。确认目标店铺、站点和商品或类目；角色、站点支持及依赖检测约定见 `references/api.md`。

## 查询流程

1. 确认用户要分析商品还是类目，以及需要主题、趋势或二者对照；按任务范围选择操作，避免自动执行整套查询。
2. 用户需要商品评论主题时，查询商品评论主题；需要比较主题提及量与星级影响时，分别获取两种排序结果。
3. 用户需要时间变化时，再查询商品评论趋势。
4. 需要类目对照且尚无类目编号时，查询商品所属类目，从实际响应取得类目编号。
5. 按用户范围查询该类目的评论主题、评论趋势、退货主题和退货趋势，整合已有数据展示；失败或空结果时遵守调用约束，不自动换目标试探。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次，优先读取已保存的响应；脚本不读取或保存响应缓存。失败或空结果时，不得自动换目标或连续试探；需要继续查询时，先向用户说明原因和查询范围。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-amazon-store-customer-feedback-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、响应中可用的计数或状态字段（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
- 添加 `--inline` 可强制全量打印到标准输出，同时仍保存文件。

先通过摘要判断数据是否足够。需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

### 算力消耗预估

不消耗算力 （限时）。

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- HTTP 状态码为 `401` 或 `402`。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

### 约束与建议

- **区分反馈概念**：评论主题、星级影响与退货主题是不同的聚合视角；类目数据不能直接当作某个 ASIN 的实际退货记录。
- **清晰展示数据**：注明店铺、站点、ASIN 或类目及统计区间，用表格呈现响应中可用的主题、提及量、星级影响和趋势，不补造未返回指标。
- **先检查状态**：先检查外层响应与 `developerProxy.errcode`、`httpStatus`，再读各脚本解析字段。响应与店铺保护规则见 `references/api.md`，完整冷却及恢复指引见 `references/spapi-protection.md`。
- **说明数据时效**：注明 Amazon 返回的统计时间；刷新频率以 Amazon 为准，通常按周，不能按实时评论理解。

## 使用示例

### 分析商品口碑

用户：看看这个 ASIN 的主要好评、差评，以及近期变化。

确认店铺、站点与商品，按需比较评论主题的提及量和星级影响，再结合评论趋势说明变化，标明统计区间。

### 对照类目评论与退货问题

用户：这个商品所在类目普遍有哪些问题，退货原因有什么变化？

先取得商品所属类目，按范围查询类目评论与退货洞察，区分类目问题和商品证据，不将类目聚合数据解释为单品退货记录。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
