---
name: linkfox-wb-google-tools
display_name: LinkFox Google工具集
display_name_en: LinkFox Google Tools
description: Google趋势、AI搜索与公开专利检索的一体化工具，帮助发现搜索需求、提炼实时网页信息并完成专利初筛。
description_zh: 面向 WorkBuddy 的 Google 数据研究工具，支持目标市场的历史关键词热度、近期热门搜索、带引用的 AI 网页信息摘要，以及 Google Patents 公开专利发现与筛选。适用于跨境市场调研、趋势判断、消费者偏好研究、长尾方向探索和专利初筛；详细参数、响应字段和 MCP 示例见 references/。
description_en: Google research tools for WorkBuddy covering historical keyword interest, recent trending searches, citation-backed AI web summaries, and Google Patents discovery with filters and pagination. Use for cross-border market research, trend validation, consumer-preference research, long-tail exploration, and preliminary patent screening; detailed parameters, response fields, and MCP examples are in references/.
icon: icons/logo.png
version: 2.1.0
author: Linkfox
---

> [!IMPORTANT]
本 Skill 必须依赖 MCP “LinkFox”。如未安装该MCP，请明确通知用户：
> 请先安装 LinkFox 连接器：
> - 在 WorkBuddy 左侧找到 “专家·技能·连接器” → “连接器”；
> - 搜索关键词 “LinkFox”，并安装连接器 “LinkFox”（注意：是 linkfox，不是 linkfox-product-selection），按指引完成登录授权；
> - 返回 WorkBuddy 重试。


# LinkFox Google工具集（LinkFox Google Tools）

帮助 WorkBuddy 判断 Google 搜索需求变化、发现目标地区近期热搜、提炼实时网页信息并检索公开专利。当前覆盖 4 个子能力，均通过 `LinkFox` 的 `proxy_call` 调用。

## 能力边界

### 能力范围

- **历史关键词热度**：调用 `proxy_call`，`toolName` 为 `googleTrend/getTrendByKeys`，按关键词、国家/地区和自定义日期范围获取 0–100 归一化搜索兴趣。适合季节性、年度变化和区域兴趣判断。
- **近期热门搜索发现**：调用 `proxy_call`，`toolName` 为 `googleTrend/getTrendByTime`，按 `days` 和 `region` 获取近期热门查询、相对搜索量、涨幅及观察时间窗。适合实时热点和短期爆发扫描。
- **AI 网页信息研究**：调用 `proxy_call`，`toolName` 为 `aiMode/googleSearch`，对单个自然语言问题获取 Google AI Mode 的 Markdown 概览、引用链接、任务信息和结果数量。
- **公开专利发现**：调用 `proxy_call`，`toolName` 为 `googlePatent/search`，按关键词、高级语法、国家、日期、状态、发明人、受让人和分页条件获取 Google Patents 的著录结果及链接。
- **可审计调用**：记录精确 `toolName`、原始业务参数、调用时间和返回的错误层级、`costToken`、分页或任务标识；不要假定 MCP 端提供缓存或本地落盘。

### 边界与限制

- Google Trends 历史热度是选定范围内的 0–100 相对值，不是绝对搜索量；`getTrendByKeys` 每次调用一个关键词，多关键词比较需要分别调用并承担额外消耗。历史数据从 2004 年起，冷门词可能数据稀疏。
- 近期热门搜索由 `days` 控制，面向短期趋势，不替代月度/年度历史分析；仅支持 US、GB、JP、CA、MX、DE、FR、IT、ES、NL、AU、SG、AE、BR、IN、TR、PL、SE 这 18 个地区。
- AI 搜索每次只处理一个 `keyword`，不支持同一请求内的多轮追问；追问必须总结上一轮结果和引用后发起新的调用。AI Overview 可能不触发，`resultsNum=0` 时不能把空结果解释为没有相关网页。语言和措辞会影响 Google 的地区偏向，接口没有显式地区参数。
- Google Patents 只返回发现阶段的专利/Scholar 著录列表，不提供已知专利号的完整全文、法律状态、专利族或图片详情；不能替代法律意见、FTO 结论或律师审查。`q` 必填且最多 1000 字符，`num` 只能为 10–100。
- 不处理 Google Ads 竞价/CPC、Amazon 或其他平台关键词、社交媒体趋势、SEO 排名、网站流量、广告投放、专利申请办理或诉讼策略。
- WorkBuddy 自动注入授权，不要求或接收用户提供 API Key、token 或认证 headers。401/402、余额不足、套餐权限和业务参数错误应按认证章节处理。失败、空结果和分页不得自动改词、改参数或连续重试；继续调用前先向用户说明可能产生额外积分消耗。

## 工具选择指南

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| “这个词过去一年是上升还是下降？”“看季节性/区域热度” | `linkfox-google-trend-get-trend-by-keys`，传 `keyword`、`region`、`dayRangeStart`、`dayRangeEnd` | 只关心最近 1–7 天的热搜榜用 `linkfox-google-trend-get-trend-by-time`；需要绝对搜索量或广告指标时不适用 |
| “最近美国有什么热搜？”“找本周正在爆发的话题” | `linkfox-google-trend-get-trend-by-time`，传 `days` 和 `region` | 需要固定关键词的长期曲线用 `linkfox-google-trend-get-trend-by-keys`；需要解释网页观点而非热搜列表用 `linkfox-ai-mode-google-search` |
| “用 Google AI 总结网上对 XX 的看法/痛点/偏好” | `linkfox-ai-mode-google-search`，将完整自然语言问题放入单个 `keyword` | 需要可比较的结构化趋势值用 Trends；只要原始网页或搜索结果而非 AI 综合时不适用 |
| “检索 XX 的专利”“查美国授权/某受让人的专利” | `linkfox-google-patent-search`，用 `q` 配合 `country`、`status`、日期或 `assignee` | 已有专利号并要全文、法律状态、家族或图像详情时应转到专门的专利详情能力，不应反复检索列表 |
| “同时看热度、近期热点和网页观点” | 先按问题选择所需层次；每个不同端点单独调用并分别标注来源 | 不要为了填充报告自动调用全部端点；积分和数据形态不同，应让用户决定是否继续扩大范围 |

选择时先判断用户要的是**历史相对曲线**、**近期热搜列表**、**网页观点综合**还是**专利候选列表**，再检查入参是否满足该端点的必填字段和范围。相近需求优先使用默认推荐；若切换工具会改变数据含义、成本或输出结构，应先说明差异并由用户决定。

## 业务需求路由速查

| 子能力 | 业务能力 | reference | `toolName` |
|---|---|---|---|
| `linkfox-google-trend-get-trend-by-keys` | 指定关键词的历史搜索兴趣、区域与时间范围趋势 | `references/linkfox-google-trend-get-trend-by-keys.md` | `googleTrend/getTrendByKeys` |
| `linkfox-google-trend-get-trend-by-time` | 指定地区和近期天数的热门搜索与涨幅 | `references/linkfox-google-trend-get-trend-by-time.md` | `googleTrend/getTrendByTime` |
| `linkfox-ai-mode-google-search` | 单问题 Google AI Mode 网页概览与引用 | `references/linkfox-ai-mode-google-search.md` | `aiMode/googleSearch` |
| `linkfox-google-patent-search` | Google Patents 公开专利关键词/条件检索与分页 | `references/linkfox-google-patent-search.md` | `googlePatent/search` |

## 调用方式

- 固定 MCP Server：`LinkFox`，URL：`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`，只调用 `proxy_call`。
- 外层参数固定为 `{"toolName":"<精确值>","arguments":{...}}`。`arguments` 直接放原接口请求体，不增加 `body`、`data` 或 `params` 包装。
- `toolName` 必须精确使用上表值，区分大小写且不得带前导 `/`。不得调用未在上表列出的 endpoint。
- WorkBuddy 自动注入授权。调用参数中禁止添加 `headers`、`Authorization`、API Key、token 或任何认证字段，也不要向用户索取这些信息。
- 禁止用 `curl`、`urllib`、`requests`、`httpx` 等直连旧工具网关；MCP 失败时不得降级到 HTTP 网关。
- `proxy_call` 的 `text` 结果若是 JSON 字符串，只解析一次。先判断 MCP/代理层错误，再判断下游业务响应中的 HTTP 状态、`errcode`、`code`、`errmsg` 或 `msg`。
- 单次失败、空结果和分页都不自动重试、改词、改参或翻页；再次调用可能重复扣费，须先说明原因并征得用户同意。
- AI 返回的 `sourceUrl`、引用链接，以及专利返回的 Google Patents、Scholar、PDF、缩略图和来源域名 URL，都是下游公开结果数据。只有用户要求核验来源时才访问，不能把这些 URL 当成 MCP server、工具网关或 `toolName`。
- Feedback API 是独立的公开反馈通道，不通过 `proxy_call`，也不是业务 endpoint。完整参数、响应字段和 MCP 示例见各 reference；授权异常见 `references/onboarding.md`。

## 使用示例

### 1. 历史关键词热度

```json
{
  "toolName": "googleTrend/getTrendByKeys",
  "arguments": {
    "keyword": "wireless charger",
    "region": "US",
    "dayRangeStart": "2024-01-01",
    "dayRangeEnd": "2025-12-31"
  }
}
```

调用 `LinkFox.proxy_call`。读取 `trendInfoForKeys[].trendValues[]` 的 `timeRange` 与 0–100 `value`，说明峰值、低谷和变化；若有 `chartOption`，说明其 X/Y 字段和曲线形态。关键词必须使用目标地区语言，单词长度最多 100 字符；相对值不能写成实际搜索量。

### 2. 近期热门搜索

```json
{
  "toolName": "googleTrend/getTrendByTime",
  "arguments": {
    "days": 7,
    "region": "DE"
  }
}
```

调用 `LinkFox.proxy_call`。读取 `trendValues[]` 的 `query`、`searchVolume`、`increasePercentage`、`startTime`、`endTime`，并明确“德国、最近 7 天”的时间窗；高涨幅项目可作为爆发话题标记。`searchVolume` 是相对值，不能与绝对流量混同，地区必须是支持列表中的代码。

### 3. Google AI 网页研究

```json
{
  "toolName": "aiMode/googleSearch",
  "arguments": {
    "keyword": "What are the unsolved pain points of open-ear headphones for US consumers in 2026?"
  }
}
```

调用 `LinkFox.proxy_call`。成功时直接保留 `stdout` Markdown 和其中的引用链接，并结合 `sourceUrl`、`resultsNum`、`costTime`、`costToken` 说明结果；`resultsNum=0` 时报告没有触发 AI Overview，不得虚构摘要。追问要把上一轮关键事实和引用先总结，再把新问题放进新的 `keyword`，每次都是新的计费调用。

### 4. Google Patents 专利发现

```json
{
  "toolName": "googlePatent/search",
  "arguments": {
    "q": "wireless earbuds",
    "country": "US",
    "status": "GRANT",
    "after": "publication:20240101",
    "sort": "new",
    "num": 20,
    "page": 1
  }
}
```

调用 `LinkFox.proxy_call`。以 `organicResults[]` 展示公开号、标题、发明人、受让人、公开/授权日期、`patentLink` 和 `pdf`，同时报告 `searchInformation.total_results`、当前页和总页数。`q` 支持 `owner:"Company"`、`inventor:"Name"`、`before:publication:YYYYMMDD` 等语法；`num` 必须为 10–100。结果只是候选专利清单，不构成侵权或 FTO 法律结论。

## 展示规则

1. **按数据形态展示**：历史趋势和近期热搜用表格或曲线摘要；Google AI 搜索直接保留返回的 Markdown 层级；Google Patents 用专利清单表格，避免把非结构化 AI 文本当作结构化数据处理。
2. **标注范围与来源**：每次输出注明端点/子能力标识、地区、关键词、日期或天数、调用时间和数据来源；趋势结果说明 0–100 是选定范围内的归一化值，近期热搜说明 `searchVolume` 和涨幅为相对指标。
3. **解释趋势特征**：历史数据指出峰值、低谷、季节性、持续增长或下降；近期数据突出明显高涨幅并写出 `startTime`/`endTime`；存在 `chartOption` 时说明标题、坐标字段和数据点可用于可视化。
4. **保留 AI 证据**：展示 AI 搜索时保留 `stdout` 中的引用链接和 `sourceUrl`，说明结果来自调用时的 Google AI Mode；`resultsNum=0` 明确提示未触发概览，不能用空结果推出事实结论。
5. **展示专利分页与链接**：专利结果显示总命中数、当前页范围和实际返回条数；日期格式化为易读日期；同时提供 `patentLink`、`pdf`。`scholar=true` 时将 Scholar 文章与专利明显区分。
6. **只展示真实字段**：不编造标题、日期、受让人、趋势值或引用；缺失字段标注 N/A 或省略。对 `0`、`-1` 等明确表示不可用的值，不当作真实业务数值。
7. **错误可操作化**：业务错误显示 `errcode`/`code` 与 `errmsg`/`msg`，并给出针对性修正：关键词语言或日期、地区代码、专利 `q`/`num`/日期格式；400 修参数，401/402 走认证章节，501 说明未开通专利权限或套餐配额耗尽且不要盲目重试。
8. **控制风险与成本**：空结果、失败和分页不自动变更参数；连续调用前提醒可能产生额外积分消耗。专利和趋势分析仅呈现数据与检索线索，不能表述为法律意见、侵权认定或绝对市场规模。

## 认证与积分异常

WorkBuddy 自动处理 MCP 授权，禁止要求用户提供 API Key、token 或认证 headers。遇到异常时先区分错误层级，完整规则见 `references/onboarding.md`。

- **MCP 工具不可用或未连接**：提示用户在 WorkBuddy 检查 `LinkFox` 连接状态；不要改走旧 HTTP 网关。
- **MCP/代理层 401 或 403**：提示用户在 WorkBuddy 重新连接或重新授权 MCP；不要把密钥写进参数。
- **下游业务 401/402**：原样报告状态与消息；402 或积分不足时引导用户访问 `https://agent.linkfox.com/` 检查套餐或积分。不要自动重试、购买或支付。
- **下游业务 403**：按业务 reference 的实际错误处理，不归类为 401 或 402。
- **Google Patents 501**：来源说明为 API 未开通或套餐配额耗尽；不要误报为登录失败，也不要盲目重试。

## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
