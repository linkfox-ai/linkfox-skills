---
name: linkfox-zhihuiya-claim-data
description: 从智慧芽（PatSnap）获取专利权利要求数据。当用户提到专利权利要求、权利要求文本、独立权利要求、从属权利要求、权利要求数量、权利要求树、权利要求分析、权利要求范围、权利要求语言、想查看特定专利的权利要求部分、patent claims, independent claims, dependent claims, claims text, PatSnap时触发此技能。即使用户未明确提及"智慧芽"或"PatSnap"，只要其请求涉及通过专利ID或公开号获取或分析专利权利要求信息，也应触发此技能。
---

# Zhihuiya Patent Claims Data

This skill guides you on how to retrieve and present patent claims data from the Zhihuiya (PatSnap) patent database, helping IP professionals, patent analysts, and R&D teams quickly access the claims section of any patent.

## 调用方式

- **API 端点**：`POST /zhihuiya/claimData`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/zhihuiya_claim_data.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-zhihuiya-claim-data-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## Core Concepts

Patent claims define the legal scope of protection granted by a patent. They are the most critical part of a patent document for infringement analysis, freedom-to-operate assessments, and prior art comparisons. This tool retrieves the full set of claims for one or more patents by their patent ID or publication number.

**Family substitution**: When a patent's claims are unavailable in the database, you can optionally request that claims from a related family member patent be returned instead. This is controlled by the `replaceByRelated` parameter.

## Data Fields

| Field | API Name | Description | Example |
|-------|----------|-------------|---------|
| Patent ID | patentId | Internal Zhihuiya patent identifier | 98a1b2c3-... |
| Publication Number | pn | Publication or grant number of the patent | CN115000000A |
| Related PN | pnRelated | Publication number of the family member used as substitute (only present when family substitution occurred) | US20230001234A1 |
| Claims | claims | Array of claim objects containing the claim text and metadata | [...] |
| Claim Count | claimCount | Total number of claims in the patent | 15 |

## Parameter Guide

### Required (at least one)

You must provide **at least one** of the following two parameters. If both are provided, `patentId` takes priority.

| Parameter | Description | Format |
|-----------|-------------|--------|
| patentId | One or more Zhihuiya patent IDs | Comma-separated string, max 100 entries |
| patentNumber | One or more publication/grant numbers | Comma-separated string, max 100 entries |

### Optional

| Parameter | Description | Values |
|-----------|-------------|--------|
| replaceByRelated | Whether to substitute with a family member's claims when the target patent's claims are unavailable | `1` = yes, `0` = no (default) |

### How to Choose Between patentId and patentNumber

- Use **patentNumber** when the user provides a publication or grant number (e.g., `CN115000000A`, `US11234567B2`). This is the most common scenario.
- Use **patentId** when the user provides an internal Zhihuiya identifier, typically obtained from a previous Zhihuiya search result.
- When the user provides both, pass both and the API will prefer patentId.

## Usage Examples

**1. Single patent by publication number**
```json
{"patentNumber": "CN115000000A"}
```

**2. Multiple patents by publication number**
```json
{"patentNumber": "CN115000000A,US20230001234A1,EP4000000A1"}
```

**3. Single patent by patent ID**
```json
{"patentId": "98a1b2c3-xxxx-xxxx-xxxx-xxxxxxxxxxxx"}
```

**4. With family substitution enabled**
```json
{"patentNumber": "CN115000000A", "replaceByRelated": "1"}
```

**5. Batch query with family substitution**
```json
{"patentNumber": "CN115000000A,JP2023100000A", "replaceByRelated": "1"}
```

## Display Rules

1. **Present claims clearly**: Display claims in a numbered list preserving the original claim numbering. Use indentation or formatting to distinguish independent claims from dependent claims where possible.
2. **Highlight claim count**: Always state the total number of claims returned for each patent.
3. **Family substitution notice**: If `pnRelated` is present in a result, explicitly inform the user that the claims shown are from a family member patent and provide the family member's publication number.
4. **Batch results**: When multiple patents are queried, organize results by patent with clear headings showing the publication number.
5. **Error handling**: When a query fails, explain the reason based on the response and suggest the user verify the patent number format or try enabling family substitution.
6. **No subjective analysis**: Present the raw claim text without legal interpretation unless the user specifically requests analysis.
## Important Limitations

- **At least one identifier required**: Either `patentId` or `patentNumber` must be provided; omitting both will result in an error.
- **Batch limit**: A maximum of 100 patents can be queried in a single request.
- **Claims availability**: Not all patents have claims data available. Use `replaceByRelated` = `1` to attempt family member substitution when claims are missing.
- **Claim object structure**: The individual claim objects within the `claims` array may vary in structure depending on the patent office and data source.

## User Expression & Scenario Quick Reference

**Applicable** -- Patent claims retrieval and analysis:

| User Says | Scenario |
|-----------|----------|
| "Show me the claims of patent XX" | Single patent claims lookup |
| "Get the claim text for these patents" | Batch claims retrieval |
| "How many claims does patent XX have" | Claim count query |
| "What are the independent claims of XX" | Claims retrieval + display |
| "Compare claims of patent A and patent B" | Multi-patent claims retrieval |
| "The claims are not available, try a family member" | Family substitution query |
| "Patent claim scope", "claim language" | Claims retrieval |

**Not applicable** -- Needs beyond patent claims data:
- Patent search or discovery (finding patents by keyword/topic)
- Patent legal status or prosecution history
- Patent citation or reference analysis
- Patent full-text beyond claims (abstract, description, drawings)
- Freedom-to-operate or infringement opinions (legal advice)


**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
