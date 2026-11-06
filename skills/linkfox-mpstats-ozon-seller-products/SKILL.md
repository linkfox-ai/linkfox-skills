---
name: linkfox-mpstats-ozon-seller-products
description: 按卖家 ID 查看 MPSTATS Ozon 俄罗斯站店铺商品，返回各 SKU 的销量、销售额、价格、评分、库存、周转和损失销售额，支持数值筛选、排序与货币换算。适用于店铺结构分析、店内畅销商品拆解及竞争店铺对标，无需明确提及 MPSTATS。品牌或类目商品查询、单品趋势及其他平台数据不在本技能范围，也不提供采购或跟卖建议。
---

# MPSTATS Ozon 卖家商品

## 适用范围

### 适用

查看指定 Ozon 卖家下各 SKU 的销售表现，用于店铺结构、畅销商品、库存周转、缺货损失及竞争店铺对比。

**场景速查**

| 用户表达 | 查询场景 |
|----------|----------|
| 看卖家 3628678 的商品，按销量排 | 店铺 SKU 分布与销量排行。 |
| 这家 Ozon 店铺哪些商品销售额最高 | 店内高销售额商品。 |
| 店里周转低于 20 天的商品有多少 | 按周转指标筛选商品。 |
| 这家店哪些商品因缺货损失销售额 | 缺货损失扫描。 |
| 比较两家 Ozon 店铺的 SKU 数和销量 | 分别查询两名卖家，按相同口径对比。 |

### 边界

只有卖家名称时，先用 MPSTATS Ozon 商品搜索（`mpstats-ozon-product-search`）按卖家筛选并读取 `sellerId`。品牌维度使用 `mpstats-ozon-brand-products`，类目维度使用 `mpstats-ozon-category-products`，单 SKU 时间序列使用 `mpstats-ozon-product-trend`。这些名称表示对应数据源能力，使用前确认当前环境可用。
“某类目有哪些头部卖家”应查询类目商品后在本地按卖家汇总。Wildberries 及其他市场不属于本技能。

## 前置条件

先确定目标卖家编号与统计口径；名称、品牌名及类目路径不能替代卖家编号。具体参数约定见 `references/api.md`。

## 查询流程

1. 确认卖家及任务：查看店铺商品分布、销量或销售额排行、周转表现、缺货损失，或比较两家店铺。
2. 根据任务准备排序、筛选、统计区间和货币口径，按 `references/api.md` 核对请求；比较店铺时统一口径，并说明每名卖家需要单独查询。
3. 按下方算力预估提醒用户，由用户决定是否继续；取得结果后先看摘要，按需读取已保存的完整响应。失败或空结果时遵守成本约束。
4. 展示本次返回的商品和查询范围；大型店铺优先收紧筛选，再考虑继续翻页。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python scripts/mpstats_ozon_seller_products.py '<JSON 参数>' [--inline]`。
- **成本约束**：本工具按下方算力规则计费。同一会话、同一参数组合默认只调用一次，脚本提供 24 小时本地缓存。失败或空结果时，不得自动更换关键词、翻页或修改邮编连续试探；需要继续检索时，先向用户说明额外消耗。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-mpstats-ozon-seller-products-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8000 个 UTF-8 字节：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8000 个 UTF-8 字节：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
- 添加 `--inline` 可强制全量打印到标准输出，同时仍保存文件。

先通过摘要判断数据是否足够。需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

### 算力消耗预估

按动态规则计费：消耗算力 = 12；列表为空返回 0 算力 （限时）。本服务按倍数动态计算，可能一次性消耗大量算力，必须提醒用户，由用户决定是否继续。

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

用户会因算力消耗而支付费用。需要高频调用或用户对消耗量预期不足时，提醒用户，并由用户决定是否继续。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- 响应状态码为 `401` 或 `402`。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

### 约束与建议

- **区分查询维度**：卖家编号代表店铺；本技能返回该店铺下商品的指标，不把卖家、品牌和类目混为同一维度。
- **说明统计口径**：FBO 表示平台仓配，FBS 表示卖家自发货；展示时说明是否纳入 FBS、统计区间和币种，参数语义见 `references/api.md`。
- **紧凑展示店铺商品**：表格优先列出 `productId`、`title`、`brand`、`price`、`monthlySalesUnits`、`monthlySalesRevenue`、`rating`、`balance`、`turnoverDays`、`lostProfit`、`position`。销量和销售额按实际统计期解释，不能仅根据字段名认定为自然月数据。
- **明确占比分母**：`revenueSharePercent` 是本次卖家查询维度内的销售额占比，不是全市场份额；只展示实际返回值。
- **保留俄语标题**：按响应保留标题，用户要求时再翻译。
- **标注货币换算**：使用响应中的币种；换算后注明“已按 USD 换算”等实际目标币种。
- **说明覆盖范围**：区分命中总数和当前页商品数，不把单页当作店铺全部 SKU；大型店铺先收紧筛选再深翻页。
- **仅呈现数据**：可以解释店铺指标及对比结果，不作采购、选品开发或跟卖推荐，不据此判断某 SKU 是否值得复制。
- **处理异常**：按 `references/api.md` 的公共响应规则和业务说明解释错误或空结果，保留已取得的数据，不自动改参数连续试探。

## 使用示例

### 店铺销量前 100 个商品

```json
{"sellerId":"3628678","sortField":"sales","sortDirection":"desc","pageSize":100}
```

### 店铺销售额前 20 个商品

```json
{"sellerId":"3628678","sortField":"revenue","sortDirection":"desc","pageSize":20}
```

### 筛选销量与周转符合要求的商品

```json
{"sellerId":"3628678","filters":[{"field":"sales","op":"GTE","value":30},{"field":"turnover_days","op":"LTE","value":20}],"sortField":"revenue","sortDirection":"desc"}
```

### 查看缺货损失较高的商品

```json
{"sellerId":"3628678","filters":[{"field":"lost_profit","op":"GTE","value":100000}],"sortField":"lost_profit","sortDirection":"desc"}
```

### 按美元查看店铺商品

```json
{"sellerId":"3628678","currency":"USD","sortField":"revenue","sortDirection":"desc"}
```

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。