---
name: linkfox-zhihuiya-patent-forward-citation
description: 从智慧芽专利数据库查询专利的前向引用详情。当用户询问专利引用、被引用专利、引用文献、专利参考文献、前向引用、在先技术引用或想查看特定专利在申请过程中引用了哪些专利、非专利文献、patent cited references, forward citations, patent references, citation analysis, PatSnap时触发此技能。当用户提供专利ID或公开号并需要引用信息时，即使未明确说"前向引用"，任何关于专利引用了哪些参考文献的请求都适用。
---

# Zhihuiya Patent Forward Citation

This skill guides you on how to query patent forward citation data from the Zhihuiya patent database, helping users discover the patents and non-patent literature cited by specific patents during their application process.

## Core Concepts

**Forward citation** refers to the patents and non-patent literature that a given patent has cited in its application documents. This is a fundamental aspect of patent analysis — understanding what prior art a patent references helps assess its novelty, scope, and technological lineage.

- **Patent citations** (`citedPatents`): Other patents referenced by the queried patent.
- **Non-patent literature citations** (`citedOthers`): Academic papers, technical reports, and other non-patent documents referenced by the queried patent.

## Parameter Guide

You must provide at least one of the following two parameters. If both are provided, `patentId` takes priority.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| patentId | string | Conditionally | Patent ID(s). Multiple values separated by commas. Maximum 100 entries. |
| patentNumber | string | Conditionally | Publication/announcement number(s). Multiple values separated by commas. Maximum 100 entries. |

**Rules**:
1. At least one of `patentId` or `patentNumber` must be provided.
2. If both are present, `patentId` is used preferentially.
3. Multiple values are separated by commas (English commas).
4. Each parameter supports up to 100 entries per request.

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Total number of records returned |
| data | array | List of patent citation results |
| data[].patentId | string | Patent ID of the queried patent |
| data[].pn | string | Publication/announcement number |
| data[].citedPatents | array | List of cited patent documents |
| data[].citedOthers | array | List of cited non-patent literature |
| columns | array | Column definitions for rendering |
| costToken | integer | Tokens consumed by the query |
| type | string | Rendering style hint |

## 调用方式

- **API 端点**：`POST /zhihuiya/patentForwardCitation`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/zhihuiya_cited_references.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-zhihuiya-patent-forward-citation-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。
## Usage Examples

**1. Query forward citations by publication number**
```
Look up the forward citations for patent US10000000B2.
```
Parameters: `{"patentNumber": "US10000000B2"}`

**2. Query forward citations for multiple patents**
```
Find all citations for patents US10000000B2, US9876543B1, and EP3456789A1.
```
Parameters: `{"patentNumber": "US10000000B2,US9876543B1,EP3456789A1"}`

**3. Query forward citations by patent ID**
```
Retrieve the cited references for patent ID 12345678.
```
Parameters: `{"patentId": "12345678"}`

**4. Query forward citations using both identifiers**
```
Look up citations for patent ID 12345678 (publication number US10000000B2).
```
Parameters: `{"patentId": "12345678", "patentNumber": "US10000000B2"}` (patentId takes priority)

## Display Rules

1. **Present data clearly**: Show citation results in well-structured tables, separating patent citations from non-patent literature citations.
2. **Summarize counts**: Always state the total number of cited patents and cited non-patent literature items.
3. **No fabrication**: Only display data returned by the API. Do not infer or fabricate citation details.
4. **Error handling**: When a query fails, explain the reason based on the error response and suggest the user verify their patent ID or publication number.
5. **Batch results**: When querying multiple patents, organize results by patent so each patent's citations are clearly grouped.
6. **Empty results**: If a patent has no citations, explicitly inform the user rather than showing an empty table.
## User Expression & Scenario Quick Reference

**Applicable** -- Patent citation queries:

| User Says | Scenario |
|-----------|----------|
| "What patents does XX cite" | Forward citation lookup |
| "Show me the references for patent XX" | Citation detail retrieval |
| "What prior art is cited by XX" | Prior art reference query |
| "List the cited literature for XX" | Non-patent literature lookup |
| "Citation analysis for patent XX" | Combined patent + literature citation |
| "What documents does patent XX reference" | General citation query |

**Not applicable** -- Needs beyond forward citation data:
- Backward/reverse citations (who cites this patent)
- Patent validity or legal status
- Patent family analysis
- Patent full-text search
- Patent classification or landscape analysis


**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
