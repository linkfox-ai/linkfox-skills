---
name: linkfox-damai-mercado-market-intelligence
description: 使用大麦数据研究 Mercado Libre（美客多）的类目、行业规模、商品与属性聚合、销量趋势、图片相似商品和评论，覆盖墨西哥、巴西、阿根廷、智利、哥伦比亚。适用于美客多选品、市场调研、竞品研究和评论分析；不适用于店铺授权、商品发布、库存修改、订单履约、退款或广告运营。
---
# 大麦数据美客多市场洞察与选品

## 适用范围

### 适用

根据类目、关键词、商品、店铺或图片研究美客多市场，展示真实返回的市场与商品指标。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 找墨西哥手机类目、美客多类目编号 | 使用 `search_categories` 查找候选类目。 |
| 这个类目的市场规模和趋势 | 先定位类目，再使用 `industry_overview`。 |
| 筛选月销高的商品、查这个 SKU | 使用 `search_product_snapshots`。 |
| 这个商品最近销量如何 | 使用 `product_sales_trend`。 |
| 用这张图找美客多同款 | 使用 `image_search_products`。 |
| 分析这个商品的评论 | 使用 `review_search`。 |

## 接口清单

| 接口 | 端点 | 对应脚本 | 说明 |
|---|---|---|---|
| 搜索候选类目（`search_categories`） | POST `/damai/call` → `toolName=search_categories`（无上游 path 参数） | `scripts/damai_mercado_market_intelligence.py` | 查找类目与本地化路径，免费。 |
| 查询行业概览（`industry_overview`） | POST `/damai/call` → `toolName=industry_overview`（无上游 path 参数） | `scripts/damai_mercado_market_intelligence.py` | 读取类目规模与月度趋势。 |
| 搜索商品快照（`search_product_snapshots`） | POST `/damai/call` → `toolName=search_product_snapshots`（无上游 path 参数） | `scripts/damai_mercado_market_intelligence.py` | 按商品、店铺及指标筛选并返回属性聚合。 |
| 查询商品销量趋势（`product_sales_trend`） | POST `/damai/call` → `toolName=product_sales_trend`（无上游 path 参数） | `scripts/damai_mercado_market_intelligence.py` | 读取月度与 ISO 周销量和覆盖范围。 |
| 搜索图片相似商品（`image_search_products`） | POST `/damai/call` → `toolName=image_search_products`（无上游 path 参数） | `scripts/damai_mercado_market_intelligence.py` | 返回外观相似商品编号。 |
| 查询商品评论（`review_search`） | POST `/damai/call` → `toolName=review_search`（无上游 path 参数） | `scripts/damai_mercado_market_intelligence.py` | 读取评论原文、评分和买家字段。 |
| 获取图片上传预签名 | POST `/oss/file/presignedPut` | `scripts/upload_image.py` | 获取上传地址，随后向 OSS 执行 PUT，输出公开图片地址。 |

## 前置条件

确认用户需要研究的市场与对象。只有类目名称时，先定位类目，类目查询免费；本地图片由上传脚本处理。各接口参数与限制见 `references/api.md`。

## 查询流程

1. 根据任务选择类目、行业、商品、趋势、图搜或评论操作；使用目标市场的当地语言准备检索内容，按 `references/api.md` 校验请求。
2. 类目名称先通过类目查询确定，该操作免费；再进行需要的收费分析；本地图片先运行 `python scripts/upload_image.py <path>`，上传成功后再图搜，上传失败时停止图搜。
3. 连续调用多个收费操作、高频查询或翻页前，说明预计调用次数与算力消耗，由用户决定是否继续。按任务范围调用，先读摘要，按需提取已保存数据。图搜只得到商品编号时，先说明补充完整商品信息会产生另一笔查询消耗。
4. 按接口参考判断响应，展示筛选条件与实际数据覆盖。空结果不自动改词、翻页或换市场；超时、限流、5xx 或连接结果不明时不自动重放收费操作，说明不确定性，用户明确同意后再调用。
5. 大麦上游服务不可用时停止收费调用，提示稍后重试或联系管理员，不查询或展示上游账户信息。参数错误按参考修正，改变用户筛选意图前先询问。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python scripts/damai_mercado_market_intelligence.py '<JSON 参数>' [--inline] [--no-cache]`。
- **成本约束**：行业概览、商品搜索、销量趋势、图片搜索和评论查询每次成功调用消耗 12 LinkFox 算力（￥0.12）。同一会话、同一参数组合默认只调用一次，脚本提供 24 小时本地缓存。失败或空结果时，不得自动更换关键词、翻页或修改邮编连续试探；需要继续检索时，先向用户说明额外消耗。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-damai-mercado-market-intelligence-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
- 添加 `--inline` 可强制全量打印到标准输出，同时仍保存文件。

先通过摘要判断数据是否足够。需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

### 算力消耗预估

类目查询免费；行业概览、商品搜索、销量趋势、图片搜索、评论查询每次成功调用消耗 12 LinkFox 算力（￥0.12）。图片上传预签名的算力价格不确定，不推定免费或套用大麦业务操作的收费标准。

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

用户会因算力消耗而支付费用。需要高频调用或用户对消耗量预期不足时，提醒用户，并由用户决定是否继续。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- HTTP 状态码为 `401` 或 `402`。
- LinkFox 响应提示算力或余额不足、计费不足或需要充值。英文错误消息也按其含义判断。

### 约束与建议

- **数据含义**：类目结果含路径、层级及经营指标；行业结果含月度趋势与汇总；商品结果含销售、卖家、履约、库存及属性聚合；趋势结果含月度、周度序列及覆盖信息；图搜结果以商品编号为主；评论结果保留原文与评分。
- **据实展示**：只呈现响应支持的字段，不编造需求、利润、竞争或预测结论。注明市场、筛选条件、统计范围、记录数、币种与分页信息。
- **类目展示**：展示完整本地化路径及是否末级类目。
- **商品展示**：优先展示商品编号与标题、价格、近 30 天及累计订单、评分与评论数、卖家、类目、上架日期、履约及库存。
- **趋势展示**：区分请求天数与实际覆盖天数，明确覆盖不足提示。
- **评论展示**：保留原语言；仅当上游提供译文时标注翻译内容。
- **读取顺序**：优先读取业务数据；文本内容仅用于业务数据含义不清时辅助理解，原始上游响应仅在诊断时展示。
- **解释业务结果**：数据可能延迟或不完整，空记录、不可用标记和覆盖提示可能是正常业务结果；收费操作调用成功时，即使没有匹配记录也可能扣费。
- **认证与脱敏**：只通过 LinkFox 网关访问大麦数据，不直连上游或索要上游密钥。不暴露 LinkFox Key、上游凭证、完整 Base64、预签名查询参数或账号标识。
- **错误解释**：网关无权访问或托管上游认证失败时联系后端管理员，不能让用户提供上游 Key。按接口参考同时检查 HTTP、网关状态、错误消息与业务数据，不只依赖脚本退出码。

## 使用示例

### 免费查找类目

```json
{"toolName":"search_categories","arguments":{"market_code":"MLM","query":"celulares","limit":10}}
```

### 搜索类目商品

```json
{"toolName":"search_product_snapshots","arguments":{"market_code":"MLM","category_id":"MLM1055","sort_by":"sales_30d","sort_order":"desc","page":1,"limit":20}}
```

### 查询商品销量走势

```json
{"toolName":"product_sales_trend","arguments":{"market_code":"MLM","sku_id":"MLM1602785195","days":90}}
```

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
