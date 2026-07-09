---
name: linkfox-zhihuiya-pdf-data
description: 通过专利ID或公开号从智慧芽专利数据库下载专利PDF全文文档。当用户提到专利PDF下载、专利全文、专利文件获取、公开号查询、专利家族PDF替代、批量专利PDF导出、patent PDF download, patent full-text document, patent file download, PatSnap, patent PDF时触发此技能。即使用户未明确提及"智慧芽"，只要其需求涉及下载或查看专利PDF文档，也应触发此技能。
---

# Zhihuiya Patent PDF Downloader

This skill guides you on how to retrieve patent PDF full-text download links from the Zhihuiya patent database, supporting lookup by patent ID or publication number.

## Core Concepts

The Zhihuiya Patent PDF service provides direct download links to the full-text PDF documents of patents worldwide. You can query by **patent ID** or **publication number** (also called public announcement number), and retrieve up to **100 patents** in a single request.

**Lookup priority**: When both `patentId` and `patentNumber` are supplied, the service uses `patentId` first. This is important to remember when both identifiers are available.

**Family substitution**: If a patent's own PDF is unavailable, the service can optionally return the PDF of a related family patent instead.

## Parameter Guide

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| patentId | string | Conditionally | Patent ID(s). At least one of `patentId` or `patentNumber` must be provided. Separate multiple values with commas. Max 100 entries. |
| patentNumber | string | Conditionally | Publication/announcement number(s). At least one of `patentId` or `patentNumber` must be provided. Separate multiple values with commas. Max 100 entries. |
| replaceByRelated | string | No | Whether to substitute with a family patent PDF when the original is unavailable. `1` = yes, `0` = no. Defaults to no substitution. |

### How to Choose the Right Identifier

- **Patent ID** (`patentId`): An internal numeric identifier within the Zhihuiya system. Use this when the user provides Zhihuiya-specific IDs.
- **Publication Number** (`patentNumber`): The public-facing patent number (e.g., `US20230012345A1`, `CN115000000A`). Use this when the user provides standard patent numbers.

## Response Fields

| Field | Description |
|-------|-------------|
| total | Number of records returned |
| data | Array of patent objects, each containing download information |
| data[].patentId | The patent ID |
| data[].pn | The publication/announcement number |
| data[].pdfPath | The PDF full-text download URL |
| data[].pnRelated | Publication number of the substitute family patent (only present when family substitution is used) |
| costToken | Tokens consumed by the request |

## 调用方式

- **API 端点**：`POST /zhihuiya/pdfData`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/zhihuiya_pdf_data.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-zhihuiya-pdf-data-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。
## Usage Examples

**1. Single Patent by Publication Number**
```
Retrieve the PDF for patent publication number US20230012345A1.
```
Parameters: `{"patentNumber": "US20230012345A1"}`

**2. Multiple Patents by Publication Number**
```
Download PDFs for CN115000000A, CN115000001A, and CN115000002A.
```
Parameters: `{"patentNumber": "CN115000000A,CN115000001A,CN115000002A"}`

**3. Single Patent by Patent ID**
```
Get the full-text PDF for patent ID 12345678.
```
Parameters: `{"patentId": "12345678"}`

**4. With Family Substitution Enabled**
```
Download the PDF for EP4000000A1. If it is unavailable, use a family patent PDF instead.
```
Parameters: `{"patentNumber": "EP4000000A1", "replaceByRelated": "1"}`

**5. Batch Download by Patent IDs**
```
Retrieve PDFs for patent IDs 11111111, 22222222, 33333333.
```
Parameters: `{"patentId": "11111111,22222222,33333333"}`

## Display Rules

1. **Present download links clearly**: For each patent, show the publication number and its PDF download link in a clean table or list format.
2. **Highlight substitutions**: If a PDF was provided via family patent substitution, explicitly note this and show the `pnRelated` value so the user knows which family patent was used.
3. **Batch results**: When multiple patents are returned, present them in a table with columns: Publication Number, Patent ID, PDF Link, and Substitution Note (if applicable).
4. **Error handling**: When a query fails or returns no results, explain the reason and suggest the user verify the patent ID or publication number. If `replaceByRelated` was not enabled, suggest enabling it as an alternative.
5. **No PDF available**: If a patent entry is returned without a `pdfPath`, inform the user that the PDF is not available and suggest enabling family substitution.
## Important Limitations

- **Batch limit**: A maximum of 100 patents per request.
- **Identifier requirement**: At least one of `patentId` or `patentNumber` must be provided; the request will fail if both are empty.
- **Priority rule**: When both identifiers are provided, `patentId` takes precedence over `patentNumber`.
- **PDF availability**: Not all patents have PDFs available. Use the `replaceByRelated` option to fall back to family patents.

## User Expression & Scenario Quick Reference

**Applicable** -- Patent PDF document retrieval tasks:

| User Says | Scenario |
|-----------|----------|
| "Download the PDF for patent XX" | Single patent PDF retrieval |
| "Get full-text documents for these patents" | Batch patent PDF download |
| "I need the PDF for publication number XX" | Lookup by publication number |
| "Can I get the patent document even if it's not directly available" | Family substitution scenario |
| "Batch export patent PDFs" | Multi-patent batch download |

**Not applicable** -- Needs beyond patent PDF retrieval:
- Patent search or discovery (finding patents by keyword, assignee, etc.)
- Patent citation or legal status analysis
- Patent claim interpretation or translation
- Patent portfolio analytics or landscape mapping


**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
