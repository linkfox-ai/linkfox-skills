---
name: linkfox-echotik-product-video
description: 查询TikTok商品的关联带货视频数据，包括播放量、点赞、评论、分享、视频销量与GMV，分析商品的视频营销表现与达人内容效果。当用户提到TikTok商品视频、TikTok带货视频、商品关联视频、视频营销分析、达人视频表现、TikTok视频销量、TikTok video sales, product video analysis, influencer video performance, TikTok promotional videos, product marketing videos时触发此技能。即使用户未明确提及"EchoTik"或"商品视频"，只要其需求涉及查看某个TikTok商品有哪些带货视频、视频的播放和转化数据，也应触发此技能。
---

# EchoTik - TikTok Product Video

This skill guides you on how to query promotional videos associated with a TikTok Shop product, helping sellers analyze video marketing performance and identify effective influencer content strategies.

## Core Concepts

This tool retrieves the list of promotional videos linked to a specific TikTok product. Each video record includes engagement metrics (views, likes, comments, shares, favorites), estimated sales attribution (video sales count and GMV), video metadata (duration, resolution, publish date), and the creator (influencer) ID. This enables sellers to understand which videos drive the most sales for a product and what content patterns work best.

**Required input**: A `productId` is mandatory. You can obtain product IDs from the EchoTik product search tool (`linkfox-echotik-product-search`) or the new product ranking tool (`linkfox-echotik-new-product-rank`).

**Sort fields**: Videos can be sorted by views (1), likes (2), shares (3), video sales (4), video GMV (5), or publish date (6).

**Pagination**: `pageSize` must be a multiple of 10, max 100. The backend fetches in batches of 10 and merges results.

## Parameter Guide

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| productId | string | Yes | TikTok product ID | - |
| userId | string | No | Filter by influencer ID | - |
| productVideoSortField | integer | No | Sort field: 1=views, 2=likes, 3=shares, 4=video sales, 5=video GMV, 6=publish date | 1 |
| sortType | integer | No | Sort order: 0=ascending, 1=descending | 1 |
| minCreateTime | integer | No | Video publish start time (Unix timestamp in seconds) | - |
| maxCreateTime | integer | No | Video publish end time (Unix timestamp in seconds) | - |
| pageNum | integer | No | Page number | 1 |
| pageSize | integer | No | Results per page (multiple of 10, max 100) | 50 |

## 调用方式

- **API 端点**：`POST /echotik/listProductVideo`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/echotik_list_product_video.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-echotik-product-video-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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

**1. Top videos by views for a product**
```json
{
  "productId": "1729382310407603945",
  "productVideoSortField": 1,
  "sortType": 1,
  "pageSize": 20
}
```

**2. Find highest-converting videos (by video sales)**
```json
{
  "productId": "1729382310407603945",
  "productVideoSortField": 4,
  "sortType": 1,
  "pageSize": 20
}
```

**3. Videos by a specific influencer for a product**
```json
{
  "productId": "1729382310407603945",
  "userId": "7234567890123456789",
  "productVideoSortField": 1,
  "sortType": 1
}
```

**4. Recent videos in a time range (sorted by GMV)**
```json
{
  "productId": "1729382310407603945",
  "minCreateTime": 1717200000,
  "maxCreateTime": 1719792000,
  "productVideoSortField": 5,
  "sortType": 1
}
```

**5. Videos sorted by publish date (newest first)**
```json
{
  "productId": "1729382310407603945",
  "productVideoSortField": 6,
  "sortType": 1,
  "pageSize": 50
}
```

## Display Rules

1. **Present data in tables**: Show video description (truncated if long), views, likes, comments, shares, video sales, video GMV, publish date, and influencer ID
2. **Link to original**: When `officialUrl` is available, provide it so users can view the video on TikTok
3. **Estimation notice**: Video sales and GMV are estimated values, remind users these are approximations
4. **Cover image**: If `coverUrl` is present, mention it so the user knows video thumbnails are available
5. **Duration formatting**: Convert `duration` (seconds) to a readable format (e.g., "1:30" for 90 seconds)
6. **Hashtag display**: Show `hashTag` when present to help users understand content themes
7. **Playback URL caveat**: The `playAddr` field may expire quickly; prefer `officialUrl` for sharing

## User Expression & Scenario Quick Reference

### Applicable Scenarios

| User Says | Scenario |
|-----------|----------|
| "Show me the promotional videos for this TikTok product" | Query videos by product ID |
| "Which videos are driving the most sales for this product" | Sort by video sales (field 4) |
| "What influencer videos are promoting this product" | General video list query |
| "Show me videos by a specific creator for this product" | Filter by userId |
| "Recent promotional videos for this product" | Filter by time range or sort by date |
| "Which TikTok videos have the highest GMV for this product" | Sort by video GMV (field 5) |
| "Analyze the video marketing performance of this product" | Comprehensive video list query |

### Not Applicable Scenarios

- Searching for products (use `linkfox-echotik-product-search` instead)
- TikTok new product rankings (use `linkfox-echotik-new-product-rank` instead)
- Influencer profile analytics (follower count, bio, overall performance)
- TikTok live-stream data
- Video content creation or editing advice
- TikTok advertising / ad campaign management
- Non-TikTok platform video data

### Boundary Judgment

When users ask about "TikTok videos", determine whether they want videos associated with a specific product (this skill) or general TikTok video analytics (not this skill). If they mention a product ID or ask "what videos are promoting product X", this skill applies. If they ask about trending videos in general without a product context, this skill does not apply.

## 积分消耗规则

消耗 4.5 积分。

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
