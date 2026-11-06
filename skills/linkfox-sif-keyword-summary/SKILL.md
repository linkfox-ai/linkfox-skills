---
name: linkfox-sif-keyword-summary
description: 分析亚马逊指定关键词下竞品 ASIN 的流量来源及竞争格局，比较自然搜索、SP 广告、SB 品牌广告、SBV 视频广告、SP 推荐及 AC/ER/TR 推荐位曝光，支持指定竞品、时间区间和新进流量筛选。适用于关键词自然与付费流量占比、广告竞争和推荐位广告与非广告拆分分析，无需明确提及 SIF；不适用于整品跨关键词流量汇总、历史排名趋势、广告竞价与预算优化、评论与 Listing 内容、销量估算或搜索量曲线研究。
---

# SIF 关键词流量来源分析

## 适用范围

### 适用

查看某个亚马逊关键词下出现的 ASIN，分析各竞品通过哪些渠道获得曝光，并对比该词下的流量结构与商品整体流量结构。

**场景速查**

| 用户表达 | 查询场景 |
|----------|----------|
| 这个关键词的流量从哪里来，是否被广告主导 | 自然搜索与付费曝光占比、广告饱和程度。 |
| 哪些竞品在抢这个词的流量 | 关键词下 ASIN 流量分布与竞争格局。 |
| 谁在投 SP、品牌或视频广告 | SP、SB、SBV 广告竞争。 |
| 哪些商品进入 SP 推荐位 | SP 推荐曝光及推荐位广告与非广告拆分。 |
| 哪些商品有 Amazon's Choice、编辑推荐或高评分推荐曝光 | AC、ER、TR 推荐渠道分析。 |
| 比较这两个 ASIN 在这个词下的流量 | 指定竞品对比。 |
| 看某一周或本期新进流量 | 自定义统计区间或新进流量筛选。 |

### 边界

整品跨关键词流量、关键词计数与变体汇总使用 SIF ASIN 流量来源工具；超出当前或自定义统计窗口的历史关键词排名趋势使用 ABA 等对应数据工具。广告竞价与预算优化、评论与 Listing 内容、销量估算和完整搜索量曲线不属于本技能范围。

## 前置条件

先确定种子关键词、目标站点及分析目标；关键词尽量使用目标站点的语言。按需确认待比较的竞品和统计时间范围，参数及支持范围见 `references/api.md`。

## 查询与分析流程

1. 明确用户希望查看整体竞争格局、自然与付费占比、特定广告或推荐渠道，还是比较指定竞品。
2. 按 `references/api.md` 选择对应筛选、时间和排序方式，优先复用同参数已有结果，再运行脚本取得数据。
3. 先查看返回摘要，按需从保存文件提取竞品与渠道指标；核对网关状态和 SIF 业务状态，空结果或失败按接口定义解释，不自动追加试探查询。
4. 按用户问题选择商品级或关键词级指标，用表格比较流量结构，注明统计区间和本次返回范围，再概括主要曝光来源。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python scripts/sif_keyword_traffic.py '<JSON 参数>' [--inline]`。
- **成本约束**：本工具会消耗算力。同一会话、同一参数组合默认只调用一次，脚本提供 24 小时本地缓存。失败或空结果时，不得自动更换关键词、翻页或修改邮编连续试探；需要继续检索时，先向用户说明额外消耗。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-sif-keyword-summary-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
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

- **区分指标口径**：无 `keyword` 前缀的曝光指标表示 ASIN 在所有关键词上的商品级表现，例如 `naturalSearchExposureScore`；`keyword*` 表示仅本次查询关键词的表现，例如 `keywordNaturalExposureScore`。列名明确标注口径，禁止混用；用户问“这个词”时优先使用关键词级字段。
- **理解流量渠道**：自然搜索为自然结果位；SP 为商品广告常规位，SB 为搜索页头部或底部品牌广告，SBV 为品牌视频广告。SP 推荐覆盖 Trending now、Seen on social media、Customers frequently viewed、4 stars and above 等位置；AC 为 Amazon's Choice，ER 为编辑推荐，TR 为高评分推荐。展示推荐位时区分广告和非广告曝光。
- **清晰展示数据**：用中文友好列名和表格按渠道展示各 ASIN 的曝光得分及可用占比，突出自然与付费的对比。接口未直接给出的占比若需计算，注明分子与分母及其口径；不要把得分直接当作占比。
- **格式化比例**：比例字段转为百分比，例如 `0.45` 展示为 `45%`。单个 ASIN 附简短流量构成概括，结论必须与所用口径一致。
- **标注统计时间**：注明最近七天或已解析的自定义起止日期，并展示每行的 `dataPeriodStartDate`；跨商品比较曝光或计数时先核对统计窗口。
- **说明返回范围**：大结果先展示核心数据和本次返回数量，再告知可分页查看更多；不要把本页记录数当作全部竞品数量。后续请求遵守成本约束。
- **解释失败原因**：依据 `msg` 或 `errmsg` 解释原因，建议核对关键词拼写、站点和其他参数；完整判断规则及接口限制见 `references/api.md`。

## 使用示例

### 美国站关键词流量概览

```json
{"searchKeyword": "wireless charger", "country": "US"}
```

### 仅查看自然搜索曝光

```json
{"searchKeyword": "wireless charger", "country": "US", "condition": "nfPosition"}
```

### 查看 SP 广告竞争

```json
{"searchKeyword": "wireless charger", "country": "US", "condition": "isSpAd"}
```

### 查看 SP 推荐位

```json
{"searchKeyword": "wireless charger", "country": "US", "condition": "acAd"}
```

### 日本站使用当地语言关键词

```json
{"searchKeyword": "ワイヤレス充電器", "country": "JP"}
```

### 比较指定竞品

```json
{"searchKeyword": "wireless charger", "country": "US", "asins": "B01NBNDC1T,B09VLJJPL6"}
```

### 查看指定日期区间

```json
{"searchKeyword": "wireless charger", "country": "US", "last7d": false, "startDate": "2026-04-05", "endDate": "2026-04-11"}
```

### 按商品整体 SP 曝光排序

```json
{"searchKeyword": "wireless charger", "country": "US", "sortBy": "totalSpSocre", "desc": true}
```

### 查看本期新进流量

```json
{"searchKeyword": "wireless charger", "country": "US", "condition": "totalPeriod.in"}
```

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。