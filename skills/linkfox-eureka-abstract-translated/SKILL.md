---
name: linkfox-eureka-abstract-translated
description: 通过Eureka专利数据平台获取专利标题和摘要的翻译版本。当用户要求专利摘要翻译、专利标题翻译、翻译后的专利摘要、其他语言的专利内容、中文/英文/日文的专利摘要，或需要通过专利ID或公开号查询特定专利的摘要、标题、Eureka专利摘要、patent abstract translation, patent title translation, Eureka patent, patent translation, abstract lookup时触发此技能。当用户提到Eureka或专利摘要查询时也应触发，即使未明确说"翻译"。
---

# Eureka Patent Abstract Translation

This skill guides you on how to retrieve translated patent titles and abstracts from the Eureka patent data platform, supporting Chinese, English, and Japanese translations.

## Core Concepts

Eureka is a professional patent data platform. This tool queries its database to return translated titles and abstracts for one or more patents. You can look up patents by **patent ID** or **publication (announcement) number**, and receive translations in Chinese, English, or Japanese.

**Patent identification**: Each patent can be identified by either a `patentId` (internal identifier) or a `patentNumber` (public publication/announcement number such as `US20200012345A1` or `CN112345678A`). If both are provided, the patent ID takes priority.

**Family patent fallback**: When the original patent has no abstract available, you can optionally substitute the abstract from a related family patent by setting `replaceByRelated` to `1`.

## Parameter Guide

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| patentId | string | At least one of patentId or patentNumber | Internal patent ID. Separate multiple IDs with commas. Up to 100 patents per request. |
| patentNumber | string | At least one of patentId or patentNumber | Publication (announcement) number. Separate multiple numbers with commas. Up to 100 patents per request. |
| replaceByRelated | integer | No | Whether to substitute a family patent abstract when the original is unavailable. `1` = yes, `0` = no. Default `0`. |
| lang | string | No | Target translation language. `en` = English (default), `cn` = Chinese, `jp` = Japanese. |

### Key Rules

1. **At least one identifier is required**: You must provide either `patentId` or `patentNumber` (or both). If both are supplied, `patentId` takes priority.
2. **Batch queries**: Multiple patents can be queried at once by separating values with commas, up to 100 per request.
3. **Default language is English**: When the user does not specify a language, use `en`.
4. **Family fallback**: Set `replaceByRelated` to `1` only when the user explicitly wants a substitute abstract from a family patent if the original is missing.

## Response Fields

| Field | Description |
|-------|-------------|
| total | Number of patent records returned |
| data | Array of patent objects (see below) |
| data[].patentId | Internal patent ID |
| data[].pn | Publication (announcement) number |
| data[].title | Translated patent title |
| data[].abstractText | Translated patent abstract |
| data[].pnRelated | Publication number of the substitute family patent (only present when family replacement was used) |
| costToken | Tokens consumed by this request |

## Usage Examples

**1. Translate a single patent abstract to English by publication number**
```
Look up patent number US20200012345A1 and give me the English abstract.
```
Parameters: `patentNumber = "US20200012345A1"`, `lang = "en"`

**2. Translate multiple patents to Chinese**
```
Get the Chinese translation of abstracts for patents CN112345678A and US20200067890A1.
```
Parameters: `patentNumber = "CN112345678A,US20200067890A1"`, `lang = "cn"`

**3. Look up by patent ID with family fallback**
```
Get the Japanese abstract for patent ID 12345678. If the abstract is unavailable, use a family patent instead.
```
Parameters: `patentId = "12345678"`, `lang = "jp"`, `replaceByRelated = 1`

**4. Batch query by patent IDs**
```
Translate the titles and abstracts for these patent IDs: 111111, 222222, 333333.
```
Parameters: `patentId = "111111,222222,333333"`, `lang = "en"`

**5. Translate to Chinese with family patent fallback enabled**
```
查询专利CN112345678A的中文摘要，如果没有就用同族专利替代。
```
Parameters: `patentNumber = "CN112345678A"`, `lang = "cn"`, `replaceByRelated = 1`

## Display Rules

1. **Present data clearly**: Show results in a well-structured table with patent number, title, and abstract.
2. **Indicate language**: Mention the translation language in the output header so users know which language the results are in.
3. **Family patent notice**: If `pnRelated` is present in any result, explicitly inform the user that the abstract was sourced from a family patent and show the substitute publication number.
4. **Long abstracts**: For very long abstracts, display the full text without truncation so users can review the complete content.
5. **Error handling**: When a query fails or returns no results, explain the likely cause (e.g., invalid patent number, patent not found in database) and suggest corrections.

## 调用方式

- **API 端点**：`POST /tool-eureka/abstractDataTranslated`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/eureka_abstract_translated.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-eureka-abstract-translated-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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

## Important Limitations

- **Identifier required**: At least one of patent ID or publication number must be provided; the tool cannot perform keyword-based searches.
- **Translation languages**: Only Chinese (`cn`), English (`en`), and Japanese (`jp`) are supported.
- **No full-text retrieval**: This tool returns only titles and abstracts, not full patent claims or descriptions.
- **Family replacement is optional**: The substitute family patent abstract is only provided when explicitly requested via `replaceByRelated = 1`.
- **Batch limit**: A maximum of 100 patents per request.

## User Expression & Scenario Quick Reference

**Applicable** -- Patent abstract and title translation queries:

| User Says | Scenario |
|-----------|----------|
| "Translate this patent abstract" | Single patent translation |
| "What does patent XX say / what is it about" | Abstract lookup |
| "Get the Chinese/Japanese version of this patent" | Specific language translation |
| "Look up the abstract for patent number XX" | Publication number lookup |
| "Translate these patents in batch" | Batch translation |
| "The abstract is missing, try a family patent" | Family patent fallback |

**Not applicable** -- Needs beyond abstract translation:

- Full patent text, claims, or description retrieval
- Patent search by keyword, classification, or applicant
- Patent legal status, citation analysis, or landscape reports
- Patent valuation or infringement analysis

**Boundary** -- Edge cases:

- If the user asks for "patent content" without specifying which part, default to abstract translation and inform them about claim/description tools.
- If the user provides more than 100 patents, split into multiple batches.

## 积分消耗规则

按动态规则计费：消耗积分 = 81 × max(返回条数, 1)。

> **重要**：本技能的服务按倍数动态计算，可能一次性消耗大量积分，必须提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
