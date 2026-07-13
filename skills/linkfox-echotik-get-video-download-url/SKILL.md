---
name: linkfox-echotik-get-video-download-url
description: 解析TikTok视频地址，返回该视频的无水印/含水印下载地址、播放地址与封面地址，用于保存带货视频素材或离线分析。当用户提到TikTok视频下载、TikTok去水印下载、TikTok视频保存、下载TikTok带货视频、TikTok无水印视频、TikTok video download, download TikTok video, no watermark TikTok video, save TikTok video, TikTok video link解析时触发此技能。即使用户未明确提及"EchoTik"，只要其需求涉及从一个TikTok视频链接取出可下载/可播放的视频地址，也应触发此技能。
---

# EchoTik TikTok Video Download

This skill guides you on how to resolve a TikTok video URL into direct download and playback links, helping sellers save influencer/promotional video assets for offline analysis or reuse.

## Core Concepts

This tool takes a single TikTok video URL and resolves it to direct media addresses: a no-watermark download URL (preferred for clean assets), a watermarked download URL, a playback URL, and cover images (static and dynamic). This is useful when a seller wants to archive a high-performing promotional video found via the EchoTik product-video tool, or reuse a creator's clip without re-recording.

**Required input**: A `url` is mandatory. Two URL formats are accepted:
- Short link: `https://vt.tiktok.com/xxxxxx`
- Full link: `https://www.tiktok.com/@user/video/1234567890`

**Conditional download URLs**: Not every video returns a downloadable address. `noWatermarkDownloadUrl` and `downloadUrl` are returned only when the source video allows it; for some videos (region/privacy/availability restricted) both are absent and only `playUrl` plus cover images come back. Always check presence before presenting a download link, and fall back to `playUrl` for playback when the download fields are missing.

**URL freshness**: The returned download/playback addresses may expire over time. Use them promptly after resolving, and re-resolve if a link stops working.

## Parameter Guide

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| url | string | Yes | TikTok video URL (short link `vt.tiktok.com/xxx` or full link `tiktok.com/@user/video/xxx`). Max length 1000 | - |

## 调用方式

- **API 端点**：`POST /echotik/getVideoDownloadUrl`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/echotik_get_video_download_url.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-echotik-get-video-download-url-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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

**1. Resolve a full TikTok video link**
```json
{
  "url": "https://www.tiktok.com/@user/video/1234567890"
}
```

**2. Resolve a TikTok short link**
```json
{
  "url": "https://vt.tiktok.com/Z123abc/"
}
```

## Display Rules

1. **Present the no-watermark link first**: When `noWatermarkDownloadUrl` is present, surface it as the primary download option, since clean assets are usually what sellers want
2. **Offer the watermarked variant**: Also list `downloadUrl` (watermarked) when present, in case the user wants the original branding
3. **Handle missing download URLs**: When both `noWatermarkDownloadUrl` and `downloadUrl` are absent (common for some videos), do not fabricate a download link — tell the user the video has no direct download address and offer `playUrl` for playback/preview instead
4. **Provide playback + cover**: Mention `playUrl` for quick preview and `coverUrl` / `dynamicCoverUrl` for thumbnails
5. **Freshness caveat**: Remind the user that the resolved URLs may expire and should be downloaded promptly
6. **Present data only**: Show the resolved addresses clearly without subjective advice on how to use the video
7. **Error handling**: When resolution fails, explain the reason based on `errcode`/`errmsg` — `400` means a missing/invalid `url`, `10000` means the link is not a valid/accessible TikTok video; suggest checking the URL format

## User Expression & Scenario Quick Reference

### Applicable Scenarios

| User Says | Scenario |
|-----------|----------|
| "Download this TikTok video" / "Save this TikTok clip" | Resolve a video URL into download links |
| "Get the no-watermark version of this TikTok video" | Prioritize `noWatermarkDownloadUrl` |
| "I want to save this influencer's promo video" | Resolve and archive a creator's video |
| "Give me a playable link for this TikTok video" | Return `playUrl` |
| "Get the cover/thumbnail of this TikTok video" | Return `coverUrl` / `dynamicCoverUrl` |

### Not Applicable Scenarios

- Listing promotional videos associated with a TikTok **product** (use `linkfox-echotik-product-video` instead — it needs a `productId`, not a video URL)
- Searching for TikTok products (use `linkfox-echotik-product-search`)
- TikTok new product rankings (use `linkfox-echotik-new-product-rank`)
- TikTok live-stream data
- Video editing or content creation advice
- Non-TikTok platform video downloads

### Boundary Judgment

When users mention "TikTok video", determine whether they already have a **specific video URL** they want to download (this skill) or want to **discover videos linked to a product** (the product-video skill). If the user provides a `tiktok.com` or `vt.tiktok.com` link and asks to save/download/extract it, this skill applies. If they mention a product ID and ask "what videos promote this product", use `linkfox-echotik-product-video` instead.

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
