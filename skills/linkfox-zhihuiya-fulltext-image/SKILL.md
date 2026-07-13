---
name: linkfox-zhihuiya-fulltext-image
description: 通过专利ID或公开号获取专利文件中的全文附图（图纸、示意图、图表）。当用户询问专利图片、专利图纸、专利示意图、专利插图、全文附图、专利图表、专利技术图或想查看、下载专利文件中的嵌入图片、patent fulltext drawings, patent diagrams, technical drawings, patent images, PatSnap时触发此技能。即使用户未明确提及"全文附图"，只要其需求涉及获取特定专利中的视觉内容（图纸、示意图、图表），也应触发此技能。
---

# Zhihuiya Patent Fulltext Image

This skill guides you on how to retrieve fulltext images (drawings, figures, diagrams) from patent documents using the Zhihuiya patent data service, helping users access and analyze visual content within patents.

## Core Concepts

Patent fulltext images are the figures, drawings, and diagrams embedded in patent documents. They are essential for understanding the technical details of an invention. This tool queries the Zhihuiya patent database and returns image metadata including download paths and image types for a given patent.

**Lookup methods**: You can look up images by either **patent ID** (an internal identifier) or **publication number** (the publicly visible patent number such as `US20230012345A1` or `CN115000000A`). At least one of these must be provided.

## Parameter Guide

| Parameter | API Name | Required | Description | Example |
|-----------|----------|----------|-------------|---------|
| Patent ID | patentId | No* | Internal patent identifier | 8a7b6c5d-... |
| Publication Number | patentNumber | No* | Public patent publication/grant number | US20230012345A1 |
| Limit | limit | No | Maximum number of images to return (max 100, default 100) | 50 |
| Offset | offset | No | Pagination offset for image results | 0 |

> *At least one of `patentId` or `patentNumber` must be provided.

## Response Fields

| Field | Description |
|-------|-------------|
| total | Total number of image records available |
| data | Array of image entries |
| data[].patentId | Patent identifier |
| data[].pn | Publication/grant number |
| data[].fulltextImagePath | URL path to download the image |
| data[].imageType | Type/category of the image |
| columns | Column rendering metadata |
| costToken | Token cost of the request |
| type | Rendering style hint |

## 调用方式

- **API 端点**：`POST /zhihuiya/fulltextImage`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/zhihuiya_fulltext_image.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-zhihuiya-fulltext-image-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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

**1. Get all images for a patent by publication number**
```
Retrieve fulltext images for patent US20230012345A1.
```
Parameters: `{"patentNumber": "US20230012345A1"}`

**2. Get images for a patent by patent ID**
```
Fetch the drawings for patent ID abc123def456.
```
Parameters: `{"patentId": "abc123def456"}`

**3. Paginated retrieval of images**
```
Get the first 20 images for patent CN115000000A.
```
Parameters: `{"patentNumber": "CN115000000A", "limit": "20", "offset": "0"}`

**4. Get the next page of images**
```
Get images 21-40 for patent CN115000000A.
```
Parameters: `{"patentNumber": "CN115000000A", "limit": "20", "offset": "20"}`

## Display Rules

1. **Present data clearly**: Show image results in a structured table with image type, download path, and patent number
2. **Image links**: Always present `fulltextImagePath` values as clickable links so users can view or download images directly
3. **Pagination notice**: When `total` exceeds the number of returned results, inform the user that more images are available and offer to fetch the next page
4. **Error handling**: When a query fails, explain the reason and suggest verifying the patent ID or publication number
5. **No fabrication**: Never invent patent IDs, publication numbers, or image URLs -- only display data returned by the API
6. **Total count**: Always mention the total number of images available for the patent
## Important Limitations

- **Image limit**: Each request returns a maximum of 100 images
- **Identifier required**: At least one of `patentId` or `patentNumber` must be supplied
- **All parameters are strings**: Even numeric values like `limit` and `offset` must be passed as strings

## User Expression & Scenario Quick Reference

**Applicable** -- Requests involving patent visual content:

| User Says | Scenario |
|-----------|----------|
| "Show me the drawings for patent XX" | Fulltext image retrieval |
| "Get the figures from this patent" | Fulltext image retrieval |
| "Download patent images for XX" | Fulltext image retrieval |
| "What diagrams does patent XX contain" | Fulltext image listing |
| "How many figures are in patent XX" | Image count query |
| "Show me the technical drawings" | Fulltext image retrieval |

**Not applicable** -- Needs beyond patent fulltext images:
- Patent text/abstract/claims search
- Patent family or citation analysis
- Patent legal status queries
- Patent assignee or inventor search
- General image search unrelated to patents

## 积分消耗规则

消耗 81 积分。

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
