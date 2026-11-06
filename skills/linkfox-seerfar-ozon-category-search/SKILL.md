---
name: linkfox-seerfar-ozon-category-search
description: 按 Ozon 类目编号查询 Seerfar 数据库中的商品列表，返回类目总销量、总销售额、平均价格、平均评分、季节性及商品销量、价格、评分、评论数、品牌、卖家和配送方式。适用于 Ozon 类目选品分析、爆品挖掘、市场容量、价格带和季节性研究。当用户希望查看某个 Ozon 类目的商品及汇总数据时使用，无需明确提及 Seerfar。店铺查询、关键词搜索和单品详情查询使用对应技能。
---

# Seerfar Ozon 类目商品搜索

## 适用范围

### 适用

查看单个 Ozon 类目的商品及汇总数据。
用户已有 `categoryId`，或能够从上游数据源确定编号，且希望按销量、价格、评分列举或排序该类目商品、判断类目容量时，使用本技能。

**场景速查**

| 用户表达 | 查询场景 |
|----------|----------|
| 分析下这个 Ozon 类目的商品 | 类目容量：总销量、总销售额和平均价格。 |
| 这个类目最畅销的商品是什么 | 爆品挖掘：按 `sales` 排序。 |
| 这个类目销售额最高的商品 | 高销售额商品：按 `revenue` 排序。 |
| 这个类目的价格带或客单价 | 价格带分析：查看平均价格，按 `price` 排序。 |
| 这个类目评分最高的商品 | 高评分商品：按 `reviewRating` 排序。 |
| 这个类目上个月的数据 | 历史月份快照：传入 `date`。 |
| 这个类目采用 FBO 配送的商品 | 配送方式筛选：传入 `fulfillment`。 |


### 边界
店铺查询、关键词发现和单品深查转交对应技能。

**其他场景的技能选择**：

- 查看某个店铺或卖家的商品：使用 Seerfar Ozon 店铺搜索技能。
- 在整个市场中按关键词搜索：使用 Seerfar Ozon 市场关键词搜索技能。
- 挖掘关键词：使用 Seerfar Ozon 关键词挖掘技能。
- 查看单个商品的完整详情：使用 Seerfar Ozon 商品详情数据源。

## 前置条件

**先确定类目编号**：用户提供类目名称时，先从上游 Seerfar Ozon 数据源取得 `categoryId`。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python scripts/seerfar_ozon_category_search.py '<JSON 参数>' [--inline]`。
- **成本约束**：本工具会消耗算力。同一会话、同一参数组合默认只调用一次，脚本提供 24 小时本地缓存。失败或空结果时，不得自动更换关键词、翻页或修改邮编连续试探；需要继续检索时，先向用户说明额外消耗。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-seerfar-ozon-category-search-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。按原技能要求，禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
- 添加 `--inline` 可强制全量打印到标准输出，同时仍保存文件。

先通过摘要判断数据是否足够。需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

### 算力消耗

15 算力 / 次

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

用户会因算力消耗而支付费用。需要高频调用或用户对消耗量预期不足时，提醒用户，并由用户决定是否继续。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- 响应状态码为 `401` 或 `402`。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

### 约束与建议

- **传入排序规则**：类目商品可能很多，建议始终传入 `page.orders`。按 `sales` 降序查畅销商品，按 `revenue` 降序查高销售额商品，按 `price` 降序查高价带，按 `reviewRating` 降序查高评分商品。
- **清晰展示数据**：用表格呈现类目汇总和商品指标，不附加主观建议。
- **先展示类目背景，再展示商品**：优先用 `categoryInfo.cnTitlePath` 核对类目名称；缺失时可用 `enTitlePath`。展示类目总销量、总销售额、平均价格、平均评分、季节性（`seasonalityAmplitude`、`seasonalityCoef`）和统计区间。用一行概括 `sellerType` 中各配送方式的商品数，再用表格展示商品编号、标题、价格、销量、销售额、评分、评论数、品牌和卖家，对应 `sku`、`title`、`price`、`sales`、`revenue`、`reviewRating`、`reviewCount`、`brandName`、`sellerName`。
- **标明币种**：价格和销售额以卢布（₽）展示，使用响应中的 `currency` 符号。
- **展示配送方式**：响应中的商品 `fulfillment` 是数组，例如 `["FBO"]`；有多个值时用 `/` 连接。
- **避免重复字段**：`productId`、`rating`、`brand`、`monthlySalesUnits`、`monthlySalesRevenue`、`productPageUrl` 分别对应 `sku`、`reviewRating`、`brandName`、`sales`、`revenue`、`productUrl`。展示一组即可，优先使用原始字段。
- **说明分页情况**：`hasNextPage` 为真时，告知用户可通过 `page.page` 查看更多页，并提醒每页最多 20 条。
- **解释空结果**：不存在的类目编号可能返回成功状态及 `total=0`、空商品列表。提示用户核对类目编号，不将其直接认定为系统错误。
- **解释错误原因**：`code` 不为 `"200"` 或 `errcode` 不为 `200` 时，根据 `msg` 或 `errmsg` 解释原因，给出补充 `page`、调小 `pageSize` 或限流后稍候重试等建议；后续调用遵守成本约束。

## 使用示例

### 类目畅销商品：按近 30 天销量降序

```json
{"categoryId": "15621032_15621049_115951147", "page": {"page": 1, "pageSize": 20, "orders": [{"field": "sales", "direction": "DESC"}]}}
```

### 类目销售额最高的商品

```json
{"categoryId": "15621032_15621049_115951147", "page": {"page": 1, "pageSize": 20, "orders": [{"field": "revenue", "direction": "DESC"}]}}
```

### 类目高价商品：按价格降序

```json
{"categoryId": "15621032_15621049_115951147", "page": {"page": 1, "pageSize": 20, "orders": [{"field": "price", "direction": "DESC"}]}}
```

### 历史月份快照

```json
{"categoryId": "15621032_15621049_115951147", "date": "2026-02", "page": {"page": 1, "pageSize": 20, "orders": [{"field": "sales", "direction": "DESC"}]}}
```

### 仅查看采用 FBO 配送的商品

```json
{"categoryId": "15621032_15621049_115951147", "fulfillment": "FBO", "page": {"page": 1, "pageSize": 20, "orders": [{"field": "sales", "direction": "DESC"}]}}
```

### 查询类目的第二页商品

```json
{"categoryId": "15621032_15621049_115951147", "page": {"page": 2, "pageSize": 20, "orders": [{"field": "sales", "direction": "DESC"}]}}
```

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。