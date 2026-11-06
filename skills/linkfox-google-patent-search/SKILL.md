---
name: linkfox-google-patent-search
description: 检索 Google Patents 公开专利数据库，按关键词、发明人、受让人、国家、日期及专利状态查找全球专利，返回公开号、标题、摘要、日期、CPC 分类和文献链接。适用于跨境商品上架前的专利风险初筛、自由实施（FTO）排查和现有技术检索；不适用于已知专利的全文、法律状态、专利族详情、以图查专利或智慧芽表达式检索。
---

# Google Patents 专利检索

## 适用范围

### 适用

在 Google Patents 公开文献中发现相关专利，或按著录条件缩小候选范围。用户希望“查专利”“专利防侵权排查”或检索现有技术时，无需明确提及 Google Patents。

**场景速查**

| 用户表达 | 查询场景 |
|----------|----------|
| 检索 wireless earbuds 相关专利 | 全文关键词检索。 |
| 查谷歌专利 / Google Patents 搜一下 | 公开专利发现。 |
| 查美国授权的 XX 专利 | 国家与专利状态筛选。 |
| 查 2024 年至今公开的 XX 专利 | 日期范围筛选与最新排序。 |
| 查受让人是 Apple 或某位发明人的专利 | 受让人或发明人检索。 |
| 翻到第 2 页 | 在已明确的查询条件下继续分页。 |

### 边界

已知专利号并需完整著录、全文、法律状态、专利族或图片时，按需求转交 `linkfox-zhihuiya-bibliography`、`linkfox-zhihuiya-legal-status`、`linkfox-zhihuiya-patent-family` 等专用技能。以图查专利使用 `linkfox-zhihuiya-patent-image-search`；智慧芽字段布尔表达式检索使用 `linkfox-zhihuiya-retrieval-patent-search`。

## 前置条件

确定检索主题和用户所需的筛选范围；调用前阅读 `references/api.md`，按其中的查询语法与参数约定准备请求。

## 检索流程

1. 从用户问题确定关键词、发明人或受让人等检索主题，并整理国家、状态、日期和排序需求。
2. 按 `references/api.md` 构造检索条件，复用同一参数组合的有效缓存，执行一次查询。
3. 根据接口参考判断响应，先查看摘要，再从保存的 JSON 中提取所需字段；按下方展示建议呈现候选专利。
4. 用户需要后续页或扩大检索范围时，先说明额外消耗；失败或空结果不得自动改写查询、换关键词或连续翻页试探，先与用户确认后续检索。
5. 需要深入某个候选专利时，使用返回的专利标识衔接专用技能，不重复用列表检索代替详情查询。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python scripts/google_patent_search.py '<JSON 参数>' [--inline]`。
- **成本约束**：本工具每次消耗 8 算力。同一会话、同一参数组合默认只调用一次，脚本提供 24 小时本地缓存。失败或空结果时，不得自动更换关键词、翻页或修改邮编连续试探；需要继续检索时，先向用户说明额外消耗。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-google-patent-search-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
- 添加 `--inline` 可强制全量打印到标准输出，同时仍保存文件。

先通过摘要判断数据是否足够。需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

### 算力消耗预估

8 算力 / 次

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

用户会因算力消耗而支付费用。需要高频调用或用户对消耗量预期不足时，提醒用户，并由用户决定是否继续。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- 响应状态码为 `401` 或 `402`。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

### 约束与建议

- **理解结果范围**：本技能提供按相关性或指定排序返回的文献列表及著录信息，可能包含 Google Scholar 学术文章；专利详情应由专用数据源获取。
- **表格展示**：优先展示公开号、标题、发明人、受让人、公开日期或授权日期，对应 `publicationNumber`、`title`、`inventor`、`assignee`、`publicationDate`、`grantDate`。
- **总量与分页**：依据实际返回的 `searchInformation` 或 `pagination` 展示总命中数和当前页范围；未返回的信息明确说明缺失，不推算或补造总量。
- **日期与链接**：将申请、公开、授权、优先权日期显示为可读日期，提供返回的 `patentLink` 和 `pdf` 链接。
- **区分文献类型**：明确区分学术文章与专利，不将 Scholar 字段混作专利著录信息。
- **大结果集**：先给摘要表和总量，再按用户需要展开特定专利；仅展示实际返回的字段，不编造标题、日期、受让人或其他信息。
- **进一步研究**：通过 `patentId` 或 `publicationNumber` 衔接边界章节所列的著录、法律状态或专利族技能。

## 使用示例

### 基础关键词检索

用户：在 Google Patents 检索 wireless earbuds 相关专利，返回 10 条。

```json
{"q": "wireless earbuds", "num": 10}
```

### 国家与状态筛选

用户：检索美国已授权的 wireless earbuds 专利。

```json
{"q": "wireless earbuds", "country": "US", "status": "GRANT"}
```

### 日期范围与最新排序

用户：检索 2024 年至今公开的 wireless earbuds 专利，按最新排序。

```json
{"q": "wireless earbuds", "after": "publication:20240101", "sort": "new"}
```

### 受让人检索

用户：检索受让人 Apple 的专利。

```json
{"q": "owner:\"Apple\"", "assignee": "Apple"}
```

### 继续分页

用户：继续检索 wireless earbuds，查看第 2 页，每页 20 条。

说明本次分页的额外消耗后，按用户意图执行：

```json
{"q": "wireless earbuds", "page": 2, "num": 20}
```

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。