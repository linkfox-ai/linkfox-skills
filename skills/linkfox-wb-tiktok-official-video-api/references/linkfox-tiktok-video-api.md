# TikTok 可购物视频 API

## MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- 本 reference 所有可调用操作的精确 `toolName`：`tiktokVideo/developerProxy`
- 原代理请求体直接作为 `arguments`：`openId`、`path`、`method`、可选 `region`/`queryString`/`contentType`/`body`。不传 headers 或任何 token。

先检查 MCP schema/`isError`；再读取代理包络，`body` 为 JSON 字符串时只解析一次，最后检查 TikTok `code`/`message`。相同 `toolName + arguments` 不重复调用；失败、空响应或结果不理想不自动重试，不作 HTTP fallback。

### 代理响应包络

| 响应字段路径 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | 上游 HTTP 状态码 |
| contentType | string | 响应 Content-Type |
| body | string | TikTok API 原始响应正文（JSON 字符串） |

### 通用白名单代理

精确 `toolName`：`tiktokVideo/developerProxy`。已有具名操作优先；只有用户明确要求调用未登记 Creator API 且 path 已知时使用。

| `arguments` 字段 | 必填 | 类型 | 说明 |
|---|---|---|---|
| openId | 是 | string | 已授权 creator open_id；不得替换为 token |
| path | 是 | string | 不带前导 `/` 的相对路径；只允许 `affiliate_creator`、`video`、`creator` 前缀 |
| method | 是 | string | `GET` / `POST` / `PUT` / `DELETE` |
| region | 否 | string | `global`（默认）或 `us` |
| queryString | 否 | string | GET 查询串，不带 `?` |
| contentType | 否 | string | 请求正文类型；JSON 请求用 `application/json` |
| body | 否 | string | POST/PUT 的上游原始正文字符串 |

不得向未知 path 试探，不得使用绝对 URL、`..` 或重复斜杠。

## 1. 达人档案

上游 `GET affiliate_creator/202508/profiles`；精确 `toolName`：`tiktokVideo/developerProxy`。无业务 Query/Path 参数，仅传已授权 `openId`。

```json
{"toolName":"tiktokVideo/developerProxy","arguments":{"openId":"<creator_open_id>","path":"affiliate_creator/202508/profiles","method":"GET","region":"global"}}
```

| TikTok body 响应字段路径 | 类型 | 说明 |
|---|---|---|
| code | int | 业务状态码（成功/失败） |
| message | string | 业务消息；失败时说明原因 |
| request_id | string | 请求日志 ID |
| data | object | 达人档案信息；内部字段来源未说明 |

## 2. 店铺商品

上游 `GET affiliate_creator/202509/shop_products`；精确 `toolName`：`tiktokVideo/developerProxy`。

| 参数 | 必填 | 类型 | 默认/范围 | 说明 |
|---|---|---|---|---|
| openId | 是 | string | 来源未说明 | 已授权 creator open_id |
| title_keyword | 否 | string | 来源未说明 | 标题关键词 |
| sort_field | 否 | string | `PRODUCT_ID` | `PRODUCT_ID` / `PRICE` / `SALE` |
| sort_order | 否 | string | `DESC` | `DESC` / `ASC` |
| page_size | 是 | int32 | 1~20，推荐 20 | 每页返回数 |
| page_token | 否 | string | 来源未说明 | 上一页游标；首页不传 |

```json
{"toolName":"tiktokVideo/developerProxy","arguments":{"openId":"<creator_open_id>","path":"affiliate_creator/202509/shop_products","method":"GET","region":"global","queryString":"title_keyword=apple&sort_field=PRICE&sort_order=DESC&page_size=20"}}
```

| TikTok body 响应字段路径 | 类型 | 说明 |
|---|---|---|
| code | int | 业务状态码（成功/失败） |
| message | string | 业务消息；失败时说明原因 |
| request_id | string | 请求日志 ID |
| data | object | 商品检索结果（商品列表、`next_page_token` 等）；内部字段来源未说明 |

## 3. 橱窗/直播袋商品

上游 `GET affiliate_creator/202405/showcases/products`；精确 `toolName`：`tiktokVideo/developerProxy`。

| 参数 | 必填 | 类型 | 默认/范围 | 说明 |
|---|---|---|---|---|
| openId | 是 | string | 来源未说明 | 已授权 creator open_id |
| page_size | 是 | int | 1~20 | 每页返回数 |
| page_token | 否 | string | 来源未说明 | 上一页游标 |
| origin | 是 | string | `SHOWCASE` | `SHOWCASE` 或 `LIVE` |

```json
{"toolName":"tiktokVideo/developerProxy","arguments":{"openId":"<creator_open_id>","path":"affiliate_creator/202405/showcases/products","method":"GET","region":"global","queryString":"page_size=20&origin=SHOWCASE"}}
```

| TikTok body 响应字段路径 | 类型 | 说明 |
|---|---|---|
| code | int | 业务状态码（成功/失败） |
| message | string | 业务消息；失败时说明原因 |
| request_id | string | 请求日志 ID |
| data | object | 橱窗/直播袋商品列表与分页信息；内部字段来源未说明 |

## 4. 小文件上传（当前阻塞）

上游 `POST affiliate_creator/202505/videos/video_files` 为 `multipart/form-data`，字段 `data` 是 binary。精确代理 endpoint 映射仍为 `tiktokVideo/developerProxy`，但 `proxy_call` 的 JSON `arguments` 无法承载该 multipart 文件，因此禁止调用或声称上传成功。

| 文件约束 | 说明 |
|---|---|
| 格式 | MP4、MOV、MKV、WMV、WEBM、AVI、3GP、FLV、MPEG |
| 最大大小 | 100 MB；>10MB 使用大文件分片方案 |
| 宽高比 | 9:16 ~ 16:9 |
| 推荐 | 分辨率 ≥720p，时长 >30秒 |

| 预期 TikTok 响应字段路径 | 类型 | 说明 |
|---|---|---|
| code | int32 | 业务状态码（0=成功） |
| message | string | 业务消息 |
| request_id | string | 请求日志 ID |
| data | object | 返回信息 |
| data.video_file | object | 视频文件信息 |
| data.video_file.id | string | 已上传视频文件 id，后续作为 `file_id` |
| data.video_file.md5 | string | 上传文件的 MD5 校验值 |

## 5. 大文件上传

见 `linkfox-tiktok-video-large-file-upload.md`。初始化和绑定均映射到 `tiktokVideo/developerProxy`，但 `open/` 路径当前未放行；分片 PUT 是对返回的文件网关 URL 的本地操作。

## 6. 发布可购物视频

上游 `POST affiliate_creator/202607/videos`；精确 `toolName`：`tiktokVideo/developerProxy`。这是写操作，须确认参数后调用。

| Body 字段路径 | 必填 | 类型 | 说明 |
|---|---|---|---|
| video_info | 是 | object | 视频信息 |
| video_info.file_id | 是 | string | 上传所得文件 id |
| video_info.title | 是 | string | 最长 4000 UTF-16 runes |
| video_info.cover_uri | 否 | string | 自定义封面 URI；与时间戳同时传时优先 |
| video_info.cover_timestamp_ms | 否 | int32 | 视频帧毫秒；不传封面参数则用首帧 |
| video_info.music_id | 否 | string | 背景音乐 ID |
| video_info.is_ai_generated | 否 | bool | AI 生成内容标识 |
| product_link_info | 是 | object | 商品关联信息 |
| product_link_info.product_id | 是 | string | 关联商品 id |
| product_link_info.title | 是 | string | 锚点标题，建议 <30 字符 |

```json
{"toolName":"tiktokVideo/developerProxy","arguments":{"openId":"<creator_open_id>","path":"affiliate_creator/202607/videos","method":"POST","contentType":"application/json","body":"{\"video_info\":{\"file_id\":\"<file_id>\",\"title\":\"Demo\",\"is_ai_generated\":false},\"product_link_info\":{\"product_id\":\"<product_id>\",\"title\":\"Anchor\"}}"}}
```

| TikTok body 响应字段路径 | 类型 | 说明 |
|---|---|---|
| code | int32 | 业务状态码（0=成功） |
| message | string | 业务消息 |
| request_id | string | 请求日志 ID |
| data | object | 返回信息 |
| data.video | object | 已发布视频信息 |
| data.video.id | string | 视频 id，用于查询发布状态 |
| data.quota | string | 发帖配额，如 `3/day`；成功时返回，失败时可能写入错误信息，无限制时省略 |

## 7. 查询发布状态

上游动态路径 `GET affiliate_creator/202509/videos/{video_id}/status`；精确 `toolName`：`tiktokVideo/developerProxy`。`video_id` 必填 string，来自发布响应。

```json
{"toolName":"tiktokVideo/developerProxy","arguments":{"openId":"<creator_open_id>","path":"affiliate_creator/202509/videos/<video_id>/status","method":"GET"}}
```

| TikTok body 响应字段路径 | 类型 | 说明 |
|---|---|---|
| code | int32 | 业务状态码（0=成功） |
| message | string | 业务消息 |
| request_id | string | 请求日志 ID |
| data | object | 返回信息 |
| data.video | object | 视频信息 |
| data.video.id | string | 视频 id |
| data.video.post_status | string | `SUCCESS` / `FAIL` / `PROCESSING` |
| data.video.post_time | int64 | 发布成功时间（秒）；仅 `SUCCESS` 返回 |

## 8. 内容预检

上游 `POST affiliate_creator/202511/videos/precheck_task`；精确 `toolName`：`tiktokVideo/developerProxy`。这是写操作。

| Body 字段路径 | 必填 | 类型 | 说明 |
|---|---|---|---|
| video_info | 是 | object | 视频信息 |
| video_info.file_id | 是 | string | 上传接口所得文件 id |
| product_link_info | 是 | object | 商品关联信息 |
| product_link_info.product_id | 是 | string | 关联商品 id |
| product_link_info.title | 是 | string | 锚点标题，建议 <30 字符 |

```json
{"toolName":"tiktokVideo/developerProxy","arguments":{"openId":"<creator_open_id>","path":"affiliate_creator/202511/videos/precheck_task","method":"POST","contentType":"application/json","body":"{\"video_info\":{\"file_id\":\"<file_id>\"},\"product_link_info\":{\"product_id\":\"<product_id>\",\"title\":\"Anchor\"}}"}}
```

| TikTok body 响应字段路径 | 类型 | 说明 |
|---|---|---|
| code | int32 | 业务状态码（0=成功） |
| message | string | 业务消息 |
| request_id | string | 请求日志 ID |
| data | object | 返回信息 |
| data.precheck | object | 视频内容预检任务结果 |
| data.precheck.task_id | string | 异步预检任务 id |

## 9. 查询预检结果

上游动态路径 `GET affiliate_creator/202511/videos/precheck_tasks/{task_id}`；精确 `toolName`：`tiktokVideo/developerProxy`。`task_id` 必填 string。

```json
{"toolName":"tiktokVideo/developerProxy","arguments":{"openId":"<creator_open_id>","path":"affiliate_creator/202511/videos/precheck_tasks/<task_id>","method":"GET"}}
```

| TikTok body 响应字段路径 | 类型 | 说明 |
|---|---|---|
| code | int32 | 业务状态码（0=成功） |
| message | string | 业务消息 |
| request_id | string | 请求日志 ID |
| data | object | 返回信息 |
| data.precheck_task | object | 视频预检任务 |
| data.precheck_task.id | string | 预检任务 id |
| data.precheck_task.result | string | `SUCCESS` / `FAIL` / `PROCESSING` |
| data.precheck_task.issues | array<object> | 失败时的违规明细 |
| data.precheck_task.issues[] | object | 单条违规明细（来源示例确认） |
| data.precheck_task.issues[].risk | string | 违规风险点，如 `Pirated Content` |
| data.precheck_task.issues[].suggestions | string | 解决建议 |

## 错误、轮询与成本

`1002` 表示参数/登录上下文/白名单配置错误；`1003` 表示上游服务或网络异常；`1005` 表示 path 不在 `affiliate_creator`/`video`/`creator` 白名单。业务错误按 TikTok `code`/`message` 原样报告。每次列表翻页、预检、发布和状态查询都可能计费；不自动翻页、轮询或重试。`PROCESSING` 时保存 ID 并报告，下一次查询需用户明确要求。

## Feedback API（不迁移到 MCP）

用户明确反馈满意、不满或描述错误时，可独立 `POST https://skill-api.linkfox.com/api/v1/public/feedback`。它不是 tool-gateway endpoint，不使用 `proxy_call`；字段为 `skillName`（`linkfox-tiktok-video`）、`sentiment`（`POSITIVE`/`NEGATIVE`）、`category`（`BUG`/`FEATURE_REQUEST`/`OTHER`）、`content`。反馈失败不得影响业务结果，也不得自动重试。

## 响应字段来源

全部表仅据 `skills/linkfox-tiktok-video/references/api.md` 的 `developerProxy 出参`、各节 `上游响应` 表及紧邻 JSON 示例核对。达人档案和两类商品的 `data` 内部字段在来源中未说明；其余父对象/数组及所有已列嵌套字段均已展开。
