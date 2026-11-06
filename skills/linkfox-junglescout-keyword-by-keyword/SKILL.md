---
name: linkfox-junglescout-keyword-by-keyword
description: 使用 Jungle Scout 从一个亚马逊种子关键词拓展相关词和长尾词，提供搜索量、月度与季度趋势、PPC 建议出价、相关性和排名难度，覆盖美国、英国、德国、日本等 10 个站点。适用于关键词挖掘、关键词发现、关键词建议、低竞争词筛选、PPC 竞价研究和综合关键词调研，无需明确提及 Jungle Scout。单个关键词历史搜索量、ABA 搜索排名、ASIN 反查、商品搜索、Listing 分析和非亚马逊关键词研究不适用。
---

# Jungle Scout 根据关键词扩展关键词信息

## 适用范围

### 适用

从种子关键词发现相关词、扩充 Listing 词库、寻找长尾机会，结合搜索需求、竞争和广告出价开展关键词研究。

**场景速查**

| 用户表达 | 查询场景 |
|----------|----------|
| 帮我拓展这个关键词 | 从种子词发现相关词。 |
| 这个词有哪些相关关键词 | 相关词挖掘。 |
| 找一些长尾词 | 按词数筛选长尾关键词。 |
| 竞争度低的词有哪些 | 综合排名容易度和自然商品数量评估竞争。 |
| 这个词的 PPC 出价多少 | 查看精确匹配、广泛匹配和品牌广告建议出价。 |
| 搜索量大的相关词 | 高搜索量关键词筛选。 |
| 德国站有什么相关词 | 非美国站关键词拓展。 |
| 帮我做关键词调研 | 结合搜索量、趋势、相关性与竞争开展综合研究。 |

### 边界

单个关键词随时间变化的历史搜索量应使用关键词历史查询能力；ABA 搜索词排名、ASIN 反查关键词、商品搜索、Listing 分析及非亚马逊数据不在本技能范围。用户只说“关键词研究”时，根据其要拓展词表还是查看历史趋势判断。

## 前置条件

先确定用户提供的种子词、目标市场和研究目的，按 `references/api.md` 中的站点映射、默认值和筛选约定准备查询。

## 关键词研究流程

1. 确认用户要拓词、寻找长尾机会、筛选低竞争或高需求词，还是研究 PPC 出价；保留用户种子词原意。
2. 阅读 `references/api.md`，按目标市场映射、返回数量、排序和筛选条件构造一次查询；常见组合见“使用示例”。
3. 先说明动态算力消耗，结合用户已授权范围确定是否继续；优先复用同一参数组合的已有结果，避免重复付费。
4. 执行查询并保存完整数据，先查看摘要，再按需从文件提取指标；遵守接口定义中的调用限制。
5. 用表格展示关键词与指标，再说明需求、趋势和竞争方面的发现；查询失败时根据实际错误说明原因，给出参数调整建议。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python scripts/junglescout_keyword_by_keyword.py '<JSON 参数>' [--inline]`。
- **成本约束**：本工具按实际查询页数计费，具体公式见“算力消耗预估”。同一会话、同一参数组合默认只调用一次，脚本提供 24 小时本地缓存。失败或空结果时，不得自动更换关键词、翻页或修改邮编连续试探；需要继续检索时，先向用户说明额外消耗。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-junglescout-keyword-by-keyword-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
- 添加 `--inline` 可强制全量打印到标准输出，同时仍保存文件。

先通过摘要判断数据是否足够。需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

### 算力消耗预估

按动态规则计费：消耗算力 = 实际查询页数 × 63.75。

本服务按倍数动态计算，单次可能消耗大量算力，必须提醒用户，由用户决定是否继续。

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

用户会因算力消耗而支付费用。需要高频调用或用户对消耗量预期不足时，提醒用户，并由用户决定是否继续。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- 响应状态码为 `401` 或 `402`。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

### 约束与建议

- **研究概念**：关键词拓展用于扩充 Listing 词库；长尾词用于寻找更具体的需求。竞争判断结合 `easeOfRankingScore` 和 `organicProductCount`，PPC 研究结合精确、广泛和品牌广告建议出价，趋势研究结合月度和季度变化。
- **表格优先**：核心展示列为关键词、精确搜索量、广泛搜索量、月度趋势、PPC 精确出价和排名难度。PPC 研究侧重出价列，拓词侧重搜索量和趋势，按用户目的裁剪。
- **趋势标注**：月度和季度趋势为正值时标注上升 ↑，负值标注下降 ↓；不将月均估算口径解释为实时搜索数据，数据范围见接口定义。
- **难度解读**：`easeOfRankingScore` 越高越容易排名，1–3 为困难、4–6 为中等、7–10 为容易；避免将容易度高误读为竞争更激烈。
- **补充洞察**：表格后简述高搜索量词的主类目分布、长尾词竞争优势和增长词，依据实际返回指标形成结论。
- **错误和空结果**：按 `references/api.md` 解释返回情况，保留原始错误信息；不凭空补造关键词或未返回指标。

## 使用示例

### 扩展种子关键词 — 获取相关关键词列表

```json
{
  "marketplace": "us",
  "searchTerms": "yoga mat"
}
```

### 挖掘长尾关键词（3+ 词）

```json
{
  "marketplace": "us",
  "searchTerms": "yoga mat",
  "minWordCount": 3,
  "needCount": 50
}
```

### 低竞争关键词发现

```json
{
  "marketplace": "us",
  "searchTerms": "yoga mat",
  "maxOrganicProductCount": 200,
  "minMonthlySearchVolumeExact": 1000,
  "sort": "-ease_of_ranking_score"
}
```

### 高搜索量关键词筛选

```json
{
  "marketplace": "us",
  "searchTerms": "yoga mat",
  "minMonthlySearchVolumeExact": 10000,
  "sort": "-monthly_search_volume_exact",
  "needCount": 30
}
```

### PPC 竞价研究 — 按广泛出价排序

```json
{
  "marketplace": "us",
  "searchTerms": "yoga mat",
  "minMonthlySearchVolumeExact": 500,
  "sort": "ppc_bid_broad",
  "needCount": 30
}
```

### 德国站广泛搜索量关键词

```json
{
  "marketplace": "de",
  "searchTerms": "yogamatte",
  "minMonthlySearchVolumeBroad": 5000,
  "sort": "-monthly_search_volume_broad"
}
```

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。