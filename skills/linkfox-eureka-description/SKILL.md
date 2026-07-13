---
name: linkfox-eureka-description
description: 通过Eureka专利数据平台获取专利说明书（描述）数据。当用户提到专利说明书、专利全文、专利技术描述、专利实施方式详情、Eureka说明书数据、patent specification, patent full text, technical description, embodiment details, Eureka, patent detailed description, patent description data时触发此技能。即使用户未明确说"Eureka"，只要其需要查看一项或多项专利的完整说明书/描述内容，也应触发此技能。
---

# Eureka Patent Description Data

This skill guides you on how to query patent description (specification) data from the Eureka patent data platform, helping users retrieve the full-text description content of specific patents.

## Core Concepts

A patent description (also called the specification) is the detailed technical document that accompanies a patent filing. It discloses how the invention works, preferred embodiments, and other technical details required by patent law. This tool queries the Eureka platform to return description data for one or more patents identified by their internal patent ID or public publication number.

**Identifier priority**: When both a patent ID and a publication number are provided for the same query, the patent ID takes precedence.

**Family substitution**: If the description for a given patent is unavailable, the tool can optionally return the description from a related family member patent instead.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| patentId | string | Conditionally | Internal patent ID. At least one of patentId or patentNumber must be provided. Multiple values separated by commas; max 100. |
| patentNumber | string | Conditionally | Publication / announcement number. At least one of patentId or patentNumber must be provided. Multiple values separated by commas; max 100. |
| replaceByRelated | string | No | Whether to substitute a family patent's description when the target patent's description is unavailable. `1` = yes, `0` = no. |

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Number of patent records returned |
| data | array | List of patent description objects |
| data[].patentId | string | Patent ID |
| data[].pn | string | Publication number |
| data[].pnRelated | string | Publication number of the substitute family patent (only present when family substitution is used) |
| data[].description | array | Description / specification content sections |
| columns | array | Column definitions for rendering |
| costToken | integer | Tokens consumed by the query |
| type | string | Rendering style hint |

## 调用方式

- **API 端点**：`POST /tool-eureka/descriptionData`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/eureka_description.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-eureka-description-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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

## How to Build Queries

### Querying by Publication Number

When users provide a patent publication number (e.g., CN115099012A, US20230012345A1), pass it via the `patentNumber` parameter:

```
patentNumber: "CN115099012A"
```

### Querying by Patent ID

When users provide internal patent IDs, pass them via the `patentId` parameter:

```
patentId: "abc123def456"
```

### Batch Queries

Both `patentId` and `patentNumber` accept comma-separated values for batch lookups (up to 100):

```
patentNumber: "CN115099012A,US20230012345A1,EP4123456A1"
```

### Family Substitution

When a patent's description is not available in the database and the user still wants content, enable family substitution:

```
patentNumber: "CN115099012A"
replaceByRelated: "1"
```

## Usage Examples

**1. Look up a single patent description by publication number**
```
patentNumber: "CN115099012A"
```

**2. Look up descriptions for multiple patents at once**
```
patentNumber: "CN115099012A,US20230012345A1"
```

**3. Look up with family substitution enabled**
```
patentNumber: "CN115099012A"
replaceByRelated: "1"
```

**4. Look up by patent ID**
```
patentId: "some-patent-id"
```

## Display Rules

1. **Present data faithfully**: Show the returned description content clearly without altering technical details or adding subjective interpretation.
2. **Structured output**: When the description contains multiple sections (background, summary, detailed description, claims, etc.), present them with clear headings for readability.
3. **Family substitution notice**: If the response includes a `pnRelated` field, explicitly inform the user that the description was sourced from a related family patent and state the substitute publication number.
4. **Batch results**: When multiple patents are returned, clearly separate each patent's content with its publication number as a heading.
5. **Error handling**: When a query fails or returns no data, explain the reason and suggest the user verify the patent ID or publication number.

## Important Limitations

- **Identifier requirement**: At least one of `patentId` or `patentNumber` must be provided; the tool cannot search by keyword or applicant name.
- **Batch limit**: A maximum of 100 patents can be queried in a single request.
- **Availability**: Not all patents have descriptions available in the database. Use `replaceByRelated: "1"` to attempt family substitution when needed.
- **Priority rule**: If both `patentId` and `patentNumber` are supplied, `patentId` takes precedence.

## User Expression & Scenario Quick Reference

**Applicable** -- Queries about patent description / specification content:

| User Says | Scenario |
|-----------|----------|
| "Show me the description of patent XX" | Single patent description lookup |
| "Get the full specification for these patents" | Batch patent description retrieval |
| "I need the detailed text of CN115099012A" | Lookup by publication number |
| "Can you find a family patent's description instead" | Family substitution query |
| "What does this patent describe technically" | Description content review |

**Not applicable** -- Needs beyond patent description data:
- Patent search by keyword, applicant, or classification
- Patent claim analysis or claim chart generation
- Patent legal status or prosecution history
- Patent landscape or statistical analysis
- Freedom-to-operate or infringement opinions

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
