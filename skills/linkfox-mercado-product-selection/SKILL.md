---
name: linkfox-mercado-product-selection
description: 查询和分析 Mercado Libre（美客多）的商品、官链、销量历史、关键词、类目趋势、店铺、评论、汇率与套餐用量，覆盖墨西哥、巴西、阿根廷、智利及部分哥伦比亚数据。适用于美客多选品筛选、竞品研究、热搜词与流量词分析、类目机会和市场趋势判断；不适用于店铺商品维护、订单履约或广告投放操作。
---

# 美客多商品选品与市场研究

## 适用范围

### 适用

从美客多商品、官链、关键词、类目、店铺或评论出发，查询真实数据并形成有依据的研究结论；也支持查询汇率和套餐用量。

**场景速查**

| 用户表达 | 查询场景 |
|------|------|
| 查这个美客多商品、商品详情或销量历史 | 商品详情、销量历史。 |
| 搜墨西哥站耳机、筛选商品 | 商品搜索与条件筛选。 |
| 查官链、catalog、目录链接 | 官链详情、销量历史或搜索。 |
| 关键词热搜、月度词、流量词反查 | 日度或月度热搜词、商品流量词。 |
| 类目趋势、新品机会、销量分布、品牌排行 | 类目定位、排行与趋势分析。 |
| 查店铺、seller | 店铺筛选及指定店铺商品研究。 |
| 查评论、reviews | 买家评论研究。 |
| 汇率、套餐用量 | 辅助信息查询。 |

## 接口清单

网关统一使用 POST `/mercado/productSelection`，按 `toolName` 选择操作。该契约没有单独的转发 path 参数，不构造其他 HTTP 端点。

| 接口 | 端点与操作标识 | 接口文档 | 对应脚本 | 说明 |
|------|------|------|------|------|
| 查询商品基本信息（`itemInfo`） | POST `/mercado/productSelection` → `toolName=itemInfo` | `references/api.md` | `scripts/linkfox_mercado_product_selection.py` | 根据站点和商品ID查询基本信息 |
| 查询商品销量历史（`itemHistory`） | POST `/mercado/productSelection` → `toolName=itemHistory` | `references/api.md` | `scripts/linkfox_mercado_product_selection.py` | 根据商品ID查询商品销量历史信息 |
| 商品搜索（`itemSearch`） | POST `/mercado/productSelection` → `toolName=itemSearch` | `references/api.md` | `scripts/linkfox_mercado_product_selection.py` | 商品搜索工具。支持按站点、关键词、类目、价格、销量（总销量/30天销量）、评分、评论数、重量及上架时间等多维度筛选商品，并支持排序。 |
| 查询官链基本信息（`catalogInfo`） | POST `/mercado/productSelection` → `toolName=catalogInfo` | `references/api.md` | `scripts/linkfox_mercado_product_selection.py` | 根据站点和官链（或目录链接）ID查询基本信息 |
| 查询官链销量历史（`catalogHistory`） | POST `/mercado/productSelection` → `toolName=catalogHistory` | `references/api.md` | `scripts/linkfox_mercado_product_selection.py` | 根据站点和官链（或目录链接）ID查询销量历史信息 |
| 官链搜索（`catalogSearch`） | POST `/mercado/productSelection` → `toolName=catalogSearch` | `references/api.md` | `scripts/linkfox_mercado_product_selection.py` | 官链（或目录链接）搜索工具，支持按站点、关键词、类目、价格、销量、评分、BSR排名等多维度筛选官链 |
| 按天搜索热搜词（`keywordDateSearch`） | POST `/mercado/productSelection` → `toolName=keywordDateSearch` | `references/api.md` | `scripts/linkfox_mercado_product_selection.py` | 根据站点和日期查询按天热搜词信息 |
| 月度热搜词（`keywordMonthSearch`） | POST `/mercado/productSelection` → `toolName=keywordMonthSearch` | `references/api.md` | `scripts/linkfox_mercado_product_selection.py` | 根据站点和月份查询月度热搜词信息 |
| 流量词反查（`keywordReverse`） | POST `/mercado/productSelection` → `toolName=keywordReverse` | `references/api.md` | `scripts/linkfox_mercado_product_selection.py` | 流量词反查 |
| 搜索类目（`categorySearch`） | POST `/mercado/productSelection` → `toolName=categorySearch` | `references/api.md` | `scripts/linkfox_mercado_product_selection.py` | 免费 （限时）：搜索类目信息，根据站点和类目名称(西文或葡文) |
| 搜索最小子类目（`categorySmallSearch`） | POST `/mercado/productSelection` → `toolName=categorySmallSearch` | `references/api.md` | `scripts/linkfox_mercado_product_selection.py` | 免费 （限时）：搜索最小类目信息，根据站点和类目名称(西文或葡文) |
| 热门品牌排行榜（`trendBrandTopBrand`） | POST `/mercado/productSelection` → `toolName=trendBrandTopBrand` | `references/mercado-tool-reference.md` | `scripts/linkfox_mercado_product_selection.py` | 查询指定类目下的热门品牌排行榜数据 |
| 热门商品排行榜（`trendBrandTopItem`） | POST `/mercado/productSelection` → `toolName=trendBrandTopItem` | `references/mercado-tool-reference.md` | `scripts/linkfox_mercado_product_selection.py` | 查询指定类目下的热门商品排行榜数据 |
| 热门店铺排行榜（`trendBrandTopSeller`） | POST `/mercado/productSelection` → `toolName=trendBrandTopSeller` | `references/mercado-tool-reference.md` | `scripts/linkfox_mercado_product_selection.py` | 查询指定类目下的热门店铺排行榜数据 |
| 新品机会分析（`trendNewItems`） | POST `/mercado/productSelection` → `toolName=trendNewItems` | `references/mercado-tool-reference.md` | `scripts/linkfox_mercado_product_selection.py` | 查询指定类目的新品机会数据，包括新品销量、占比等信息 |
| 价格分布趋势（`trendPrice`） | POST `/mercado/productSelection` → `toolName=trendPrice` | `references/mercado-tool-reference.md` | `scripts/linkfox_mercado_product_selection.py` | 查询指定类目的价格分布趋势数据 |
| 销量分布（`trendSale`） | POST `/mercado/productSelection` → `toolName=trendSale` | `references/mercado-tool-reference.md` | `scripts/linkfox_mercado_product_selection.py` | 查询指定类目的销量分布数据，支持按月查询 |
| 销售历史趋势（`trendSoldHis`） | POST `/mercado/productSelection` → `toolName=trendSoldHis` | `references/mercado-tool-reference.md` | `scripts/linkfox_mercado_product_selection.py` | 查询指定类目的销售历史趋势数据 |
| 类目汇总统计（`trendStatistical`） | POST `/mercado/productSelection` → `toolName=trendStatistical` | `references/mercado-tool-reference.md` | `scripts/linkfox_mercado_product_selection.py` | 查询指定类目的汇总统计数据，包括总商品数、销量、销售额等 |
| 仓储类型分布（`trendStoreInventoryType`） | POST `/mercado/productSelection` → `toolName=trendStoreInventoryType` | `references/mercado-tool-reference.md` | `scripts/linkfox_mercado_product_selection.py` | 查询指定类目的仓储类型分布数据，包括FBM、FULL、CBT等仓储类型的销售情况 |
| 店铺搜索（`sellerSearch`） | POST `/mercado/productSelection` → `toolName=sellerSearch` | `references/mercado-tool-reference.md` | `scripts/linkfox_mercado_product_selection.py` | 店铺搜索工具，支持按站点、店铺类型、店铺等级等条件筛选店铺 |
| 查询商品评论（`reviewSearch`） | POST `/mercado/productSelection` → `toolName=reviewSearch` | `references/mercado-tool-reference.md` | `scripts/linkfox_mercado_product_selection.py` | 按商品ID获取评论列表详情 |
| 汇率查询（`rateInfo`） | POST `/mercado/productSelection` → `toolName=rateInfo` | `references/mercado-tool-reference.md` | `scripts/linkfox_mercado_product_selection.py` | 免费接口 （限时）：美客多平台，按站点，查询对应国家币种汇率(美元)，及折算人民币汇率信息 |
| 查询套餐使用量（`myUsage`） | POST `/mercado/productSelection` → `toolName=myUsage` | `references/mercado-tool-reference.md` | `scripts/linkfox_mercado_product_selection.py` | 免费接口 （限时）：购买的套餐及使用量 |

## 前置条件

先确定用户的研究目标、站点及已有的商品、官链或类目信息。仅有类目名称时先定位类目；参数要求与各操作支持范围见接口清单中的文档。

## 查询流程

1. 根据用户意图，从接口清单选择所需操作；区分商品与官链、商品历史与类目趋势，避免扩大付费查询范围。
2. 用户只给类目名称时，先用类目查询定位（免费 （限时）），再使用返回的类目编号进行商品、官链或趋势研究。
3. 对宽泛调研，先用用户目标确定站点、类目、关键词、统计时间和筛选范围，再查询所需数据，避免没有明确目的的付费探索。
4. 先判断封装状态，再阅读业务结果；保留已取得数据，按实际返回解释空结果或异常。需要进一步检索时遵守成本约束。
5. 根据用户问题呈现可核验的数据和结论；大结果先看摘要，再从保存文件中抽取所需内容。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python scripts/linkfox_mercado_product_selection.py '<JSON 参数>' [--inline] [--no-cache]`。
- **成本约束**：收费操作每次消耗 12 算力。同一会话、同一参数组合默认只调用一次，脚本提供 24 小时本地缓存。失败或空结果时，不得自动更换关键词、翻页或修改邮编连续试探；需要继续检索时，先向用户说明额外消耗。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-mercado-product-selection-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
- 添加 `--inline` 可强制全量打印到标准输出，同时仍保存文件。

先通过摘要判断数据是否足够。需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

### 算力消耗预估

收费操作：12 算力 / 次。`categorySearch`、`categorySmallSearch`、`reviewSearch`、`rateInfo`、`myUsage` 免费 （限时），其余操作收费。后端 token 计量与算力不混用，以实际扣除为准。

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

用户会因算力消耗而支付费用。需要高频调用或用户对消耗量预期不足时，提醒用户，并由用户决定是否继续。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- HTTP 状态码为 `401` 或 `402`。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

### 约束与建议

- **区分研究对象**：商品使用 item 系列，官链或目录使用 catalog 系列，流量和热搜使用 keyword 系列，类目排行与趋势使用 trend 系列；店铺、评论及辅助查询按接口清单选择。
- **按返回结构读取**：先读 `data`，文本或含义不明确时结合 `contentText`；仅在用户要求原始诊断时查看 `rawResponse`。各操作的业务返回可能是文本，不强行套用统一表格结构。
- **保留数据含义**：展示结果时保留重要字段与原始含义，可翻译标签，但不编造响应不支持的经营结论。
- **说明返回范围**：大型数组和时间序列先说明可见数据范围，按需提取，不将局部结果当作全市场数据。
- **解释空结果**：上游返回“无数据”或业务失败提示时据实解释；只有封装层确有异常才按接口文档判为系统问题。
- **保护凭证与隐私**：不在用户输出中披露 LinkFox 密钥、上游凭证或完整敏感原始负载。
- **运行约定**：缓存、CLI、认证兼容及响应解析限制见 [主接口文档](references/api.md)；趋势与辅助查询的独立契约见 [补充接口文档](references/mercado-tool-reference.md)。

## 使用示例

### 按名称定位墨西哥类目

用户：查墨西哥站耳机类目，再看看这个类目的市场表现。

先用类目搜索确定目标类目（免费 （限时）），再按用户关心的销量、价格或品牌选择趋势数据；说明继续研究的消耗，避免连续试探。

### 查询商品与官链

用户：看看这个商品的基本信息和销量历史。

根据用户给出的商品或官链标识选择对应操作，展示实际返回的资料和历史区间，缺少的信息不补造。

### 月度热搜词或套餐用量

用户：查看巴西某月热搜词，或者查询我的套餐用量。

前者按用户指定月份选择月度关键词查询；后者使用套餐用量查询。完整请求示例见相应接口文档。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
