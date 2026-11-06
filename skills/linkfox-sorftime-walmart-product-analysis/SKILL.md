---
name: linkfox-sorftime-walmart-product-analysis
description: 使用 Sorftime 按自然语言商品名称发现 Walmart 美国站相关商品，或围绕已知 ProductId 查询商品详情、历史趋势和按日或变体销量。适用于竞品发现、当前价格与评分核对、历史变化和销量跟踪；不适用于类目市场研究、关键词指标或反查、多条件商品筛选。
---
# Walmart 产品分析

## 适用范围

### 适用

从自然语言名称发现 Walmart 美国站相关商品，或研究已知 ProductId 的当前资料、历史变化及销量记录。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 按商品名称找相关 Walmart 产品 | 名称发现：展示相关商品及本页范围。 |
| 看这个 ProductId 的价格、评分或类目排名 | 商品详情：展示当前商品摘要。 |
| 这个商品的价格、评分或排名怎么变化 | 商品趋势：识别时间序列并说明变化。 |
| 看这个商品按日销量、变体销量或昨日销量 | 销量记录：展示指定时间范围的记录。 |

## 接口清单

| 接口 | 端点 | 对应脚本 | 说明 |
|---|---|---|---|
| 名称搜索（`searchByName`） | POST `/sorftime/walmart/productAnalysis`；`operation=searchByName` | `scripts/sorftime_walmart_product_analysis.py` | 按自然语言名称发现相关商品。 |
| 商品详情（`detail`） | POST `/sorftime/walmart/productAnalysis`；`operation=detail` | `scripts/sorftime_walmart_product_analysis.py` | 查询当前商品摘要。 |
| 商品趋势（`trend`） | POST `/sorftime/walmart/productAnalysis`；`operation=trend` | `scripts/sorftime_walmart_product_analysis.py` | 查询商品历史变化。 |
| 销量记录（`salesVolume`） | POST `/sorftime/walmart/productAnalysis`；`operation=salesVolume` | `scripts/sorftime_walmart_product_analysis.py` | 查询按日或变体销量。 |

## 前置条件

先确定本次需要的查询场景，以及商品名称或目标 ProductId；历史销量查询还应明确用户需要的时间范围。调用前阅读 `references/api.md` 中对应操作的定义。

## 查询流程

1. 根据用户目的选择名称发现、当前详情、历史趋势或销量记录，补齐目标信息；不得默认把四项全部查询。
2. 按 `references/api.md` 准备对应请求，优先复用相同参数的有效缓存，执行用户要求的查询。
3. 先查看摘要，再按需提取已保存的数据；按查询场景解释结果及实际消耗。
4. 需要另一操作、下一页或不同日期范围时，先说明额外消耗并取得用户授权，不自动补查。失败、空结果也遵守这一要求。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python scripts/sorftime_walmart_product_analysis.py '<JSON 参数>' [--inline] [--no-cache]`。
- **成本约束**：本工具会消耗算力。同一会话、同一参数组合默认只调用一次，脚本提供 24 小时本地缓存。失败或空结果时，不得自动更换关键词、翻页或修改邮编连续试探；需要继续检索时，先向用户说明额外消耗。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-sorftime-walmart-product-analysis-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、HTTP 状态（`_http_status`）、常见计数（如 `total`、`costToken`、由响应头复制的 `costCredit`）、最大列表字段的长度和前 3 条样本。
- 添加 `--inline` 可强制全量打印到标准输出，同时仍保存文件。

先通过摘要判断数据是否足够。需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

### 算力消耗预估

按动态规则计费：单个 Sorftime Request 参考 6 算力；名称搜索和商品趋势各消耗 2 Request，商品详情和销量记录各消耗 1 Request。多 Request 操作由网关按整单计算并取整，最终以入口脚本返回的 `costCredit` 为准，不要简单用 `requestConsumed × 6` 代替实际账单。无数据与计费的特殊判断见 `references/api.md`。

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

用户会因算力消耗而支付费用。需要高频调用或用户对消耗量预期不足时，提醒用户，并由用户决定是否继续。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- HTTP 状态码为 `401` 或 `402`。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

### 约束与建议

- **区分查询目的**：名称搜索用于自然语言相关商品发现；详情用于当前快照；趋势用于历史属性；销量记录用于带日期的销量，不将名称搜索解释为多条件商品库或类目市场查询。
- **说明查询与消耗**：注明本次操作、商品名称或编号及返回的 `requestConsumed`、`costCredit`、`costToken`。缓存命中时说明这些数值来自原请求，本次没有新增生产扣费。
- **相关性与分页**：名称搜索结果标为相关商品，不承诺精确匹配；同时说明本次请求页码。
- **忠实展示详情**：仅展示 ProductSummeryObject 实际返回的字段，不推断缺失属性。
- **正确解释趋势和销量**：先从响应确认时间字段、单位及编码，再总结变化；销量记录的解析及昨日记录标记见 `references/api.md`。
- **区分估算与事实**：准确标注预估销量、预估销售额或观测值，不将其称为已确认的 Walmart 交易。
- **说明数据覆盖**：历史覆盖及指标可用性由 Sorftime 决定；不承诺固定最早日期，不补造缺失数据。

## 使用示例

### 按名称发现相关商品

用户：找一下 Walmart 上和无线耳机相关的商品。

使用名称搜索，展示相关商品和本次返回范围，不自动查询每个商品的详情。

### 查看当前详情

用户：查 ProductId 5169493923 的当前价格和评分。

读取指定商品详情，仅使用返回字段展示当前摘要。

### 查看商品历史趋势

用户：看 ProductId 5169493923 的价格和排名变化。

读取趋势，确认日期编码、金额单位和类目排名结构后解释变化。

### 查看指定时间范围的销量

用户：查 ProductId 5169493923 在 2026 年 7 月的按日销量。

按用户指定范围读取销量记录，说明返回记录与数据覆盖情况；补查其他页需先说明额外消耗并取得授权。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
