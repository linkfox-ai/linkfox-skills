---
name: linkfox-youying-shopee-get-product-infos
description: 查询和筛选友鹰数据库中的 Shopee 商品，覆盖马来西亚、中国台湾、印尼、泰国、菲律宾、新加坡、越南、巴西、墨西哥、智利和哥伦比亚 11 个站点，支持关键词、价格、销量、上架时间、类目、店铺和商品属性组合筛选。适用于虾皮商品搜索、爆款与新品发现、品类选品、市场数据查看和竞品店铺商品比较，无需明确提及友鹰；不适用于其他平台搜索、Shopee 广告策略、店铺运营建议、物流仓储方案或已有本地数据文件的处理。
---

# 友鹰 Shopee 商品选品

## 适用范围

### 适用

按用户条件搜索和筛选 Shopee 商品，查看价格、销量、销售额、评分和店铺等数据。
用户提到“东南亚选品”“虾皮市场分析”或“跨境电商选品”，且具体需求是搜索或筛选 Shopee 商品时，使用本技能。

**场景速查**

| 用户表达 | 查询场景 |
|----------|----------|
| 虾皮上什么好卖、Shopee 爆款 | 按销量查热销商品。 |
| 帮我在 Shopee 搜某种商品 | 按标题关键词搜索。 |
| 马来站最近上架的新品 | 按上架日期发现新品。 |
| 销量过千的商品有哪些 | 按销量范围筛选。 |
| 东南亚哪些品类有机会 | 查看指定站点与类目的商品数据。 |
| 帮我看看这个店铺的商品 | 检索竞品店铺商品。 |
| 跨境商品和本土商品对比 | 按发货类型筛选与比较。 |
| Shopee 优选商品筛选 | 按优选标识筛选。 |
| 低价高销量的商品 | 组合价格和销量条件。 |

## 前置条件

**先确定目标站点**：用户未说明站点时，先询问要查询哪个 Shopee 站点。站点名称、代码及全部筛选条件见 `references/api.md`。

## 查询流程

1. 确认用户要查询的站点及商品范围，理解其关键词、类目、店铺、日期、价格和销量条件。
2. 阅读 `references/api.md`，将自然语言精确映射到对应筛选项；明确关键词匹配、排除逻辑、数值范围、排序和分页意图，避免添加用户未要求的条件。
3. 按用户条件构建请求并执行一次查询；后续检索遵守执行方式中的成本约束。
4. 先检查响应与保存文件的摘要，再按需读取商品字段；按接口定义解释错误和空结果，给出可调整的查询方向，由用户决定是否继续。
5. 用表格呈现核心商品数据，说明站点、币种、统计口径和本次返回范围；有图片时展示图片供用户判断。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python scripts/youying_shopee_search.py '<JSON 参数>' [--inline]`。
- **成本约束**：本工具每次调用消耗 4 算力。同一会话、同一参数组合默认只调用一次，脚本提供 24 小时本地缓存。失败或空结果时，不得自动更换关键词、翻页或修改邮编连续试探；需要继续检索时，先向用户说明额外消耗。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-youying-shopee-get-product-infos-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
- 添加 `--inline` 可强制全量打印到标准输出，同时仍保存文件。

先通过摘要判断数据是否足够。需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

### 算力消耗预估

4 算力 / 次

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

用户会因算力消耗而支付费用。需要高频调用或用户对消耗量预期不足时，提醒用户，并由用户决定是否继续。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- 响应状态码为 `401` 或 `402`。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

### 约束与建议

- **理解数据维度**：销量包括近 30 天实际销量、近 30 天估算销量和累计销量；价格包括默认价与 SKU 最低、最高价。店铺数据区分官方店、虾皮优选、本地或海外、跨境或本土；商品数据还包括评分、评分数、收藏、浏览、SKU 数量、上架时间及类目。
- **区分销量口径**：展示时明确 `sold` 为前 30 天销量、`estimateSold` 为估算前 30 天销量、`historicalSold` 为累计销量、`payment` 为前 30 天销售额，避免混用。
- **清晰展示数据**：使用表格，优先展示标题、`price`、`sold`、`payment` 和 `rating`，不附加主观经营建议。
- **标明币种**：展示价格和销售额时提醒用户其为目标站点的当地货币。各站点币种对应关系见接口定义。
- **说明返回范围**：结果较多时先展示核心数据，告知可通过分页查看更多；实际继续调用遵守成本约束，分页限制见接口定义。
- **展示图片**：返回 `imageUrl` 时附商品图片，帮助用户直观判断。
- **说明数据时效**：数据取决于友鹰抓取进度，使用 `lastModiTime` 说明更新情况，不将其表述为实时成交数据。
- **解释失败原因**：依据接口定义及实际错误消息解释查询失败，建议核对站点或筛选条件；不把空结果直接解释为市场没有需求。

## 使用示例

### 关键词选品：按销量筛选热销商品

```json
{"station":"malaysia","keyword":"Storage Box","keywordType":2,"soldMin":100,"orderBy":"sold","orderByType":"DESC","pageSize":100}
```

### 新品发现：近期上架且有一定销量

```json
{"station":"thailand","keyword":"Phone Case","listingDateFrom":"2025-06-01","soldMin":50,"orderBy":"gen_time","orderByType":"DESC"}
```

### 低价高销量商品

```json
{"station":"indonesia","keyword":"LED Light","priceMax":50000,"soldMin":500,"orderBy":"payment","orderByType":"DESC"}
```

### 跨境卖家商品筛选

```json
{"station":"malaysia","keyword":"Wireless Earbuds","cbOption":1,"soldMin":200,"orderBy":"sold","orderByType":"DESC"}
```

### 品类选品：按类目和销售额筛选

```json
{"station":"vietnam","pL1Id":"11036379","paymentStart":10000000,"orderBy":"payment","orderByType":"DESC","pageSize":200}
```

### 竞品店铺商品

```json
{"station":"malaysia","shopIdList":"123456789","orderBy":"sold","orderByType":"DESC"}
```

### 优选且高评分的商品

```json
{"station":"philippines","keyword":"Beauty","isShopeeVerified":1,"ratingMin":4.5,"soldMin":100,"orderBy":"rating","orderByType":"DESC"}
```

### 排除大卖店铺

```json
{"station":"taiwan_china","keyword":"收纳盒","notExistShopIdList":"111111,222222,333333","soldMin":50,"soldMax":500,"orderBy":"sold","orderByType":"DESC"}
```

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。