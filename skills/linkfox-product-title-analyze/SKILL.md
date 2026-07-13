---
name: linkfox-product-title-analyze
description: 对产品标题进行分词分析，提取词频、场景词、人群词、材质词等属性维度。当用户想分析产品标题、提取标题高频词、进行标题分词、发现场景词或人群词、对比不同商品的标题关键词用法、基于词频优化Listing标题、识别一组ASIN中的常见属性规律、title tokenization, word frequency analysis, scene keyword extraction, audience keyword analysis, title optimization, attribute keyword extraction, keyword frequency时触发此技能。即使用户未明确说"标题分析"，只要其需求涉及将产品标题拆解为有意义的词组、统计关键词频率或按提取的属性对商品分组，也应触发此技能。
---

# Product Title Analyzer

This skill guides you on how to tokenize and analyze product titles from previously queried products, helping Amazon sellers extract keyword patterns, scene words, audience words, and other attribute dimensions from product listing titles.

## Core Concepts

Product Title Analysis performs intelligent tokenization on product titles that have already been retrieved in the current conversation. It uses LLM-powered analysis to extract structured attributes (scene words, audience words, materials, colors, etc.) from free-text titles, then groups and counts them for pattern discovery.

**Automatic data aggregation**: The tool automatically collects products from all prior steps in the current conversation turn -- even across paginated queries. You do NOT need to manually pass product data unless you are referencing data from a previous conversation turn.

**One dimension per request**: Each call should analyze exactly ONE attribute dimension (e.g., scene words OR audience words). Do NOT request multiple dimensions in a single call.

## Data Fields

### Request Fields

| Field | API Name | Required | Description | Example |
|-------|----------|----------|-------------|---------|
| Analysis Request | tokenizationAndCountingRequest | Yes | Natural-language instruction describing which attribute dimension to extract from titles | "Count scene words in product titles" |
| Output Mode | outputMode | No | How multi-value attributes are returned. `MULTIPLE_RECORDS` (default): one record per value. `COMMA_SEPARATED`: all values in one record | MULTIPLE_RECORDS |
| Reference Data | refResultData | No | Externally supplied product data (only needed when referencing data from a previous conversation turn) | (JSON string) |

### Response Fields -- Product Attributes

| Field | API Name | Description | Example |
|-------|----------|-------------|---------|
| ASIN | asin | Product ASIN identifier | B0XXXXXXXX |
| Product Title | title | Original product title | Portable Camping Lantern... |
| Attribute Name | attributeName | Extracted attribute category | Scene Word |
| Attribute Value | attributeValue | Extracted attribute value | Outdoor / Camping |
| Price | price | Product price | 29.99 |
| Monthly Sales | monthlySalesUnits | Monthly unit sales | 1200 |
| Monthly Revenue | monthlySalesRevenue | Monthly sales revenue | 35988 |
| Rating | rating | Product rating | 4.5 |
| Rating Count | ratings | Number of ratings | 3820 |
| Available Date | availableDate | Listing date | 2024-03-15 |
| Brand | brand | Brand name | BrandX |
| Image URL | imageUrl | Main product image | https://... |

### Response Fields -- Attribute Groups

| Field | API Name | Description |
|-------|----------|-------------|
| Attribute Name | attributeName | The attribute category for this group (e.g., "Scene Word") |
| Attribute Value | attributeValue | A specific value within the group (e.g., "Outdoor") |
| Count | count | Number of products sharing this attribute value |
| ASIN List | asins | List of ASINs that share this attribute value |

### Response Metadata

| Field | API Name | Description |
|-------|----------|-------------|
| Render Type | type | UI rendering style |
| Columns | columns | Column definitions for table rendering |
| Source Type | sourceType | Data source type |
| Token Cost | costToken | Total LLM tokens consumed (input + output) |

## Parameter Guide

### tokenizationAndCountingRequest Examples

The `tokenizationAndCountingRequest` parameter is a natural-language instruction telling the tool which dimension to analyze. Keep it focused on a single dimension.

**Scene words (where / when the product is used)**
```
Count scene words appearing in product titles
```

**Audience / target-user words (who the product is for)**
```
Count audience words appearing in product titles
```

**Material words**
```
Count material-related words appearing in product titles
```

**Function / feature words**
```
Count function or feature words appearing in product titles
```

**Incorrect -- multiple dimensions in one request (do NOT do this)**
```
Count scene words AND audience words in product titles
```
Split this into two separate calls instead.

### outputMode

| Value | Behavior | When to Use |
|-------|----------|-------------|
| MULTIPLE_RECORDS | Each attribute value becomes its own record (default) | Most analysis -- easier to count, sort, and group |
| COMMA_SEPARATED | Multiple values stay in one record, comma-separated | When you want to see all attributes per ASIN at a glance |

## Display Rules

1. **Present data in tables**: Show extracted attributes and their frequencies in clear, sortable tables
2. **Highlight top keywords**: Call out the most frequent attribute values so patterns are immediately visible
3. **Group summary first**: When `attributeGroups` is returned, present the grouped summary before the per-product detail
4. **One dimension at a time**: If the user wants multiple dimensions analyzed, run separate calls and present results sequentially
5. **Token cost awareness**: The response includes `costToken`; do not display it unless the user asks about usage
6. **Error handling**: If the tool returns an error, explain the reason and suggest corrective action (e.g., "No products found in current conversation -- please query products first")
## Applicable Scenarios

| User Says | Scenario |
|-----------|----------|
| "What scene words appear in these titles?" | Scene-word extraction |
| "Analyze title keywords", "title word frequency" | General title tokenization |
| "What audience are these products targeting?" | Audience-word extraction |
| "Common materials in these listings" | Material-word extraction |
| "Help me optimize my title based on competitors" | Competitive title keyword analysis |
| "What words do top sellers use in titles?" | High-frequency keyword discovery |
| "Group these products by title attributes" | Attribute-based product grouping |

## Not Applicable Scenarios

- **No products queried yet**: The tool requires products to already exist in the conversation context. Prompt the user to search for products first.
- **Advertising / PPC keyword suggestions**: This tool analyzes existing titles, not ad keywords.
- **Full listing copywriting**: This tool extracts and counts words; it does not generate new titles.
- **Backend search term analysis**: This is for visible title analysis, not hidden search terms.
- **ABA search term data**: Use the ABA Data Explorer skill instead.

## 调用方式

- **API 端点**：`POST /product/titleAnalyze`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/title_analyze.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-product-title-analyze-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 解决认证和积分问题
发生以下异常情况时，采用以下措施来处理：

### 异常情况
- **未配置API Key**：环境变量未配置 `LINKFOX_AGENT_API_KEY`，也未配置 `LINKFOXAGENT_API_KEY`。
- **响应401或402状态码**
- **响应提示积分或余额不足**：消息含"积分余额不足/计费不足/余额不足/quota exceeded/insufficient balance/套餐到期/需充值/请充值"，或类似含义的内容。

### 措施
- 优先采用skill内的 onboarding.md 引导解决问题。
- 如找不到 onboarding.md 文件，则加载 /linkfox-onboarding 这个skill并根据它的引导来处理。如未安装请先安装：
    - 下载 https://agent-files.linkfox.com/skills/linkfox-onboarding/release.zip，解压后安装这个skill。如需用户授权才可下载，要询问用户获得授权，你不能自己放弃下载。
- 兜底措施：仅当前面两个措施经过所有努力都走不通时，才提示用户依据 https://skill.linkfox.com/linkfoxskills/guide.htm 指引获取API Key，或去 https://os.linkfox.com/ 补充积分。

## 积分消耗规则

按动态规则计费：消耗积分 = sum(所有被处理商品标题的(输入消耗的积分 + 输出结果消耗的积分))。

> **重要**：本技能的服务按倍数动态计算，可能一次性消耗大量积分，必须提醒用户，由用户决定是否继续。
