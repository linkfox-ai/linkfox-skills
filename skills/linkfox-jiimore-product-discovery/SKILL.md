---
name: linkfox-jiimore-product-discovery
description: 基于极目数据按关键词发掘亚马逊潜力商品，结合转化率、点击量与增长率、价格、评论、上架时间、毛利、FBA 费用、卖家来源和细分市场数量筛选与排序。适用于关键词选品、高转化或快速增长商品发现、新品机会核对及竞品对标；无需明确提及极目。不适用于 ABA 搜索词分析、广告管理、评论内容分析、Listing 优化、库存供应链管理或完整利润与定价策略报告。
---

# 极目亚马逊商品发掘

## 适用范围

### 适用

从关键词出发，按商品表现筛选候选，并返回可核对的商品数据。
用户希望发现潜力爆品、高转化商品、点击增长机会，或比较利润、评论与卖家来源时，使用本技能。

**场景速查**

| 用户表达 | 查询场景 |
|----------|----------|
| 找这个关键词下的热门商品 | 关键词驱动的商品发现。 |
| 找高转化商品或潜力爆品 | 按转化表现筛选商品。 |
| 找近期增长快的商品 | 结合点击量和点击增长表现筛选。 |
| 看看有潜力的新品 | 结合上架时间和增长指标筛选。 |
| 找毛利较高的商品 | 结合毛利与 FBA 费用筛选。 |
| 找评论少、竞争可能较低的商品 | 列出低评论候选，保留可核对的指标。 |
| 找中国卖家的商品 | 按卖家来源筛选。 |
| 挖掘细分市场机会 | 结合细分市场数量和综合转化表现筛选。 |

## 前置条件

**先确定检索目标**：明确用户要研究的关键词、目标站点和筛选重点。按 `references/api.md` 准备请求，避免以未指定的条件扩大检索范围。

## 商品发掘流程

1. 明确检索目标，未指定站点时沿用接口默认值，依据接口定义准备目标语言的关键词、筛选条件、排序和分页信息。
2. 核对已有会话结果与本地缓存，复用同一参数组合的数据；需要新查询时遵守成本约束。
3. 执行一次查询，先查看保存路径和摘要，再从完整响应中按需提取商品与指标。
4. 按下方展示建议整理结果，说明查询范围、分页和缺失数据；失败或空结果时按接口定义解释原因，后续检索遵守成本约束。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python scripts/jiimore_product_discovery.py '<JSON 参数>' [--inline]`。
- **成本约束**：本工具会消耗算力。同一会话、同一参数组合默认只调用一次，脚本提供 24 小时本地缓存。失败或空结果时，不得自动更换关键词、翻页或修改邮编连续试探；需要继续检索时，先向用户说明额外消耗。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-jiimore-product-discovery-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
- 添加 `--inline` 可强制全量打印到标准输出，同时仍保存文件。

先通过摘要判断数据是否足够。需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

### 算力消耗预估

9 算力 / 次

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

用户会因算力消耗而支付费用。需要高频调用或用户对消耗量预期不足时，提醒用户，并由用户决定是否继续。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- 响应状态码为 `401` 或 `402`。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

### 约束与建议

- **理解数据用途**：这是关键词驱动的商品筛选工具，用转化、点击增长、利润、价格、评论和上架时间等指标发现候选、核对产品想法和对标竞品；筛选命中不等于商业成功。
- **清晰展示数据**：用表格展示实际返回的标题、ASIN、价格、评论或评分、转化率、点击量与增长表现；缺失字段标明未返回，不推算补齐。
- **比例展示**：将返回的比例转换为百分比，例如将 0.12 展示为 12%；请求中的数值格式见接口定义。
- **主图展示**：有商品图片链接时，将主图与商品数据一起展示。
- **说明分页情况**：展示总量、当前页和本次返回范围；有更多页时告知可以继续获取，后续查询遵守成本约束。
- **说明语言选择**：向用户说明检索使用的关键词及目标语言，便于核对翻译是否符合产品含义；站点与语言约定见接口定义。
- **客观呈现结果**：仅基于真实返回的数据说明商品表现，不附加主观商业推荐，不生成完整利润或定价策略。
- **解释错误原因**：按 `references/api.md` 判断响应并解释错误，必要时建议用户调整条件；不得自动连续试探。

## 使用示例

### 美国站高转化无线充电器

```json
{
  "keyword": "wireless charger",
  "countryCode": "US",
  "clickConversionRateMin": 0.1,
  "sortField": "clickConversionRate",
  "sortType": "desc"
}
```

### 指定日期后上架且周点击增长较快的台灯

```json
{
  "keyword": "desk lamp",
  "countryCode": "US",
  "launchDateMin": "20250901000000",
  "clickCountGrowthT7Min": 0.2,
  "sortField": "clickCountGrowthT7",
  "sortType": "desc"
}
```

### 价格较低、毛利较高且评论较少的手机支架

```json
{
  "keyword": "phone stand",
  "countryCode": "US",
  "priceMin": 10,
  "priceMax": 30,
  "totalReviewsMax": 100,
  "grossProfitMarginMin": 0.3,
  "sortField": "gpm",
  "sortType": "desc"
}
```

### 德国站中国卖家且月点击增长较快的手机壳

```json
{
  "keyword": "Handyhuelle",
  "countryCode": "DE",
  "sellerCountry": "CN",
  "clickCountGrowthT30Min": 0.15,
  "sortField": "clickCountGrowthT30",
  "sortType": "desc"
}
```

### 日本站评分较高且年销量较多的无线耳机

```json
{
  "keyword": "ワイヤレスイヤホン",
  "countryCode": "JP",
  "customerRatingMin": 4.0,
  "salesVolumeT360Min": 1000,
  "sortField": "purchasedClicksT360",
  "sortType": "desc"
}
```

### 综合转化较高且覆盖多个细分市场的瑜伽垫

```json
{
  "keyword": "yoga mat",
  "countryCode": "US",
  "clickConversionRateCompositeMin": 0.15,
  "nicheCountMin": 3,
  "sortField": "clickConversionRateComposite",
  "sortType": "desc"
}
```

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
