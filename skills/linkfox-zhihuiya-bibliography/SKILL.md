---
name: linkfox-zhihuiya-bibliography
description: 通过专利ID或公开号查询智慧芽专利数据库中的专利著录（书目）信息。当用户提到专利著录信息查询、专利书目信息、专利申请人查询、专利发明人查询、专利分类号、专利摘要获取、专利引用分析、专利优先权主张、专利申请引用、专利审查员信息、patent bibliographic data, inventor lookup, applicant lookup, patent classification, patent metadata, PatSnap, patent citations时触发此技能。即使用户未明确提及"著录信息"，只要其需求涉及通过专利ID或公开号查询特定专利的详细元数据，也应触发此技能。
---

# Zhihuiya Patent Bibliography

This skill guides you on how to query patent bibliography (bibliographic) data from the Zhihuiya patent database, helping users retrieve detailed metadata for specific patents.

## Core Concepts

Patent bibliography data (also called bibliographic data) is the structured metadata associated with a patent document. It includes the patent title, applicants, inventors, classification codes, priority claims, cited references, abstracts, and more. This tool allows querying by **patent ID** or **publication number**, returning comprehensive bibliographic records for up to 100 patents per request.

**Patent types**: The `patentType` field indicates the type of patent document:
- `APPLICATION` -- Invention application (published but not yet granted)
- `PATENT` -- Granted invention patent
- `UTILITY` -- Utility model
- `DESIGN` -- Design patent

## Data Fields

| Field | API Name | Description |
|-------|----------|-------------|
| Patent ID | patentId | Internal patent identifier |
| Publication Number | pn | Publication/announcement number |
| Invention Title | inventionTitle | Patent title with language info |
| Abstracts | abstracts | Patent abstract text |
| Patent Type | patentType | APPLICATION, PATENT, UTILITY, or DESIGN |
| Applicants | applicants | Original applicant(s) |
| Assignees | assignees | Current patent holder(s) / assignee(s) |
| Inventors | inventors | Inventor(s) listed on the patent |
| Agents | agents | Patent attorney / agent(s) |
| Agency | agency | Filing agency / patent firm |
| Examiners | examiners | Patent examiner(s) |
| Priority Claims | priorityClaims | Priority right declarations |
| Application Reference | applicationReference | Application filing data |
| Publication Reference | publicationReference | Publication data |
| Dates of Public Availability | datesOfPublicAvailability | Public availability dates |
| IPC Classification | classificationIpcr | International Patent Classification |
| CPC Classification | classificationCpc | Cooperative Patent Classification |
| UPC Classification | classificationUpc | US Patent Classification |
| LOC Classification | classificationLoc | Locarno Classification (designs) |
| FI Classification | classificationFi | FI classification codes (Japan) |
| F-term Classification | classificationFterm | F-term codes (Japan) |
| GBC Classification | classificationGbc | GBC classification |
| Cited Patents | referenceCitedPatents | Patent documents cited as references |
| Cited Non-Patent Literature | referenceCitedOthers | Non-patent literature cited |
| Related Documents | relatedDocuments | Divisional / continuation application info |
| PCT Filing Data | pctOrRegionalFilingData | PCT or regional phase filing data |
| PCT Publishing Data | pctOrRegionalPublishingData | PCT or regional phase publication data |
| Estimated Expiry Date | exdt | Estimated patent expiration date (Zhihuiya) |

## 调用方式

- **API 端点**：`POST /zhihuiya/bibliography`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/zhihuiya_bibliography.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-zhihuiya-bibliography-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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

## Parameter Guide

The tool accepts two parameters. **At least one must be provided**; if both are supplied, `patentId` takes priority.

| Parameter | When to Use | Format |
|-----------|-------------|--------|
| `patentId` | When the user provides an internal Zhihuiya patent ID | Comma-separated string, up to 100 IDs |
| `patentNumber` | When the user provides a publication/announcement number | Comma-separated string, up to 100 numbers |

### Tips for Identifying Input Type

- If the user provides something like `US10123456B2`, `CN112345678A`, `EP3456789B1`, or `WO2023123456A1`, treat it as a **publication number** and use `patentNumber`.
- If the user provides a purely numeric or opaque identifier that does not match standard publication number patterns, treat it as a **patent ID** and use `patentId`.
- When the user provides multiple patents, join them with commas (no spaces around commas).

## Usage Examples

**1. Look up a single patent by publication number**
```
User: "Show me the bibliography for US10123456B2"
Action: Call with patentNumber = "US10123456B2"
```

**2. Look up multiple patents by publication number**
```
User: "Get bibliographic data for CN112345678A, EP3456789B1, and US20210012345A1"
Action: Call with patentNumber = "CN112345678A,EP3456789B1,US20210012345A1"
```

**3. Look up a patent by internal ID**
```
User: "Query bibliography for patent ID 8fa3b2c1-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
Action: Call with patentId = "8fa3b2c1-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

**4. Batch lookup of patents**
```
User: "I have a list of 20 publication numbers, look up all their inventors and assignees"
Action: Call with patentNumber = "<comma-separated list>"
Then extract and present inventors and assignees from the results.
```

## Display Rules

1. **Present data clearly**: Show query results in well-structured tables or organized sections. For each patent, highlight the most commonly needed fields: title, applicants/assignees, inventors, filing/publication dates, classification codes, and abstract.
2. **Respect the query scope**: Only display the fields the user asked about. If they asked for "inventors", do not dump the entire bibliography unless requested.
3. **Patent type labels**: Translate `patentType` codes into human-readable labels (APPLICATION = Invention Application, PATENT = Granted Invention, UTILITY = Utility Model, DESIGN = Design Patent).
4. **Multi-patent results**: When results contain multiple patents, use a summary table first, then expand details per patent if the user wants more.
5. **Error handling**: When a query returns an error or empty results, explain clearly and suggest the user verify their patent ID or publication number.
6. **No subjective analysis**: Present factual bibliographic data without speculative legal or commercial interpretations.
## User Expression & Scenario Quick Reference

**Applicable** -- Patent bibliography / metadata lookups:

| User Says | Scenario |
|-----------|----------|
| "Look up patent info for XX" | Single patent bibliography |
| "Who are the inventors of patent XX" | Inventor lookup |
| "Who owns patent XX", "current assignee" | Assignee / applicant query |
| "What IPC/CPC class is patent XX" | Classification lookup |
| "Show me the abstract of patent XX" | Abstract retrieval |
| "What patents does XX cite" | Citation analysis |
| "When does patent XX expire" | Expiry date query |
| "Get bibliography for these patents: A, B, C" | Batch lookup |
| "Patent details", "patent metadata" | General bibliography |

**Not applicable** -- Needs beyond patent bibliography:

- Full-text patent search by keyword or semantic query
- Patent landscape / analytics reports
- Patent valuation or legal status tracking
- Freedom-to-operate or infringement analysis
- Patent family tree exploration (unless specific publication numbers are given)

**Boundary judgment**: When users say "find patents about X" or "search for patents in field Y", that is a patent search task, not a bibliography lookup. This skill only applies when the user already has a patent ID or publication number and wants to retrieve its metadata.

## 积分消耗规则

按动态规则计费：消耗积分 = 81 × 返回data条数。每条为 1 条专利著录项结果

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
