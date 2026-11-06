---
name: linkfox-sorftime-walmart-category-market
description: 使用 Sorftime 数据研究 Walmart 美国站类目，支持查看完整类目树、按自然语言类目名称匹配相关类目，以及查询已知类目路径的市场数据和 Best Seller 商品。适用于类目节点定位、层级核对、类目市场和热销商品研究；不适用于单品详情、商品趋势或销量深查、关键词指标及收藏关键词管理。
---
# Walmart 类目市场研究

## 适用范围

### 适用

查看 Walmart 美国站类目层级、匹配类目名称，或研究指定类目的市场及返回的 Best Seller 商品。

**场景速查**

| 用户表达 | 查询场景 |
| -------- | -------- |
| 下载 Walmart 完整类目树 | 获取类目层级，按需提取节点。 |
| patio furniture 对应哪个类目 | 按自然语言匹配相关类目。 |
| 查这个类目路径的市场和热销商品 | 查询已知类目路径的市场报告。 |

### 边界

主要对象是 Walmart 商品 ID、单品趋势或销量时，使用商品分析能力；关键词指标与收藏关键词管理使用对应能力。

## 接口清单

三个操作共用端点，通过 `operation` 区分，不存在额外的转发 `path` 参数。

| 接口 | 端点 | 对应脚本 | 说明 |
|---|---|---|---|
| 完整类目树（`tree`） | POST `/sorftime/walmart/categoryMarket` → `operation=tree` | `scripts/sorftime_walmart_category_market.py` | 获取完整类目层级。 |
| 类目名称匹配（`searchByName`） | POST `/sorftime/walmart/categoryMarket` → `operation=searchByName` | `scripts/sorftime_walmart_category_market.py` | 查找自然语言名称相关的类目。 |
| 类目市场报告（`marketReport`） | POST `/sorftime/walmart/categoryMarket` → `operation=marketReport` | `scripts/sorftime_walmart_category_market.py` | 查询指定类目市场及 Best Seller 商品。 |

## 前置条件

先确认用户需要类目层级、名称匹配还是已知类目的市场研究。市场报告所需路径必须有用户提供或已有数据依据；具体参数与使用限制见 `references/api.md`。

## 查询流程

1. 根据用户意图选择一个操作：类目名称优先匹配，确需遍历完整层级时查询类目树，已有可信路径时查询市场报告。
2. 先查看已保存响应及缓存，已有数据足够时直接使用；需要请求时，按 `references/api.md` 准备参数，只执行用户任务已授权的操作，不自动串联操作。
3. 判断本次结果是否足够。失败、空结果或需要另一个操作时，说明额外消耗；没有用户授权不得重试或继续请求。
4. 按下方展示规则解释结果，保留实际返回范围与缺失信息。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python scripts/sorftime_walmart_category_market.py '<JSON 参数>' [--inline] [--no-cache]`。
- **成本约束**：本工具按 Sorftime Request 动态计费，具体规则见“算力消耗预估”。同一会话、同一参数组合默认只调用一次，脚本提供 24 小时本地缓存。失败或空结果时，不得自动更换关键词、翻页或修改邮编连续试探；需要继续检索时，先向用户说明额外消耗。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-sorftime-walmart-category-market-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、HTTP 状态（`_http_status`）、操作与消耗字段（如 `requestConsumed`、`costToken`、`costCredit`）、常见计数、最大列表字段的长度和前 3 条样本。
- 添加 `--inline` 可强制全量打印到标准输出，同时仍保存文件。

先通过摘要判断数据是否足够。需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

### 算力消耗预估

按动态规则计费：单个 Sorftime Request 当前显示为 6 算力。多 Request 操作由网关按整单计算并取整，最终以入口脚本返回的 `costCredit` 为准，不能简单用 `requestConsumed × 6` 代替实际账单。各操作的上游 Request 消耗及无数据处理规则见 `references/api.md`。

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

用户会因算力消耗而支付费用。需要高频调用或用户对消耗量预期不足时，提醒用户，并由用户决定是否继续。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- HTTP 状态码为 `401` 或 `402`。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

### 约束与建议

- **类目概念**：类目树用于核对层级；名称匹配给出相关候选，不代表精确分类；市场报告用于研究已确认的类目。Sorftime 可能省略不适合第三方卖家的类目，未返回不代表 Walmart 没有该类目。
- **说明调用与费用**：展示本次操作及实际返回的 `requestConsumed`、`costCredit`、`costToken`。`_cache.hit=true` 时，明确费用值属于原始请求，本次缓存读取未产生新的生产扣费。
- **展示类目树**：只展示相关类目名称、ID 层级和有依据的派生路径，不将完整类目树贴入对话。类目树可能约 10 MB 或更大，优先从保存的 JSON 按需提取。
- **展示名称匹配**：仅展示实际返回的 `NodeId` 与 `CategoryName`，标为相关匹配；接口的结果数量限制见 `references/api.md`。
- **展示市场报告**：仅总结实际返回的指标，用紧凑表格展示 Best Seller 商品，注明实际商品条数，不把结果称为整个类目商品目录。
- **保留字段含义**：沿用上游字段、单位及嵌套编码，不补造缺失指标和类目关系。错误、空结果及费用头的解释见 `references/api.md`。

## 使用示例

### 查看完整类目层级

用户：我需要 Walmart 美国站的完整类目树。

选择类目树操作，保存完整响应，按用户关注的分支展示节点与层级。

### 从类目名称寻找相关节点

用户：帮我找 patio furniture 相关类目。

选择名称匹配操作，展示实际返回的相关类目及路径，不自动追加市场报告。

### 查看已知路径的类目市场

用户：查看路径 4044_623679_1032619_5842891_9823303 的市场和热销商品。

确认路径有据可查后，选择市场报告操作，展示返回的商品与指标、数量范围和实际费用。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
