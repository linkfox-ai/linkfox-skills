---
name: linkfox-zhihuiya-patent-cited
description: 从智慧芽（PatSnap）查询专利被引用数据，包括被引用次数和引用专利详情。当用户提到专利被引用、被引分析、专利影响力、引用频次、专利家族被引、前向引用、想了解哪些专利引用了某一专利、patent citations, citation count, patent influence, citation analysis, PatSnap时触发此技能。即使用户未明确提及"智慧芽"或"PatSnap"，只要其需求涉及查询某专利被引用次数或被哪些专利引用，也应触发此技能。
---

# Zhihuiya Patent Citations Explorer

This skill guides you on how to query patent citation data from Zhihuiya (PatSnap), helping users understand the citation landscape of specific patents.

## Core Concepts

Patent citation analysis reveals how influential a patent is within its technology domain. When Patent B references Patent A in its prior art section, Patent A is said to be "cited by" Patent B. A higher citation count generally indicates greater technological significance and broader industry influence.

**Key metrics**:
- **3-year citations** (`citedBy3y`): Number of times the patent was cited within 3 years of publication. Indicates early-stage impact.
- **5-year citations** (`citedBy5y`): Number of times the patent was cited within 5 years. Indicates medium-term influence.
- **Simple family citations** (`citedBySimpleFamily`): Count of simple patent family members that cite the patent.
- **INPADOC family citations** (`citedByInpadocFamily`): Count of INPADOC patent family members that cite the patent.
- **PatSnap family citations** (`citedByPatsnapFamily`): Count of PatSnap-defined patent family members that cite the patent.

## Parameter Guide

You must provide at least one of the following identifiers. If both are supplied, patent ID takes priority.

| Parameter | Description | Example |
|-----------|-------------|---------|
| patentId | Zhihuiya internal patent ID. Multiple IDs separated by commas (max 100). | abc123def456 |
| patentNumber | Publication / announcement number. Multiple numbers separated by commas (max 100). | US10123456B2, CN112345678A |

**Important**: At least one of `patentId` or `patentNumber` is required. When the user provides a publication number (e.g., "US10123456B2"), use `patentNumber`. When they provide internal IDs, use `patentId`.

## Usage Examples

**1. Single patent citation lookup by publication number**
Query: "How many citations does patent US10123456B2 have?"
```json
{
  "patentNumber": "US10123456B2"
}
```

**2. Multiple patents citation comparison**
Query: "Compare citations for CN112345678A and CN113456789B"
```json
{
  "patentNumber": "CN112345678A,CN113456789B"
}
```

**3. Lookup by patent ID**
Query: "Get citation data for patent ID abc123def456"
```json
{
  "patentId": "abc123def456"
}
```

**4. Batch query with multiple IDs**
Query: "Citation info for these patent IDs: id001, id002, id003"
```json
{
  "patentId": "id001,id002,id003"
}
```

## Display Rules

1. **Present data in tables**: Show citation results in clear, structured tables. Include the publication number, 3-year citations, 5-year citations, and family citation counts.
2. **Highlight key metrics**: When comparing multiple patents, highlight the one with the highest citation counts.
3. **Explain family types**: If the user is unfamiliar with patent families, briefly explain the difference between Simple, INPADOC, and PatSnap family definitions.
4. **Citing patent details**: If the response includes a `citedByPatents` array with details of citing patents, present them in a sub-table or expandable list.
5. **Error handling**: When a query fails, explain the reason based on the response and suggest checking whether the patent number or ID is correct.
6. **No subjective advice**: Present factual citation data without making judgments about patent value or investment decisions.

## 调用方式

- **API 端点**：`POST /zhihuiya/patentCited`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/zhihuiya_cited_by.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-zhihuiya-patent-cited-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## User Expression & Scenario Quick Reference

**Applicable** -- Patent citation analysis scenarios:

| User Says | Scenario |
|-----------|----------|
| "How many times has this patent been cited" | Basic citation count |
| "Which patents cite this one" | Citing patent list |
| "Patent influence analysis" | Citation-based impact |
| "Compare citations between patents" | Multi-patent comparison |
| "3-year / 5-year citation count" | Time-windowed citation metrics |
| "Patent family citation data" | Family-level citation analysis |
| "Forward citations for patent X" | Synonym for cited-by lookup |

**Not applicable** -- Needs beyond patent citation data:
- Patent full-text search or semantic search
- Patent legal status or prosecution history
- Patent valuation or licensing recommendations
- Backward citations (references *made by* a patent)


**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
