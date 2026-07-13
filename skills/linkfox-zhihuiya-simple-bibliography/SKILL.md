---
name: linkfox-zhihuiya-simple-bibliography
description: 从智慧芽专利数据库查询专利简要著录（书目）数据。当用户提到专利著录信息查询、专利基本信息获取、专利书目数据、专利公开详情、按专利号查询发明人、专利申请人信息、专利摘要获取、专利分类号（IPC/CPC）、专利引用查询或任何通过专利ID、公开号检索结构化元数据的请求、patent brief bibliography, patent basic info, patent number lookup, patent abstract, PatSnap, patent metadata时触发此技能。即使用户未明确提及"智慧芽"或"著录信息"，只要其需求涉及查询特定专利的核心著录字段，也应触发此技能。
---

# Zhihuiya Patent Simple Bibliography

This skill guides you on how to query simple bibliographic data for patents using the Zhihuiya patent database, helping users retrieve structured patent metadata efficiently.

## Core Concepts

The Zhihuiya Simple Bibliography tool retrieves basic bibliographic (front-page) information for patents. Given one or more patent IDs or publication numbers, it returns structured metadata including title, abstract, applicants, inventors, assignees, classification codes, filing dates, priority claims, and citation references.

**Lookup modes**: You can look up patents by either `patentId` (Zhihuiya internal patent ID) or `patentNumber` (public publication/grant number). If both are supplied, `patentId` takes priority. Multiple values are separated by commas, with a maximum of 100 per request.

## Parameter Guide

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| patentId | string | Conditionally | Zhihuiya internal patent ID. Comma-separated for multiple values, max 100. At least one of `patentId` or `patentNumber` must be provided. |
| patentNumber | string | Conditionally | Public publication/grant number (e.g., `US11234567B2`, `CN115000000A`). Comma-separated for multiple values, max 100. At least one of `patentId` or `patentNumber` must be provided. |

**Priority rule**: When both `patentId` and `patentNumber` are present, the API uses `patentId` and ignores `patentNumber`.

## Response Data Fields

| Field | API Name | Description |
|-------|----------|-------------|
| Patent ID | patentId | Zhihuiya internal patent identifier |
| Title | title | Patent title |
| Abstract | abstractContent | Patent abstract text |
| Publication Number | publicationNumber | Publication number |
| Publication/Grant Number | pn | Full publication/grant number |
| Country Code | country | Country code of the patent |
| Publication Country | publicationCountry | Country where the patent was published |
| Publication Date | publicationDate | Publication date |
| Publication Kind | publicationKind | Kind code of the publication |
| Patent Type | patentType | Type of patent (e.g., invention, utility model, design) |
| Kind Code | kind | Patent kind code |
| Application Number | applicationNo | Application number |
| Application Date | applicationDate | Application filing date |
| Applicants | applicants | List of applicants |
| Inventors | inventors | List of inventors |
| Assignees | assignees | List of patent assignees/owners |
| Assignee Addresses | assigneeAddresses | List of assignee addresses |
| IPC Main | ipcMain | Main IPC classification code |
| IPC Further | ipcFurther | Additional IPC classification codes |
| CPC Main | cpcMain | Main CPC classification code |
| CPC Further | cpcFurther | Additional CPC classification codes |
| LOC | loc | Locarno classification codes (design patents) |
| GBC | gbc | GBC classification codes |
| Priority Claims | priorityClaims | List of priority claim entries |
| PCT Application No | pctApplicationNo | PCT international application number |
| PCT Filing Date | pctFilingDate | PCT international filing date |
| PCT Entry Date | pctEntryDate | PCT national phase entry date |
| Cited Patents | citedPatents | List of cited patent references |
| Cited Non-Patents | citedNonPatents | List of cited non-patent literature |

## 调用方式

- **API 端点**：`POST /zhihuiya/simpleBibliography`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/zhihuiya_simple_bibliography.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-zhihuiya-simple-bibliography-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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

## Usage Examples

**1. Look up a single patent by publication number**
```
User: "Show me the bibliographic info for patent US11234567B2."
Action: Call with patentNumber = "US11234567B2"
```

**2. Look up multiple patents by publication number**
```
User: "Get the basic info for CN115000000A, EP4000000A1, and JP2023100000A."
Action: Call with patentNumber = "CN115000000A,EP4000000A1,JP2023100000A"
```

**3. Look up patents by Zhihuiya patent ID**
```
User: "Retrieve bibliography for patent IDs abc123 and def456."
Action: Call with patentId = "abc123,def456"
```

**4. Retrieve inventor and applicant information**
```
User: "Who are the inventors and applicants for patent US20230001234A1?"
Action: Call with patentNumber = "US20230001234A1", then extract the inventors and applicants fields from the response.
```

**5. Check patent classification codes**
```
User: "What IPC and CPC codes does patent EP3999999B1 have?"
Action: Call with patentNumber = "EP3999999B1", then present ipcMain, ipcFurther, cpcMain, and cpcFurther from the response.
```

**6. Get patent abstract and citation references**
```
User: "Show me the abstract and cited patents for CN114000000B."
Action: Call with patentNumber = "CN114000000B", then display abstractContent and citedPatents.
```

## Display Rules

1. **Present data clearly**: Show bibliographic results in well-structured tables or grouped sections. For a single patent, use a key-value layout. For multiple patents, use a table with the most relevant columns.
2. **Selective display**: When results contain many fields, prioritize showing title, publication number, applicants, inventors, application date, publication date, IPC/CPC main codes, and abstract. Show additional fields only when the user specifically asks.
3. **List fields**: For array fields (inventors, applicants, assignees, classification codes, citations), present them as comma-separated values or bulleted lists depending on length.
4. **Empty fields**: Omit fields that are null or empty from the display rather than showing blank entries.
5. **Error handling**: When a query fails, explain the reason based on the error message and suggest the user verify the patent number or ID format.
6. **Batch result notice**: When querying many patents at once, remind the user that the maximum is 100 per request.
## Important Limitations

- **Maximum batch size**: Up to 100 patent IDs or publication numbers per request.
- **At least one identifier required**: Either `patentId` or `patentNumber` must be provided; omitting both will cause an error.
- **patentId takes priority**: If both parameters are supplied, only `patentId` is used.
- **Data scope**: This tool returns simple bibliographic data only. It does not return full-text claims, detailed descriptions, legal status, or patent family information.

## User Expression & Scenario Quick Reference

**Applicable** -- Patent bibliographic data retrieval:

| User Says | Scenario |
|-----------|----------|
| "Look up patent XX" / "Get info for patent XX" | Single patent bibliography lookup |
| "Who invented patent XX" / "Who is the applicant" | Inventor / applicant retrieval |
| "What's the IPC code for XX" / "Classification of XX" | Classification code lookup |
| "Show me the abstract of XX" | Abstract retrieval |
| "When was patent XX filed" / "Publication date of XX" | Date information lookup |
| "What patents does XX cite" | Citation reference lookup |
| "Get bibliographic data for these patents: A, B, C" | Batch bibliography query |
| "Patent basic info" / "Patent front page data" | General bibliography retrieval |

**Not applicable** -- Needs beyond simple bibliographic data:

- Full-text patent claims or detailed description
- Patent legal status or prosecution history
- Patent family / equivalents analysis
- Patent valuation or landscaping
- Freedom-to-operate or infringement analysis
- Patent search by keyword or semantic query (this tool requires specific patent identifiers)

## 积分消耗规则

按动态规则计费：消耗积分 = 81 × 返回data条数。每条为 1 条简版专利著录项结果

> **重要**：本技能的服务按倍数动态计算，可能一次性消耗大量积分，必须提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
