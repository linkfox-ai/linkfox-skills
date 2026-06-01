---
name: linkfox-echotik-product-video
version: 1.0.0
category: product-sourcing
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

## API Usage

This tool calls the LinkFox tool gateway API. See `references/api.md` for calling conventions, request parameters, and response structure. You can also execute `scripts/echotik_list_product_video.py` directly to run queries.

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


**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

<!-- LF_LARGE_RESPONSE_BLOCK -->
## Handling Large Responses

To avoid overflowing the agent context, persist the response to disk and extract only the fields you need:

```
python scripts/response_io.py run --script scripts/echotik_list_product_video.py --out-dir <DIR> '<params>'
python scripts/response_io.py read <file> --fields "<paths>"   # or --path "<JMESPath>"
```

> Pick `--out-dir` outside any git working tree (e.g. `/tmp/...` on Unix, `%TEMP%/...` on Windows). Persisted responses may contain PII, pricing, or auth-sensitive data — do not commit them. Files are not auto-deleted; clean up when the task is done.

`run` writes the full response to a file and emits only a schema preview + file path. `read` projects specific fields, with `--limit/--offset` for slicing and `--format json|jsonl|csv|table` for output.

**When to prefer this pattern** — apply your judgment based on the response characteristics, e.g.:
- High field count per record, or fields you don't need
- Batch/paginated results (multiple items per call)
- Long-text fields (descriptions, reviews, HTML, time series)
- Output reused across later steps rather than consumed immediately

For small, single-use responses, calling the main script directly is fine.

⚠️ The preview is a truncated schema + sample, not the full data. Any field-level decision must read from the persisted file via `read`.
<!-- /LF_LARGE_RESPONSE_BLOCK -->

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
