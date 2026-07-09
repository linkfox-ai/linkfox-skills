---
name: linkfox-zhihuiya-legal-status
description: 从智慧芽（PatSnap）数据库查询专利法律状态信息。当用户提到专利法律状态、专利有效性核查、专利状态查询、专利事件历史、简单法律状态、转让、许可、质押、异议、诉讼、复审等法律事件、patent legal status, patent validity, patent events, transfer/license/pledge, PatSnap, patent status lookup时触发此技能。当用户询问专利是否处于有效、无效、审中、过期、授权、撤回或撤销状态，或想通过专利ID或公开号查询法律状态时也应触发。
---

# Zhihuiya Patent Legal Status

This skill guides you on how to query patent legal status information via the Zhihuiya (PatSnap) platform, helping users quickly determine the current legal standing and event history of one or more patents.

## 调用方式

- **API 端点**：`POST /zhihuiya/legalStatus`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/zhihuiya_legal_status.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-zhihuiya-legal-status-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## Core Concepts

The Zhihuiya Patent Legal Status tool returns three layers of legal information for each patent:

1. **Simple Legal Status** -- A high-level summary of the patent's current standing (e.g., Active, Inactive, Pending, Undetermined, PCT designated period, PCT designated expiration).
2. **Legal Status** -- A detailed status describing the patent's lifecycle stage (e.g., Published, Examining, Granted, Abandoned, Withdrawn, Rejected, Expired, Revoked, Ceased, Restoration, etc.).
3. **Legal Events** -- Specific legal actions that have occurred on the patent (e.g., Transfer, License, Pledge, Opposition, Litigation, Re-examination, Customs, Preservation, Invalid-procedure, Oral-procedure, Declassification, Double application, Trust).

**Patent identification**: Patents can be looked up by either patent ID or publication (announcement) number. When both are provided, patent ID takes priority. Multiple values can be submitted in a single request (comma-separated, up to 100).

## Parameter Guide

| Parameter | Required | Description |
|-----------|----------|-------------|
| patentId | Conditionally | Patent ID. At least one of patentId or patentNumber must be provided. Comma-separated for multiple values, up to 100. |
| patentNumber | Conditionally | Publication (announcement) number. At least one of patentId or patentNumber must be provided. Comma-separated for multiple values, up to 100. |

- If the user provides a publication number (e.g., CN115xxxxxxA, US11xxxxxxB2, EP3xxxxxxA1), use `patentNumber`.
- If the user provides an internal patent ID, use `patentId`.
- When both are supplied, `patentId` takes precedence.

## Response Fields

| Field | Description |
|-------|-------------|
| patentId | The patent's internal ID |
| pn | Publication (announcement) number |
| simpleLegalStatus | High-level status: Active, Inactive, Pending, Undetermined, PCT designated period, PCT designated expiration |
| legalStatus | Detailed lifecycle status (Published, Examining, Granted, Abandoned, Withdrawn, Rejected, Expired, Revoked, Ceased, etc.) |
| eventStatus | Legal events (Transfer, License, Pledge, Opposition, Litigation, Re-examination, etc.) |
| legalDate | Date of the most recent legal status update |

## Usage Examples

**1. Check whether a single patent is still active**
```
Query the legal status for patent publication number CN115000000A.
```

**2. Batch-check legal status for multiple patents**
```
Look up the legal status for patents US11000000B2, EP3000000A1, and CN115000001A.
```

**3. Identify legal events on a patent**
```
Has patent CN115000000A been involved in any litigation, transfer, or pledge events?
```

**4. Determine if a patent has expired or been revoked**
```
Check if patent US10000000B1 is expired, revoked, or still in force.
```

**5. Look up patents by patent ID**
```
Query the legal status for patent IDs abc123, def456.
```

## Display Rules

1. **Present data clearly**: Show results in a structured table. Include the publication number, simple legal status, detailed legal status, and legal events for each patent.
2. **Translate status values**: When the user's language preference is clear, present status labels in that language while keeping the canonical English value in parentheses for precision.
3. **Highlight key findings**: If the user is checking validity, prominently state whether each patent is Active, Inactive, or Pending at the top of the response.
4. **Legal date context**: When `legalDate` is available, include it so users know how recent the status information is.
5. **Error handling**: If the query fails or returns no results, explain the possible reasons (invalid patent number format, patent not found in database) and suggest the user double-check the input.
6. **Volume notice**: When querying many patents, present a summary table and note the total count returned.
## Important Limitations

- **Up to 100 patents per request**: The maximum number of patent IDs or publication numbers in a single call is 100.
- **At least one identifier required**: Either `patentId` or `patentNumber` must be provided; the request will fail if both are empty.
- **Patent ID priority**: When both `patentId` and `patentNumber` are provided, the system uses `patentId` and ignores `patentNumber`.
- **Data coverage**: Results depend on the Zhihuiya (PatSnap) database coverage; some very recent filings may not yet be reflected.

## User Expression & Scenario Quick Reference

**Applicable** -- Queries about patent legal standing and events:

| User Says | Scenario |
|-----------|----------|
| "Is this patent still valid/active" | Simple legal status check |
| "What is the legal status of patent XX" | Detailed status lookup |
| "Has this patent been transferred or licensed" | Legal event query |
| "Check if these patents are expired" | Batch validity check |
| "Any litigation on this patent" | Legal event filtering |
| "Patent legal status for CN115XXXXXXA" | Direct publication number lookup |

**Not applicable** -- Needs beyond patent legal status:

- Patent search by keyword, classification, or applicant name
- Patent full-text or claims retrieval
- Patent valuation or commercial analysis
- Freedom-to-operate (FTO) analysis
- Patent family or citation analysis


**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
