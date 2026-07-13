---
name: linkfox-eureka-abstract-image
description: 通过Eureka专利数据平台获取专利摘要附图。当用户提到专利摘要附图、专利图纸、专利示意图、专利图片、摘要附图检索、专利图片查询、Eureka摘要附图、patent abstract images, patent drawings, patent illustrations, Eureka, abstract image lookup, patent figure时触发此技能。即使用户未明确说"摘要附图"，只要其需要查看专利文件中的图纸或示意图，也应触发此技能。
---

# Eureka Patent Abstract Image

This skill guides you on how to retrieve abstract images (drawings) from the Eureka patent data platform, helping users quickly obtain the illustrative figures associated with specific patents.

## Core Concepts

Abstract images (abstract drawings) are the representative figures attached to a patent document's abstract section. They provide a quick visual overview of the invention. This tool queries the Eureka patent platform and returns download paths for these images.

**Lookup logic**: You must provide at least one of two identifiers -- a patent ID or a publication number. If both are provided, patent ID takes priority. You can query up to 100 patents in a single request by separating values with commas.

## Parameter Guide

| Parameter | API Name | Required | Description | Example |
|-----------|----------|----------|-------------|---------|
| Patent ID | patentId | Conditionally (one of the two must be provided) | Internal patent identifier; multiple values separated by commas, max 100 | 5e6f7a8b9c |
| Publication Number | patentNumber | Conditionally (one of the two must be provided) | Patent publication/announcement number; multiple values separated by commas, max 100 | CN115059423A, US11234567B2 |

- At least one of `patentId` or `patentNumber` must be supplied.
- If both are supplied, `patentId` takes precedence.
- Multiple values are separated by commas (English commas), with an upper limit of 100.

## Response Fields

| Field | API Name | Description |
|-------|----------|-------------|
| Patent ID | patentId | The internal patent identifier |
| Publication Number | pn | The publication/announcement number |
| Abstract Drawing Path | abstractDrawingPath | URL path to the abstract image file |
| Total | total | Total number of records returned |
| Cost Token | costToken | Tokens consumed by the query |

## 调用方式

- **API 端点**：`POST /tool-eureka/abstractImage`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/eureka_abstract_image.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-eureka-abstract-image-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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

**1. Single patent lookup by publication number**
```
Retrieve the abstract image for patent CN115059423A.
```

**2. Multiple patents lookup by publication number**
```
Get abstract drawings for patents US11234567B2, EP3456789A1, and CN115059423A.
```

**3. Lookup by patent ID**
```
Fetch the abstract image for patent ID 5e6f7a8b9c.
```

**4. Batch lookup with mixed identifiers**
```
I have the following patent IDs: abc123, def456. Please get their abstract images.
```

## Display Rules

1. **Show the image**: When the response includes an `abstractDrawingPath`, display the image directly using Markdown image syntax so the user can see the drawing inline.
2. **Patent identification**: Always show the publication number (`pn`) alongside each image so the user knows which patent each drawing belongs to.
3. **Missing images**: If a patent has no abstract drawing (empty `abstractDrawingPath`), explicitly inform the user that no abstract image is available for that patent.
4. **Batch results**: When multiple patents are queried, present results in a clear, organized list or table format.
5. **Error handling**: When a query fails, explain the reason based on the response and suggest the user verify their patent IDs or publication numbers.

## Important Limitations

- **Up to 100 patents per request**: The maximum number of patent IDs or publication numbers in a single call is 100.
- **At least one identifier required**: Either `patentId` or `patentNumber` must be provided; the request will fail if both are empty.
- **Patent ID priority**: When both `patentId` and `patentNumber` are provided, the system uses `patentId` and ignores `patentNumber`.
- **Data coverage**: Results depend on the Eureka patent platform's database coverage; some very recent filings may not yet be reflected.

## User Expression & Scenario Quick Reference

**Applicable** -- Patent abstract image retrieval:

| User Says | Scenario |
|-----------|----------|
| "Show me the abstract image for patent XX" | Single patent image lookup |
| "Get the drawings for these patents" | Batch patent image lookup |
| "What does the patent figure look like" | Abstract drawing retrieval |
| "Retrieve patent illustrations for XX" | Image download path retrieval |
| "I need the abstract drawing for publication number XX" | Lookup by publication number |

**Not applicable** -- Needs beyond abstract image retrieval:
- Full patent text or claims analysis
- Patent search by keyword or classification
- Patent legal status or family information
- Patent citation or prior art analysis
- Patent valuation or infringement analysis

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
