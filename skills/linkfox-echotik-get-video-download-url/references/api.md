# EchoTik TikTok 视频下载 API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/echotik/getVideoDownloadUrl`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| url | string | 是 | TikTok 视频地址，支持两种格式：`https://vt.tiktok.com/xxx` 短链或 `https://www.tiktok.com/@user/video/xxx` 完整链接。最大长度 1000 |

## 响应结构

成功时 HTTP 状态码为 200，响应体顶层同时包含业务码 `errcode=200`、`errmsg="ok"` 与下列数据字段。

| 字段 | 类型 | 是否必返 | 说明 |
|------|------|----------|------|
| noWatermarkDownloadUrl | string | 条件返回 | 视频下载地址（无水印）。**并非所有视频都返回**：部分视频该字段缺省，此时无法提供无水印下载 |
| downloadUrl | string | 条件返回 | 视频下载地址（含水印）。**并非所有视频都返回**：与无水印地址一同缺省或出现 |
| playUrl | string | 始终返回 | 视频播放地址。当下载地址缺省时，可作为播放/预览的兜底 |
| coverUrl | string | 始终返回 | 视频封面地址（静态） |
| dynamicCoverUrl | string | 始终返回 | 视频动态封面地址 |
| videoId | string | 始终返回 | 视频 ID |
| columns | array | 始终返回 | 渲染列定义（字段元数据：field/title/cellType/filterable/sortable，供前端表格渲染用） |
| type | string | 始终返回 | 渲染样式（如 `tableListWorkbenches`） |
| costToken | integer | 始终返回 | 消耗 token |
| errcode | integer | 始终返回 | 业务码，200 表示成功 |
| errmsg | string | 始终返回 | 业务信息，成功时为 `ok` |

> **下载地址缺省说明**：实测部分视频（受区域、隐私或源站限制）不会返回 `noWatermarkDownloadUrl` / `downloadUrl`，仅返回 `playUrl` 与封面。此时应向用户说明该视频暂无可直接下载地址，可改用 `playUrl` 播放预览。

成功响应示例（真实调用，已截断长 URL）：

```json
{
  "errcode": 200,
  "errmsg": "ok",
  "videoId": "7096674515245206810",
  "noWatermarkDownloadUrl": "https://v45.tiktokcdn-eu.com/51678f6e0de3...",
  "downloadUrl": "https://v45.tiktokcdn-eu.com/626c5d3d5a7d...",
  "playUrl": "https://v45.tiktokcdn-eu.com/51678f6e0de3...",
  "coverUrl": "https://agent-files.linkfox.com/tiktok/20260629/7096674515245206810.jpg",
  "dynamicCoverUrl": "https://p16-common-sign.tiktokcdn-eu.com/tos-useast2a-p-0037...",
  "type": "tableListWorkbenches",
  "costToken": 12000,
  "columns": [/* 渲染列定义 */]
}
```

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 `errcode` 字段区分（`errcode = 200` 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 `errcode` 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析业务字段 |
| 400 | 参数错误 | `errmsg` 会指明缺失项，如 `url 为必填参数`；检查 `url` 是否传入且非空 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。|
| 402 | 积分不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。|
| 10000 | 未获取到视频下载地址 | URL 非 TikTok 视频链接、视频不可访问或已被删除；提示用户检查链接是否为有效的 TikTok 视频地址 |
| 其他非200值 | 业务异常 | 参考 `errmsg` 字段获取具体错误原因 |

错误响应示例：

```json
// 参数缺失
{
    "errcode": 400,
    "errmsg": "url 为必填参数",
    "url": ""
}

// 非有效 TikTok 视频链接
{
    "errcode": 10000,
    "errmsg": "未获取到视频下载地址"
}

// 未授权
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/echotik/getVideoDownloadUrl \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.tiktok.com/@user/video/1234567890"
  }'
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-echotik-get-video-download-url",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Resolved the video URL correctly, user was satisfied."
}
```

**Field rules:**
- `skillName`: Use this skill's `name` from the YAML frontmatter
- `sentiment`: Choose ONE — `POSITIVE` (praise), `NEUTRAL` (suggestion without emotion), `NEGATIVE` (complaint or error)
- `category`: Choose ONE — `BUG` (malfunction or wrong data), `COMPLAINT` (user dissatisfaction), `SUGGESTION` (improvement idea), `OTHER`
- `content`: Include what the user said or intended, what actually happened, and why it is a problem or praise
