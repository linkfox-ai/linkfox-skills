---
name: linkfox-sorftime-walmart-keyword-research
description: 研究 Walmart 美国站的当前热词、名称反查词、关键词指标、搜索结果商品、商品关联词及扩展词，并按用户要求查询、收藏、删除或移动收藏关键词。适用于 Walmart 关键词发现、需求与竞争指标研究、商品反查词及收藏词库管理；不适用于类目市场报告、单品详情或趋势分析，以及 Sorftime Walmart“其他”能力。
---
# Walmart 关键词研究

## 适用范围

### 适用

根据用户明确的研究目标选择一次关键词查询，或按明确指令管理 API 收藏词库。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 按搜索量和排名找 Walmart 热词 | 当前热词筛选。 |
| 根据商品或类目名称找热词 | 名称反查。 |
| 看关键词的指标或搜索结果商品 | 关键词详情或结果商品查询，按本次目标选一种。 |
| 查这个商品获得曝光的关键词 | 商品关联关键词。 |
| 找种子词的关联词 | 关联词拓展。 |
| 查看目录、收藏、删除或移动指定词 | 查询或维护收藏词库。 |

### 边界

类目市场报告、商品详情和商品趋势分析使用对应能力；Sorftime Walmart“其他”接口不在本技能范围。

## 接口清单

| 接口 | 端点 | 对应脚本 | 说明 |
|---|---|---|---|
| 筛选当前热词（`marketQuery`） | POST `/sorftime/walmart/keywordResearch`；`operation=marketQuery` | `scripts/sorftime_walmart_keyword_research.py` | 按关键词、排名或搜索量筛选热词。 |
| 名称反查热词（`searchByName`） | POST `/sorftime/walmart/keywordResearch`；`operation=searchByName` | `scripts/sorftime_walmart_keyword_research.py` | 从商品或类目名称查找热词。 |
| 热词搜索结果商品（`searchProducts`） | POST `/sorftime/walmart/keywordResearch`；`operation=searchProducts` | `scripts/sorftime_walmart_keyword_research.py` | 查看热词搜索结果中的商品。 |
| 关键词详情（`detail`） | POST `/sorftime/walmart/keywordResearch`；`operation=detail` | `scripts/sorftime_walmart_keyword_research.py` | 查看指定关键词的搜索与竞争指标。 |
| 商品关联关键词（`productKeywords`） | POST `/sorftime/walmart/keywordResearch`；`operation=productKeywords` | `scripts/sorftime_walmart_keyword_research.py` | 反查商品获得搜索曝光的关键词。 |
| 关联词拓展（`relatedKeywords`） | POST `/sorftime/walmart/keywordResearch`；`operation=relatedKeywords` | `scripts/sorftime_walmart_keyword_research.py` | 从种子关键词拓展相关词。 |
| 收藏关键词（`favoriteAdd`） | POST `/sorftime/walmart/keywordResearch`；`operation=favoriteAdd` | `scripts/sorftime_walmart_keyword_research.py` | 向指定目录收藏关键词。 |
| 删除或移动收藏关键词（`favoriteChange`） | POST `/sorftime/walmart/keywordResearch`；`operation=favoriteChange` | `scripts/sorftime_walmart_keyword_research.py` | 删除收藏词或移动到目标目录。 |
| 查询收藏词或目录（`favoriteList`） | POST `/sorftime/walmart/keywordResearch`；`operation=favoriteList` | `scripts/sorftime_walmart_keyword_research.py` | 查看最新收藏词或目录列表。 |

上述九个操作共用同一端点，通过 `operation` 区分，不存在独立的转发 `path`。完整定义见 `references/api.md`。

## 前置条件

先确认本次用户目标和查询对象。收藏变更会写入外部账户，必须已有明确、无歧义的用户请求；输入不足时先补齐目标信息。

## 执行流程

1. 根据用户本次意图选择一个操作；读取 `references/api.md` 中该操作的定义，核对对象、筛选或收藏目录。
2. 研究查询先复用有效缓存，没有缓存时仅发起本次操作；收藏新增、变更和列表按接口定义跳过缓存。不把关键词查询自动扩成多步骤研究链。
3. 收藏、删除或移动前核对用户已授权的目标和范围；`--no-cache` 不能替代用户授权。
4. 解释响应及本页结果，按接口定义核对写入结果。失败或空结果时停止，不自动换词、翻页或切换操作；需要继续时说明额外消耗并由用户决定。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python scripts/sorftime_walmart_keyword_research.py '<JSON 参数>' [--inline] [--no-cache]`。
- **成本约束**：本工具按动态规则计费，单个 Sorftime Request 当前显示为 6 算力，整单实际扣费见下方算力消耗预估。同一会话、同一参数组合默认只调用一次，脚本提供 24 小时本地缓存。失败或空结果时，不得自动更换关键词、翻页或修改邮编连续试探；需要继续检索时，先向用户说明额外消耗。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-sorftime-walmart-keyword-research-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应 JSON 序列化后的 UTF-8 大小不超过 8000 字节：保存后，将完整 JSON 打印到标准输出。
- 响应 JSON 序列化后的 UTF-8 大小超过 8000 字节：保存后，标准输出仅展示摘要，包括顶层字段、常见计数及费用字段（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
- 添加 `--inline` 可强制全量打印到标准输出，同时仍保存文件。

先通过摘要判断数据是否足够。需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

### 算力消耗预估

按动态规则计费：单个 Sorftime Request 当前显示为 6 算力；各操作的 Request 消耗见 `references/api.md`。网关按整单计算并取整，最终以返回的 `costCredit` 为准，不能用 `requestConsumed × 6` 代替实际账单。高消耗筛选、扩展词或连续分页前须提醒用户。

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

用户会因算力消耗而支付费用。需要高频调用或用户对消耗量预期不足时，提醒用户，并由用户决定是否继续。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- HTTP 状态码为 `401` 或 `402`。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

### 约束与建议

- **单次研究目标**：一次请求只执行一个操作；不同操作、页码或筛选是另一笔请求。接口入参和使用限制见 `references/api.md`。
- **收藏词库含义**：API 词库与 Sorftime 专业版收藏夹独立，数据不互通。当前操作不能删除目录，删除最后一个词后可能留下空目录；目录、分页及数量限制见接口定义。
- **缓存说明**：只读研究使用 24 小时本地缓存；收藏新增、变更和列表始终绕过缓存。实际命中时注明 `_cache.hit=true`，其中的费用对应生成缓存时的请求，本次缓存读取不发起新的网关请求。
- **HTTP 状态判断**：入口脚本在完整 JSON 的本地字段 `_http_status` 中保留实际 HTTP 状态，先按该状态再结合框架及业务结果判断；缓存内该字段属于原请求，旧缓存缺失时不推定为 HTTP 200。摘要未显示时从保存文件读取。
- **展示实际消耗**：注明本次操作，展示返回的 `requestConsumed`、`costCredit`、`costToken`；大响应摘要未显示的字段从已保存的 JSON 提取，字段缺失时不补造费用。
- **保留指标含义**：展示观察窗口及指标单位，不把预估搜索量、销量或销售额表述为保证需求。关键词与商品编号按字符串展示。
- **说明返回范围**：只展示已请求页；提出下一页时先说明会增加付费请求。
- **解释变更结果**：收藏操作须展示返回的业务结果码，不能只凭 HTTP 200 宣称成功。

## 使用示例

### 筛选热词

用户：找出包含 wireless 且搜索量较高的 Walmart 热词。

选择当前热词筛选，核对筛选含义与消耗后只查本次目标页，展示指标和返回范围。

### 关键词详情或商品关联词

用户：看看 wireless earbuds 的关键词指标。或：查商品 5169493923 的关联关键词。

分别选择关键词详情或商品关联词，按实际请求展示指标；不自动追加关联词拓展或商品搜索。

### 查看或变更收藏词库

用户：列出我的收藏目录。或：把 Headphones 里的 wireless earbuds 移到 Research。

前者读取最新目录；后者核对已明确的源目录、目标目录与关键词后执行变更，解释实际业务结果。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
